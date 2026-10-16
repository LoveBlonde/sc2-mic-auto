import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('watcher', Path(__file__).resolve().parents[1] / 'sc2_mic_auto.py')
watcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watcher)
DEVICE = '{0.0.1.00000000}.{00000000-0000-0000-0000-000000000001}'


class WatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        for name, value in [('STATE', base / 'state.json'), ('CONFIG', base / 'config.json'), ('LOG', base / 'log.txt'), ('DEVICE', DEVICE)]:
            p = patch.object(watcher, name, value)
            p.start()
            self.addCleanup(p.stop)
        self.current = True
        def set_enabled(value):
            self.current = value
        self.setter = patch.object(watcher, 'set_enabled', side_effect=set_enabled).start()
        patch.object(watcher, 'enabled', side_effect=lambda: self.current).start()
        self.addCleanup(patch.stopall)

    def test_game_start_exit_restores_enabled_microphone(self):
        watcher.update(True)
        self.assertFalse(self.current)
        watcher.update(False)
        self.assertTrue(self.current)
        self.assertFalse(watcher.STATE.exists())

    def test_initially_disabled_microphone_stays_disabled(self):
        self.current = False
        watcher.update(True)
        watcher.update(False)
        self.assertFalse(self.current)

    def test_repeated_polls_do_not_overwrite_original_state(self):
        watcher.update(True)
        watcher.update(True)
        self.assertTrue(json.loads(watcher.STATE.read_text())['enabled'])
        self.setter.assert_called_once_with(False)
        watcher.update(False)
        self.assertTrue(self.current)

    def test_saved_state_survives_restart_and_recovers(self):
        watcher.save_state(True)
        self.current = False
        watcher.update(False)
        self.assertTrue(self.current)

    def test_restore_failure_preserves_recovery_state(self):
        watcher.save_state(True)
        self.setter.side_effect = OSError('headset disconnected')
        with self.assertRaises(OSError):
            watcher.restore()
        self.assertTrue(watcher.STATE.exists())

    def test_changed_device_does_not_restore_wrong_microphone(self):
        watcher.save_state(True)
        with patch.object(watcher, 'DEVICE', 'different'):
            with self.assertRaises(ValueError):
                watcher.restore()
        self.setter.assert_not_called()

    def test_config_rejects_playback_endpoint(self):
        watcher.CONFIG.write_text(json.dumps({'device_id': DEVICE.replace('0.0.1.', '0.0.0.')}))
        with self.assertRaises(ValueError):
            watcher.load_config()

    def test_idle_does_not_change_device(self):
        watcher.update(False)
        self.setter.assert_not_called()


if __name__ == '__main__':
    unittest.main()
