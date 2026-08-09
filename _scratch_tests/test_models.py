# -*- coding: utf-8 -*-
"""
Whisper Model Benchmark & Testing Utility
Use this script to test saved audio dictations (.wav) across different Whisper models
(small, medium, turbo, large-v3) and check accuracy & performance.
"""

import sys
import os
import time
import glob
import json

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

from main import get_whisper_model, clean_hallucinated_subtitles, INITIAL_PROMPT

def benchmark_audio_file(wav_path, models=None):
    if models is None:
        models = ["small", "medium", "turbo", "large-v3"]
        
    if not os.path.exists(wav_path):
        print(f"❌ Error: File '{wav_path}' does not exist.")
        return

    print(f"\n==================================================")
    print(f"🎙️ BENCHMARKING AUDIO FILE: {os.path.basename(wav_path)}")
    print(f"==================================================")

    results = {}

    for model_name in models:
        print(f"\n⏳ Loading & transcribing with model '{model_name}'...")
        start_time = time.time()
        try:
            model = get_whisper_model(model_name)
            segments, info = model.transcribe(
                wav_path,
                beam_size=1,
                best_of=1,
                temperature=0.0,
                without_timestamps=True,
                suppress_blank=True,
                condition_on_previous_text=False,
                language="ru",
                initial_prompt=INITIAL_PROMPT,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=250,
                    threshold=0.5,
                    min_speech_duration_ms=250
                )
            )
            text_parts = [segment.text.strip() for segment in segments if segment.text]
            raw_text = " ".join(text_parts).strip()
            clean_text = clean_hallucinated_subtitles(raw_text)
            elapsed = time.time() - start_time
            
            results[model_name] = {
                "elapsed_sec": round(elapsed, 3),
                "raw_text": raw_text,
                "clean_text": clean_text,
                "language_probability": round(info.language_probability, 3)
            }
            print(f"✅ Model '{model_name}' finished in {elapsed:.3f}s")
            print(f"   Result: \"{clean_text}\"")
        except Exception as e:
            print(f"❌ Model '{model_name}' failed: {e}")
            results[model_name] = {"error": str(e)}

    print(f"\n--------------------------------------------------")
    print(f"📊 BENCHMARK SUMMARY FOR: {os.path.basename(wav_path)}")
    print(f"--------------------------------------------------")
    for m, res in results.items():
        if "error" in res:
            print(f"[{m.upper()}]: ERROR -> {res['error']}")
        else:
            print(f"[{m.upper()}]: {res['elapsed_sec']}s | Text: \"{res['clean_text']}\"")
    print(f"==================================================\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            benchmark_audio_file(target)
        elif os.path.isdir(target):
            wav_files = glob.glob(os.path.join(target, "*.wav"))
            for wf in wav_files:
                benchmark_audio_file(wf)
    else:
        # Check logs directory
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        wav_files = sorted(glob.glob(os.path.join(logs_dir, "**", "*.wav"), recursive=True), reverse=True)
        if not wav_files:
            wav_files = sorted(glob.glob(os.path.join(logs_dir, "*.wav")), reverse=True)
        if wav_files:
            print(f"Found {len(wav_files)} recorded dictation logs in '{logs_dir}'. Testing the latest recording: {wav_files[0]}")
            benchmark_audio_file(wav_files[0], models=["small", "turbo"])
        else:
            print(f"No WAV files found in '{logs_dir}'.")
            print("Usage: python test_models.py <path_to_audio.wav>")
