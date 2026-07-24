@echo off
chcp 65001 >nul
taskkill /F /FI "IMAGENAME eq pythonw.exe" /FI "WINDOWTITLE eq *main.py*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *main.py*" >nul 2>&1
cd /d "C:\Users\Lenovo\Desktop\projects\whisper_dictation"
start "" "C:\Users\Lenovo\.whisper_env\Scripts\pythonw.exe" "C:\Users\Lenovo\Desktop\projects\whisper_dictation\main.py"
