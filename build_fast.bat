@echo off
echo Building WhisperVoiceDictation Fast Mode...
taskkill /F /IM WhisperVoiceDictation.exe /IM pythonw.exe /IM python.exe >nul 2>&1
"C:\Users\Lenovo\.whisper_env\Scripts\pyinstaller.exe" --noconsole --onedir --noconfirm --icon=whisper_icon.ico --name=WhisperVoiceDictation --collect-all ctranslate2 --collect-all faster_whisper --collect-all sounddevice --collect-all cffi --collect-all onnxruntime main.py
echo FAST BUILD COMPLETE!
