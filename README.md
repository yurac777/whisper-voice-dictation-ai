# 🎙️ Whisper Voice Dictation AI

<p align="center">
  <img src="https://img.shields.io/github/v/release/yurac777/whisper-voice-dictation-ai?style=for-the-badge&color=74c7ec&logo=github" alt="Release">
  <img src="https://img.shields.io/github/downloads/yurac777/whisper-voice-dictation-ai/total?style=for-the-badge&color=a6e3a1&logo=github" alt="Downloads">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-89b4fa?style=for-the-badge&logo=windows" alt="Platforms">
  <img src="https://img.shields.io/badge/GPU%20Accel-AMD%20DirectML%20%7C%20NVIDIA%20CUDA-fab387?style=for-the-badge&logo=amd" alt="GPU Acceleration">
  <img src="https://img.shields.io/badge/Latency-Sub--300ms-f9e2af?style=for-the-badge&logo=lightning" alt="Latency">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>[ 🇺🇸 English ](README.md) | [ 🇷🇺 Русский ](README_RU.md)</b>
</p>

<p align="center">
  <b>Ultra-fast, 100% offline local AI voice dictation widget for Windows, Linux, and macOS. Powered by OpenAI Whisper Turbo, DirectML GPU hardware acceleration, zero disk I/O latency, and automatic active window focus tracking.</b>
</p>

---

## 🌟 Why Choose Whisper Voice Dictation AI?

| Feature | 🎙️ Whisper Dictation AI | ☁️ Cloud APIs (Yandex/Whisper) | 🪟 Built-in OS Voice Typing |
| :--- | :---: | :---: | :---: |
| **Privacy & Offline** | 🔒 **100% Offline & Private** | ❌ Sends voice data to servers | ❌ Requires cloud connection |
| **Processing Latency** | ⚡ **~0.25 seconds (Instant)** | 🐢 1.5 - 3.0 seconds | 🐢 Variable lag |
| **GPU Hardware Accel** | 🚀 **AMD Radeon, NVIDIA, Intel** | ❌ Server dependent | ❌ N/A |
| **Auto-Pasting** | 🎯 **Active Window Focus Tracking** | ❌ Manual Copy/Paste | ⚠️ Basic text input |
| **Anti-Hallucination** | 🛡️ **Built-in YouTube Filter** | ❌ Raw hallucinations | ❌ Common mistranscriptions |
| **Cost** | 🆓 **100% Free Forever (MIT)** | 💰 Pay per minute / API quota | ⚠️ Subscription bound |

---

## 📥 Downloads (Cross-Platform Standalone Binaries)

Choose your operating system and start dictating in 1 click!

| OS Platform | Download Link | Notes |
| :--- | :--- | :--- |
| **🪟 Windows (10 / 11)** | 👉 **[Download `WhisperVoiceDictation.exe`](https://github.com/yurac777/whisper-voice-dictation-ai/releases/latest/download/WhisperVoiceDictation.exe)** | Portable `.exe` (No installation needed) |
| **🐧 Linux (Ubuntu / Arch / Fedora)** | 👉 **[Download `WhisperVoiceDictation-Linux.tar.gz`](https://github.com/yurac777/whisper-voice-dictation-ai/releases)** | Standalone binary archive |
| **🍎 macOS (Intel / Apple Silicon)** | 👉 **[Download `WhisperVoiceDictation-macOS.zip`](https://github.com/yurac777/whisper-voice-dictation-ai/releases)** | Standalone `.zip` application |

---

## 🚀 Key Features

- ⚡ **Direct In-Memory RAM Audio Pipeline:** Audio array buffers are passed directly from microphone RAM memory straight to the neural network decoder, bypassing disk WAV writes for sub-300ms response time.
- 🎮 **Hardware GPU Acceleration (AMD / NVIDIA / Intel):** Built-in support for **Microsoft DirectML (`DmlExecutionProvider`)**, leveraging AMD Radeon iGPUs (e.g. 880M/780M), NVIDIA GPUs, and Intel Arc.
- 🎯 **Smart Active Window Target Tracker:** Automatically tracks your active working window (Telegram, Word, Chrome, VS Code) even when clicking the GUI widget button.
- 🛡️ **Zero Subtitle Hallucination Filter:** Built-in `clean_hallucinated_subtitles` parser eliminates phantom YouTube credits ("Субтитры создавал...", "Редактор...") when recording silent background audio.
- 🌍 **99+ Languages & Presets:** Native support for English, Russian, German, French, Spanish, Chinese, Japanese, etc.
- ⌨️ **Custom Hotkeys:** Bind activation to Middle Mouse Click, Right Alt, Right Ctrl, F9, F10.
- 📍 **Apple Dynamic Island UI:** Floating, sleek, dark-themed Widget that docks to top/bottom of screen.

---

## ⌨️ Hotkey Cheat Sheet

| Shortcut | Action |
| :--- | :--- |
| **Middle Click / R-Alt / R-Ctrl / F9 / F10** | Start / Stop Dictation |
| **`ESC`** | Cancel active recording immediately |
| **`Pause / Break`** | Convert layout of selected text (RU ↔ EN) |

---

## 🛠️ Build & Run from Source

```bash
# 1. Clone the repo
git clone https://github.com/yurac777/whisper-voice-dictation-ai.git
cd whisper-voice-dictation-ai

# 2. Setup Virtual Environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install Requirements
pip install -r requirements.txt

# 4. Launch Application
pythonw main.py
```

---

## 📄 License

Distributed under the **MIT License**. Free for personal and commercial use.
