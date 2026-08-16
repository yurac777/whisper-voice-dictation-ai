@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PY_EXE=pythonw.exe"
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    set "PY_EXE=%~dp0.venv\Scripts\pythonw.exe"
) else if exist "%USERPROFILE%\.whisper_env\Scripts\pythonw.exe" (
    set "PY_EXE=%USERPROFILE%\.whisper_env\Scripts\pythonw.exe"
)

start "" "%PY_EXE%" "%~dp0main.py"
