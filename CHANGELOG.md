# 📜 Changelog

All notable changes to **Whisper Voice Dictation AI** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.2.0] - 2026-07-25

### Added
- 🌍 **99+ Multilingual Speech Recognition Engine:** Integrated OpenAI Whisper language selection with Auto-Detect Mode (`auto`) and presets for `ru`, `en`, `es`, `de`, `fr`, `zh`, `ja`, `uk`, `pl`, `tr`.
- ⚙️ **Settings Dialog Modal (`SettingsDialog`):** Added a PyQt6 GUI configuration window for setting language, trigger hotkey, docking position, AI model size, and streaming mode.
- 🟢 **Vibrant Green Ready Indicator:** Updated idle button to `🟢 Ready` state with clear visual cue.
- ⌨️ **Custom Hotkey Support:** Allow binding trigger button to Middle Mouse Click, Right Alt, Right Ctrl, F9, or F10.
- 📍 **Widget Position Docking:** Added dock modes for Top-Center, Bottom-Center, Top-Right, and Custom Dragged position persistence.
- ⚡ **Live Real-time Streaming Dictation:** Added optional 2.5-second live chunk streaming dictation mode.

---

## [v1.1.0] - 2026-07-24

### Added
- 🖥️ **Smart Multi-Monitor Active Window Tracking:** Floating widget pill automatically jumps to the active monitor (`screenAt(QCursor.pos())`).
- 🛡️ **Portable Logging (`app.log`):** Detailed traceback logging next to executable for portable debugging.
- 🎨 **Dynamic 3-State System Tray Icon:** Visual indicators for Ready (Blue), Recording (Red), and Transcribing (Yellow).

### Fixed
- 🐛 **Sounddevice PyInstaller CFFI Callback Exception:** Replaced PortAudio CFFI callback loop with managed background thread `stream.read()`, eliminating PyInstaller `bad argument to internal function` crashes.

---

## [v1.0.0] - 2026-07-20

### Added
- Initial open-source release of Whisper Voice Dictation AI.
- `AttachThreadInput` direct window auto-typing engine.
- Fast local INT8 CPU inference via `faster_whisper` and `ctranslate2`.
- Instant keyboard layout converter (`Pause/Break` for RU ↔ EN).
