@echo off
chcp 65001 >nul
echo ============================================================
echo   WHISPER AI AUDIO/VIDEO TRANSCRIBER (AMD RYZEN AI 9)
echo ============================================================
echo.

if "%~1"=="" (
    echo Перетащите любой аудио/видео файл (.mp3, .wav, .m4a, .mp4, .mkv) на этот файл .bat
    echo или укажите путь к файлу.
    echo.
    set /p input_file="Введите путь к аудио/видео файлу: "
) else (
    set input_file=%~1
)

if "%input_file%"=="" goto end

"C:\Users\Lenovo\.whisper_env\Scripts\python.exe" "C:\Users\Lenovo\Desktop\projects\podkop\whisper_transcribe.py" "%input_file%" ru

:end
echo.
pause
