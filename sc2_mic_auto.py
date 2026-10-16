import ctypes as c
from ctypes import wintypes as w
import json
from pathlib import Path
import time

BASE = Path(__file__).resolve().parent
STATE = BASE / 'sc2_mic_state.json'
STOP = BASE / 'sc2_mic_stop'
LOG = BASE / 'sc2_mic.log'
CONFIG = BASE / 'config.json'
DEVICE = None


def load_config():
    global DEVICE
    config = json.loads(CONFIG.read_text(encoding='utf-8-sig'))
    DEVICE = config['device_id']
    import re
    if not re.fullmatch(r'\{0\.0\.1\.00000000\}\.\{[0-9a-fA-F-]{36}\}', DEVICE):
        raise ValueError('Configuration must specify an exact recording endpoint ID')
    return config


def save_state(original):
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps({'enabled': original, 'device_id': DEVICE}), encoding='utf-8')
    temp.replace(STATE)

class GUID(c.Structure):
    _fields_ = [('a', w.DWORD), ('b', w.WORD), ('d', w.WORD), ('e', c.c_ubyte * 8)]
    @classmethod
    def parse(cls, value):
        import uuid
        return cls.from_buffer_copy(uuid.UUID(value).bytes_le)

ole = c.OleDLL('ole32')
kernel = c.WinDLL('kernel32', use_last_error=True)
kernel.CreateMutexW.argtypes = [c.c_void_p, w.BOOL, w.LPCWSTR]
kernel.CreateMutexW.restype = w.HANDLE
kernel.CloseHandle.argtypes = [w.HANDLE]

def log(message):
    with LOG.open('a', encoding='utf-8') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n')

def enabled():
    enumerator = c.c_void_p()
    cls = GUID.parse('bcde0395-e52f-467c-8e3d-c4579291692e')
    iid = GUID.parse('a95664d2-9614-4f35-a746-de8db63617e6')
    ole.CoCreateInstance(c.byref(cls), None, 1, c.byref(iid), c.byref(enumerator))
    table = c.cast(enumerator, c.POINTER(c.POINTER(c.c_void_p))).contents
    device = c.c_void_p()
    try:
        hr = c.WINFUNCTYPE(c.c_long, c.c_void_p, w.LPCWSTR, c.POINTER(c.c_void_p))(table[5])(enumerator, DEVICE, c.byref(device))
        if hr < 0:
            raise OSError('Microphone is unavailable')
        dt = c.cast(device, c.POINTER(c.POINTER(c.c_void_p))).contents
        state = w.DWORD()
        c.WINFUNCTYPE(c.c_long, c.c_void_p, c.POINTER(w.DWORD))(dt[6])(device, c.byref(state))
        c.WINFUNCTYPE(w.ULONG, c.c_void_p)(dt[2])(device)
        return bool(state.value & 1)
    finally:
        c.WINFUNCTYPE(w.ULONG, c.c_void_p)(table[2])(enumerator)

def set_enabled(value):
    import subprocess
    subprocess.run([str(BASE / 'audio-tools' / 'SoundVolumeView.exe'),
                    '/Enable' if value else '/Disable', DEVICE],
                   check=True, creationflags=0x08000000, timeout=15)
    for _ in range(30):
        if enabled() == value:
            return
        time.sleep(0.1)
    raise OSError('Endpoint state verification failed')

class PROCESSENTRY32W(c.Structure):
    _fields_ = [('dwSize', w.DWORD), ('cntUsage', w.DWORD), ('th32ProcessID', w.DWORD),
                ('th32DefaultHeapID', c.c_size_t), ('th32ModuleID', w.DWORD),
                ('cntThreads', w.DWORD), ('th32ParentProcessID', w.DWORD),
                ('pcPriClassBase', w.LONG), ('dwFlags', w.DWORD), ('szExeFile', w.WCHAR * 260)]

kernel.CreateToolhelp32Snapshot.argtypes = [w.DWORD, w.DWORD]
kernel.CreateToolhelp32Snapshot.restype = w.HANDLE
kernel.Process32FirstW.argtypes = [w.HANDLE, c.POINTER(PROCESSENTRY32W)]
kernel.Process32NextW.argtypes = [w.HANDLE, c.POINTER(PROCESSENTRY32W)]

def playing():
    handle = kernel.CreateToolhelp32Snapshot(2, 0)
    if handle == c.c_void_p(-1).value:
        raise c.WinError(c.get_last_error())
    entry = PROCESSENTRY32W()
    entry.dwSize = c.sizeof(entry)
    try:
        ok = kernel.Process32FirstW(handle, c.byref(entry))
        while ok:
            if entry.szExeFile.lower() in ('sc2.exe', 'sc2_x64.exe'):
                return True
            ok = kernel.Process32NextW(handle, c.byref(entry))
        return False
    finally:
        kernel.CloseHandle(handle)

def restore():
    if STATE.exists():
        saved = json.loads(STATE.read_text(encoding='utf-8'))
        if saved['device_id'] != DEVICE:
            raise ValueError('Saved device differs from config; restore the old config first')
        original = saved['enabled']
        set_enabled(original)
        STATE.unlink()
        log('Restored microphone to original state')

def update(is_playing):
    if is_playing:
        if not STATE.exists():
            save_state(enabled())
        if enabled():
            set_enabled(False)
            log('SC2 detected: microphone disabled')
    else:
        restore()


def main():
    mutex = kernel.CreateMutexW(None, False, 'Local\\SC2MicAuto')
    if c.get_last_error() == 183:
        return
    ole.CoInitialize(None)
    try:
        load_config()
        log('Watcher started')
        while not STOP.exists():
            try:
                update(playing())
            except Exception as exc:
                log(str(exc))
                time.sleep(4)
            time.sleep(0.5)
    finally:
        restore()
        STOP.unlink(missing_ok=True)
        ole.CoUninitialize()
        kernel.CloseHandle(mutex)
        log('Watcher stopped')

if __name__ == '__main__':
    import sys
    try:
        if '--stop' in sys.argv:
            STOP.touch()
        elif '--restore' in sys.argv or '--check' in sys.argv:
            ole.CoInitialize(None)
            try:
                load_config()
                if '--restore' in sys.argv:
                    restore()
                print('Microphone enabled:', enabled())
            finally:
                ole.CoUninitialize()
        else:
            main()
    except Exception as exc:
        log('ERROR: ' + str(exc))
        raise

