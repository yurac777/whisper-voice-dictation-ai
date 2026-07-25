# 🎙️ Whisper Voice Dictation AI (Multilingual & Portable)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-UI-purple?style=for-the-badge&logo=qt" alt="PyQt6">
  <img src="https://img.shields.io/badge/OpenAI-Whisper_AI-brightgreen?style=for-the-badge&logo=openai" alt="Whisper AI">
  <img src="https://img.shields.io/badge/Languages-99%2B_Supported-orange?style=for-the-badge&logo=googletranslate" alt="Multilingual">
  <img src="https://img.shields.io/badge/Windows-11-0078D4?style=for-the-badge&logo=windows" alt="Windows 11">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>[ 🇺🇸 English ](README.md) | [ 🇷🇺 Русский ](README_RU.md)</b>
</p>

<p align="center">
  <b>Ultra-fast, 100% offline, local AI voice dictation widget for Windows 11 with 99+ languages support, dynamic window auto-typing, customizable hotkeys, intelligent accidental click defense, and Apple Dynamic Island-style UI.</b>
</p>

---

## 📦 1-Click Portable Download & Installation Guide

No Python installation required! Follow these 2 simple steps:

### Step 1: Download the Executable
👉 **[📥 DOWNLOAD LATEST RELEASE (v1.2.0 - WhisperVoiceDictation.exe)](https://github.com/yurac777/whisper-voice-dictation-ai/releases)**

### Step 2: Launch & Dictate!
1. Save `WhisperVoiceDictation.exe` in any folder or USB drive.
2. Double-click **`WhisperVoiceDictation.exe`** to launch.
3. Focus any app (Telegram, VS Code, Browser, Word) and **Click Middle Mouse Button** to start dictation!

---

## 📜 Release Notes & What's New in v1.2.0

- 🌍 **99+ Multilingual Speech Recognition Engine:** Integrated OpenAI Whisper language selection with Auto-Detect Mode (`auto`) and dedicated presets for English, Spanish, German, French, Chinese, Japanese, Russian, Ukrainian, Polish, Turkish.
- ⚙️ **Settings Dialog Modal (`SettingsDialog`):** Customize language, hotkey, max recording duration (10-300s), and accidental click sensitivity (0.1-2.0s).
- 🛡️ **Intelligent Failsafes:**
  - **Accidental Click Protection:** Cancels instantly if recording duration is `< 0.4s`.
  - **Silence Volume Threshold:** Ignores pure background silence (`RMS < 0.008`).
  - **Max Duration Timeout:** Auto-stops after 60 seconds to prevent run-away background recording.
- 🟢 **Vibrant Green Ready Indicator:** Dynamic state colors (`🟢 Ready`, `🔴 Recording`, `⚡ Transcribing`, `✅ Pasted`).
- ⌨️ **Custom Hotkeys:** Bind trigger to Middle Mouse Click, Right Alt, Right Ctrl, F9, or F10.
- 📍 **Widget Position Docking:** Snap widget to Top-Center, Bottom-Center, Top-Right, or Drag & Remember position.

---

## ⌨️ Hotkey Matrix

| Shortcut | Description |
| :--- | :--- |
| **Middle Click / R-Alt / R-Ctrl / F9 / F10** | Start / Stop Voice Dictation |
| **`ESC`** | Cancel active recording / transcription immediately |
| **`Pause / Break`** | Convert layout of selected text (RU ↔ EN) |

---

## 🛠️ Build from Source (For Developers)

```bash
# 1. Clone the repository
git clone https://github.com/yurac777/whisper-voice-dictation-ai.git
cd whisper-voice-dictation-ai

# 2. Create virtual environment & install dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Run application or build single-file EXE
pythonw main.py
build_exe.bat
```

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
