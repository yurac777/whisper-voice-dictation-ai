# 🛡️ INFRASTRUCTURE & SERVICE PASSPORT

## Service Registry

| Service / Component | Version / Type | Config Path | Launch Command | Status |
|---|---|---|---|---|
| **Whisper Voice AI Core** | PyQt6 + Faster-Whisper (Turbo/v3) | `config.json` | `run.bat` / `pythonw.exe main.py` | 🟢 Active |
| **Compiled Production Executable** | PyInstaller (`--onedir` release) | `dist/WhisperVoiceDictation/` | `dist/WhisperVoiceDictation/WhisperVoiceDictation.exe` | 🟢 Ready |
| **System Tray Integration** | QSystemTrayIcon | N/A | Automated on app startup | 🟢 Active |

## Key Features & Control Specs

1. **Minimize to Tray Button (`➖`)**: Collapses floating pill bar widget into system tray notification area (`self.hide()`).
2. **Tray Activation**: Single/double-clicking the system tray icon instantly toggles/restores window visibility.
3. **Minimized Mode Security Guards**: When window is hidden (`not self.isVisible()`), mouse clicks (middle click) and keyboard hotkeys (`Right-Alt`, `Right-Ctrl`, `F9`, `F10`, `ESC`) are ignored to prevent accidental recordings.
4. **Auto-Cancel on Hide**: Minimizing while recording automatically cancels active dictation session and releases audio devices.

## Environment & Dependencies

- **Python Virtual Environment**: `C:\Users\Lenovo\.whisper_env`
- **Audio Recorder Backend**: `sounddevice` + `numpy` (WAV buffer)
- **Speech-to-Text Engine**: `faster_whisper` (`ctranslate2`)
