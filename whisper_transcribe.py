# -*- coding: utf-8 -*-
import os, sys, time, wave
from faster_whisper import WhisperModel

VENV_PYTHON = r"C:\Users\Lenovo\.whisper_env\Scripts\python.exe"

def transcribe_file(file_path, model_size="small", language=None):
    if not os.path.exists(file_path):
        print(f"Error: File not found -> {file_path}")
        return
    
    print(f"Loading Whisper model '{model_size}' optimized for AMD Ryzen AI...")
    t0 = time.time()
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=8)
    print(f"Model loaded in {time.time() - t0:.2f}s!")

    print(f"Transcribing '{file_path}'...")
    t1 = time.time()
    segments, info = model.transcribe(file_path, beam_size=5, language=language)
    
    print(f"Detected language: {info.language} (probability {info.language_probability:.2f})")
    
    full_text = []
    for segment in segments:
        line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
        print(line)
        full_text.append(line)
    
    out_txt = os.path.splitext(file_path)[0] + "_transcription.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(full_text))
    
    print(f"\nSaved transcription to: {out_txt}")
    print(f"Done in {time.time() - t1:.2f}s!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        lang = sys.argv[2] if len(sys.argv) > 2 else None
        transcribe_file(target, language=lang)
    else:
        print("=== WHISPER AUDIO/VIDEO TRANSCRIBER (AMD RYZEN AI OPTIMIZED) ===")
        print("Usage: python whisper_transcribe.py <path_to_audio_or_video> [language_code]")
        print("Example: python whisper_transcribe.py audio.mp3 ru")
