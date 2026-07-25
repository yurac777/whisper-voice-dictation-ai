# 🎙️ Whisper Voice Dictation AI (Мультиязычный и Портативный)

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
  <b>Ультра-быстрый, 100% офлайн голосовой ввод с ИИ (OpenAI Whisper) для Windows 11 с поддержкой 99+ языков, автоматической вставкой в активное окно, защитой от случайных кликов и виджетом в стиле Apple Dynamic Island.</b>
</p>

---

## 📦 Инструкция по скачиванию и запуску (1-Click Portable)

Вам **не нужно устанавливать Python**, библиотеки или открывать консоль!

### Шаг 1: Скачайте готовый `.exe`
👉 **[📥 СКАЧАТЬ ПОСЛЕДНЮЮ ВЕРСИЮ (v1.2.0 - WhisperVoiceDictation.exe)](https://github.com/yurac777/whisper-voice-dictation-ai/releases)**

### Шаг 2: Запустите и пользуйтесь!
1. Поместите файл `WhisperVoiceDictation.exe` в любую папку или на флешку.
2. Запустите двойным кликом по **`WhisperVoiceDictation.exe`**.
3. Кликните в любое окно (Telegram, VS Code, браузер, Word) и **нажмите колесико мыши** для начала диктовки!

---

## 📜 Список изменений (Что нового в релизе v1.2.0)

- 🌍 **Мультиязычный движок (99+ языков):** Выбор любого языка или автоопределение (`auto`) в настройках (Русский, English, Español, Deutsch, Français, 中文, 日本語, Українська, Polski, Türkçe).
- ⚙️ **Полное окно Настроек (`⚙️`):** Регулировка языков, кнопки записи, максимума записи (10-300 сек) и порога защиты от коротких кликов (0.1-2.0 сек).
- 🛡️ **Интеллектуальные защиты:**
  - **Защита от случайных кликов:** Мгновенная отмена, если запись длится `< 0.4 сек`.
  - **Детектор тишины:** Отмена, если вокруг тишина и вы ничего не сказали (`RMS < 0.008`).
  - **Авто-таймаут:** Автоматическая остановка через 60 секунд.
- 🟢 **Зеленая кнопка готовности `🟢`:** Понятные статусы (`🟢 Надиктовать`, `🔴 Идет запись`, `⚡ ИИ-обработка`, `✅ Вставлено`).
- ⌨️ **Выбор кнопки записи:** Поддержка Колесика мыши, Right Alt, Right Ctrl, F9, F10.
- 📍 **Позиционирование виджета:** Прилипание вверху по центру, внизу по центру, вверху справа или с запоминанием ручного перетаскивания.

---

## ⌨️ Горячие клавиши (Hotkeys)

| Клавиша | Функция |
| :--- | :--- |
| **Middle Click / R-Alt / R-Ctrl / F9 / F10** | Начать / Завершить голосовой ввод |
| **`ESC`** | Мгновенная отмена записи или распознавания |
| **`Pause / Break`** | Сменить раскладку выделенного текста (RU ↔ EN) |

---

## 🛠️ Сборка из исходников (Для разработчиков)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yurac777/whisper-voice-dictation-ai.git
cd whisper-voice-dictation-ai

# 2. Установить зависимости
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Запустить приложение или собрать EXE
pythonw main.py
build_exe.bat
```

---

## 📄 Лицензия

Распространяется под открытой лицензией **MIT License**. Подробности в файле [LICENSE](LICENSE).
