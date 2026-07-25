@echo off
chcp 65001 > NUL
echo ===================================================
echo   Сборка портативного WhisperVoiceDictation.exe
echo ===================================================

C:\Users\Lenovo\.whisper_env\Scripts\python.exe -m pip install pyinstaller

echo.
echo Сборка WhisperVoiceDictation.exe в виртуальном окружении...
C:\Users\Lenovo\.whisper_env\Scripts\pyinstaller.exe --noconsole --onefile --icon=whisper_icon.ico --name=WhisperVoiceDictation --collect-all ctranslate2 --collect-all faster_whisper --collect-all sounddevice --collect-all cffi main.py

echo.
echo ===================================================
echo   СБОРКА УСПЕШНО ЗАВЕРШЕНА!
echo   Файл находится в: dist\WhisperVoiceDictation.exe
echo ===================================================
pause
