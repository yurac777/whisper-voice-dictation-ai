@echo off
chcp 65001 >nul
title Whisper Voice Dictation AI
start "" "C:\Users\Lenovo\.whisper_env\Scripts\pythonw.exe" "%~dp0main.py"
