# SC2 Mic Auto — 스타크래프트 2 무음 문제 자동 우회

**스타2를 켜면 소리가 사라지고, Windows에서 헤드셋 녹음 장치를 비활성화하면 해결되나요?** 이 도구는 그 작업을 자동으로 합니다.

`스타2 실행 → 선택한 마이크 비활성화 → 스타2 종료 → 원래 마이크 상태 복원`

Windows 로그인 시 백그라운드에서 시작하므로 평소처럼 Battle.net에서 게임을 실행하면 됩니다. 특정 헤드셋에 고정되어 있지 않고 설치 중 자신의 녹음 장치를 선택합니다.

## 설치

1. Windows 10/11 **x64**, [Python 3.10 이상](https://www.python.org/downloads/windows/)이 필요합니다. Python 설치 시 **Add Python to PATH**를 체크하세요.
2. 이 저장소의 **Code → Download ZIP**으로 내려받고, 계속 보관할 폴더에 압축을 풉니다. ZIP 안에서 직접 실행하지 마세요.
3. **`install.cmd`를 더블클릭**합니다. 관리자 권한은 보통 필요하지 않습니다.
4. 목록에서 **비활성화했을 때 스타2 소리가 정상화되는 헤드셋 마이크**의 번호를 입력합니다.
5. 완료 메시지가 나오면 창을 닫고 스타2를 실행합니다. 다음 로그인부터도 자동으로 작동합니다.

설치 시 NirSoft 공식 사이트에서 SoundVolumeView를 내려받습니다. 다운로드의 SHA-256을 검증하고, 본 프로그램과 별도 라이선스의 freeware로 사용합니다. Python 패키지 설치는 필요 없습니다.

## 알아둘 점

- 게임 중에는 선택한 마이크가 **Windows 전체에서 비활성화**되므로 디스코드 등에서도 사용할 수 없습니다. 다른 마이크를 쓰면 됩니다.
- 단순 음소거가 아니라 Windows 소리 제어판의 녹음 장치 비활성화에 해당하는 작업입니다.
- `SC2.exe`, `SC2_x64.exe`를 0.5초마다 확인합니다. 실제 전환에는 장치 처리 시간이 조금 더 걸릴 수 있습니다.
- 원래 꺼져 있던 마이크는 종료 후에도 꺼진 상태로 유지합니다.
- 저장한 상태는 다음 실행 때도 복원을 시도합니다. 강제 종료·전원 차단·헤드셋 분리 시에는 즉시 복원할 수 없으므로 아래 복구 방법을 참고하세요.
- 설치 폴더를 이동하거나 삭제하면 자동 실행이 깨집니다. 먼저 해제한 뒤 새 위치에서 설치하세요.
- 모든 무음 문제를 해결하는 도구는 아닙니다. **마이크 비활성화로 해결되는 증상**을 위한 우회 도구입니다. 스타2나 드라이버 파일은 수정하지 않습니다.

## 해제 및 복구

**`uninstall.cmd`를 더블클릭**하면 자동 시작을 제거하고 실행 중인 감시 프로그램에 종료를 요청합니다. 원래 마이크 상태가 복원된 뒤에만 성공 메시지가 나옵니다. 그 뒤 폴더를 삭제할 수 있습니다.

프로그램이 비정상 종료되었거나 헤드셋이 분리되어 복원에 실패했다면:

1. 스타2를 종료하고 헤드셋을 다시 연결합니다.
2. 설치 폴더의 `sc2_mic.log`를 확인합니다. 정상 감시 프로그램이 남아 있다면 먼저 `uninstall.cmd`로 종료하세요.
3. 감시 프로그램이 실행 중이지 않은 것을 확인한 뒤 설치 폴더에서 `python sc2_mic_auto.py --restore`를 실행합니다. Python Launcher만 있다면 `py -3 sc2_mic_auto.py --restore`를 사용합니다.
4. 필요하면 `Win + R → mmsys.cpl → 녹음`에서 해당 마이크를 직접 다시 활성화할 수 있습니다. 자동 시작은 `Win + R → shell:startup`의 **SC2 Mic Auto** 바로가기를 삭제하면 해제됩니다.

다른 마이크로 바꾸려면 정상 해제를 완료하고 `install.cmd`를 다시 실행합니다. 장치 ID나 `config.json`을 임의로 바꾸면 이전 장치의 복원 기록과 맞지 않을 수 있습니다.

**다운로드 해시 오류:** NirSoft의 ZIP이 업데이트되면 설치는 다운로드 파일을 실행하지 않고 중단됩니다. 최신 릴리스/이슈를 확인하세요. 해시 검증을 없애서 우회하지 마세요.

## 검증 범위

최초 개인용 버전은 Sony INZONE Buds의 USB 연결 환경에서 실제 스타크래프트 2 무음 증상 해결을 확인했습니다. 공개 버전은 장치 선택 설정을 추가했고, 원래 상태 보존·반복 감지·재시작 복구·복원 실패·잘못된 장치 선택에 대한 자동 테스트를 포함합니다. 다른 헤드셋과 Windows 버전에서의 결과는 이슈로 알려주세요. 로그나 설정을 공유할 때는 장치 ID와 로컬 경로를 지워주세요.

```powershell
python -m unittest discover -s tests -v
```

## 배경과 라이선스

블리자드는 음성채팅 제거 이후에도 스타2 클라이언트가 마이크 사용으로 표시될 수 있다고 [공식 지원 포럼에서 설명](https://us.forums.blizzard.com/en/sc2/t/cant-disable-microphone-access/27538)했습니다. 이 도구는 엔진 버그를 수정하는 대신 녹음 장치 비활성화 우회를 자동화합니다. INZONE USB 연결의 Game/Chat 장치를 일반 Bluetooth 통화 프로필과 동일하다고 가정하지 않습니다.

이 저장소의 코드는 MIT 라이선스입니다. [SoundVolumeView](https://www.nirsoft.net/utils/sound_volume_view.html)는 Nir Sofer의 별도 freeware이며 이 저장소에 바이너리를 포함하지 않습니다. Blizzard 또는 Sony의 공식 도구가 아닙니다.

## English

Automatically disable a selected Windows recording endpoint while StarCraft II (`SC2.exe` / `SC2_x64.exe`) is running, then restore its previous enabled/disabled state on exit. Intended for the **SC2 has no audio until I disable my headset microphone** issue.

Windows 10/11 x64 and Python 3.10+ are required. Download/extract this repository, keep the folder in a permanent location, double-click **install.cmd**, and choose your headset **microphone**. Setup downloads a SHA-256-verified SoundVolumeView archive from NirSoft and creates a per-user login shortcut. No Python packages are required. Double-click **uninstall.cmd** to stop and remove automatic startup.

The selected microphone is unavailable to **all applications** while SC2 runs, including Discord. Prior state is persisted for restart recovery; abrupt shutdown or disconnection can delay restoration. To recover manually, close SC2, reconnect the headset, ensure the watcher is stopped, then run `python sc2_mic_auto.py --restore`. You can also re-enable the device in Windows Sound Control Panel → Recording. This is a workaround, not a game/driver patch, and is not guaranteed for all hardware. See the Korean sections above for full setup, recovery, and validation details.
