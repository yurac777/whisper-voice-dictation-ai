# 🛡️ INFRASTRUCTURE & SERVICE PASSPORT

## Service Registry

| Service / Component | Version / Type | Config Path | Launch Command | Status |
|---|---|---|---|---|
| **Whisper Voice AI Core** | PyQt6 + Faster-Whisper (Turbo/v3) | `config.json` | `run.bat` / `pythonw.exe main.py` | 🟢 Active |
| **Compiled Production Executable** | PyInstaller (`--onedir` / `--onefile`) | `dist/WhisperVoiceDictation/` | `dist/WhisperVoiceDictation/WhisperVoiceDictation.exe` | 🟢 Ready |
| **System Tray Integration** | QSystemTrayIcon | N/A | Automated on app startup | 🟢 Active |
| **GitHub Actions CI/CD** | Automated Multi-Platform Release | `.github/workflows/` | Triggered on git tag `v*` | 🟢 Configured |

## Key Features & Control Specs

1. **Minimize to Tray Button (`➖`)**: Collapses floating pill bar widget into system tray notification area (`self.hide()`).
2. **Tray Activation**: Single/double-clicking the system tray icon instantly toggles/restores window visibility.
3. **Minimized Mode Security Guards**: When window is hidden (`not self.isVisible()`), mouse clicks (middle click) and keyboard hotkeys (`Right-Alt`, `Right-Ctrl`, `F9`, `F10`, `ESC`, `Pause`) are ignored to prevent accidental recordings.
4. **Auto-Cancel on Hide**: Minimizing while recording automatically cancels active dictation session and releases audio devices.
5. **Fault-Tolerant GPU Fallback**: If CUDA initialization fails, automatically falls back to multi-threaded CPU int8 quantization without crashing.
6. **Enterprise CLI Flags**: Supports `--minimized`, `--model <size>`, `--lang <code>`, `--version`, `--help`.

## Environment & Dependencies

- **Python Virtual Environment**: `C:\Users\Lenovo\.whisper_env`
- **Audio Recorder Backend**: `sounddevice` + `numpy` (Direct RAM buffer)
- **Speech-to-Text Engine**: `faster_whisper` (`ctranslate2` int8/float16)
- **GUI Framework**: `PyQt6`
