@echo off
chcp 65001 >nul
echo ========================================================
echo   СБОРКА АВТОНОМНОГО ИСПОЛНЯЕМОГО ФАЙЛА (EXE)
echo   Whisper Voice Dictation AI for Windows
echo ========================================================
echo.

echo Установка PyInstaller...
pip install pyinstaller

echo.
echo Сборка WhisperVoiceDictation.exe...
pyinstaller --noconsole --onefile --icon=whisper_icon.ico --name=WhisperVoiceDictation main.py

echo.
echo ========================================================
echo   СБОРКА УСПЕШНО ЗАВЕРШЕНА!
echo   Исполняемый файл находится в папке: dist\WhisperVoiceDictation.exe
echo ========================================================
pause
