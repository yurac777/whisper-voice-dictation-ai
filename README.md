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
  <b>Ultra-fast, 100% offline, local AI voice dictation widget for Windows 11 with 99+ languages support, dynamic window auto-typing, customizable hotkeys, and Apple Dynamic Island-style UI.</b>
</p>

---

## 📦 1-Click Portable Download

No Python setup required! Download the pre-compiled, 100% portable `.exe` from GitHub Releases:

👉 **[📥 DOWNLOAD LATEST RELEASE (WhisperVoiceDictation.exe)](https://github.com/yurac777/whisper-voice-dictation-ai/releases)**

* 🚀 **100% Portable:** Zero installation required. Runs directly from USB or any folder.
* 🛡️ **Local Logging (`app.log`):** Detailed event logs are saved next to the executable for easy debugging.
* 🔒 **100% Offline & Private:** Audio is processed locally on CPU (INT8 quantized). No cloud APIs, subscriptions, or telemetry.

---

## ✨ Features Breakdown

- 🌍 **99+ Multilingual Speech Recognition:** Powered by OpenAI Whisper (`CTranslate2` engine). Includes **Auto-Detect Language Mode** and dedicated presets for English, Spanish, German, French, Chinese, Japanese, Russian, Ukrainian, Polish, Turkish, and more.
- 🎯 **Direct Window Focus Auto-Typing (`AttachThreadInput`):** Instantly types recognized text directly into whichever app you are focused on (Telegram, VS Code, Browser, Word, Discord, Notepad, etc.).
- 🟢 **Vibrant Visual State Indicators:**
  - `🟢 Ready` (Green) — App is active and listening for your hotkey.
  - `🔴 Recording` (Pulsating Red) — Audio recording in progress.
  - `⚡ Processing` (Yellow) — AI transcribing speech locally.
  - `✅ Pasted` (Cyan/Green) — Text pasted directly into your active window.
- ⌨️ **Customizable Hotkey Selector:** Change the trigger key in Settings (`⚙️`) to **Middle Mouse Click**, **Right Alt**, **Right Ctrl**, **F9**, or **F10**.
- 🖥️ **Smart Multi-Monitor Jump:** The widget floating pill automatically tracks your active mouse cursor and docks at the top-center of the screen you are working on.
- 📍 **Custom Widget Docking:** Choose default positioning (Top-Center, Bottom-Center, Top-Right, or Drag & Remember).
- ⚡ **Live Real-time Streaming Mode:** Option to continuously stream and type text live every 2.5 seconds while speaking.
- 🌐 **Instant Layout Converter (`Pause / Break`):** Convert mis-typed text between RU ↔ EN keyboard layouts (`гшиги` ↔ `github`).

---

## ⌨️ Hotkey Matrix

| Shortcut | Description |
| :--- | :--- |
| **Middle Click / R-Alt / R-Ctrl / F9 / F10** | Start / Stop Voice Dictation |
| **`ESC`** | Cancel active recording / transcription immediately |
| **`Pause / Break`** | Convert layout of selected text (RU ↔ EN) |

---

## 🌍 Multilingual Usage Guide

1. Click **⚙️ Settings** on the widget bar.
2. Select your desired language from **🌍 Language / Язык**:
   - `🌐 Auto-Detect` — Automatically identifies the language you speak.
   - `🇺🇸 English` — Optimized for English dictation and technical terminology.
   - `🇷🇺 Russian` — Optimized for Russian dictation.
   - `🇪🇸 Spanish / 🇩🇪 German / 🇫🇷 French / 🇨🇳 Chinese / 🇯🇵 Japanese`, etc.
3. Click **💾 Save Settings**.

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
