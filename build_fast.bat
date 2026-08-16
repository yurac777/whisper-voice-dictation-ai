@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Building WhisperVoiceDictation Fast Mode...
taskkill /F /IM WhisperVoiceDictation.exe /IM pythonw.exe /IM python.exe >nul 2>&1

set "PYI_EXE=pyinstaller"
if exist "%~dp0.venv\Scripts\pyinstaller.exe" (
    set "PYI_EXE=%~dp0.venv\Scripts\pyinstaller.exe"
) else if exist "%USERPROFILE%\.whisper_env\Scripts\pyinstaller.exe" (
    set "PYI_EXE=%USERPROFILE%\.whisper_env\Scripts\pyinstaller.exe"
)

"%PYI_EXE%" --noconsole --onedir --noconfirm --icon=whisper_icon.ico --name=WhisperVoiceDictation --collect-all ctranslate2 --collect-all faster_whisper --collect-all sounddevice --collect-all cffi --collect-all onnxruntime main.py
echo FAST BUILD COMPLETE!
