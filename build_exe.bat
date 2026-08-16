@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===================================================
echo   Сборка портативного WhisperVoiceDictation.exe
echo ===================================================

set "PY_EXE=python"
set "PYI_EXE=pyinstaller"
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0.venv\Scripts\python.exe"
    set "PYI_EXE=%~dp0.venv\Scripts\pyinstaller.exe"
) else if exist "%USERPROFILE%\.whisper_env\Scripts\python.exe" (
    set "PY_EXE=%USERPROFILE%\.whisper_env\Scripts\python.exe"
    set "PYI_EXE=%USERPROFILE%\.whisper_env\Scripts\pyinstaller.exe"
)

"%PY_EXE%" -m pip install pyinstaller

echo.
echo Сборка WhisperVoiceDictation.exe...
"%PYI_EXE%" --noconsole --onefile --clean --icon=whisper_icon.ico --name=WhisperVoiceDictation --collect-all ctranslate2 --collect-all faster_whisper --collect-all sounddevice --collect-all cffi --collect-all onnxruntime main.py

echo.
echo ===================================================
echo   СБОРКА УСПЕШНО ЗАВЕРШЕНА!
echo   Файл находится в: dist\WhisperVoiceDictation.exe
echo ===================================================
pause
