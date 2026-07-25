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
  <b>Ультра-быстрый, 100% офлайн голосовой ввод с ИИ (OpenAI Whisper) для Windows 11 с поддержкой 99+ языков, автоматической вставкой в активное окно, настраиваемыми кнопками и виджетом в стиле Apple Dynamic Island.</b>
</p>

---

## 📦 1-Click Портативная Версия (Скачать готовый EXE)

Вам **не нужно устанавливать Python**, библиотеки или открывать консоль! Скачайте готовый `.exe` файл из раздела **Releases**:

👉 **[📥 СКАЧАТЬ ПОСЛЕДНЮЮ ВЕРСИЮ (WhisperVoiceDictation.exe)](https://github.com/yurac777/whisper-voice-dictation-ai/releases)**

* 🚀 **100% Портативно:** Работает без установки, можно запускать с флешки.
* 🛡️ **Логирование (`app.log`):** Логи всех событий автоматически создаются рядом с `.exe`.
* 🔒 **100% Приватно и Офлайн:** Звук обрабатывается локально на CPU (INT8). Никаких подписок и отправки данных в облако.

---

## ✨ Ключевые возможности

- 🌍 **99+ Языков и Автоопределение:** Базируется на OpenAI Whisper (`CTranslate2`). Поддерживает автоопределение языка и профили для русского, английского, испанского, немецкого, французского, китайского, японского, украинского, польского и др.
- 🎯 **Прямой ввод в фокусное окно (`AttachThreadInput`):** Текст вставляется мгновенно прямо в Telegram, VS Code, браузер, Discord, Word или любой текстовый редактор.
- 🟢 **Понятные визуальные статусы кнопки:**
  - `🟢 Надиктовать` (Зеленый) — Готов к записи и ждет горячую клавишу.
  - `🔴 Идет запись...` (Красный) — Идет запись с микрофона.
  - `⚡ ИИ-обработка...` (Желтый) — ИИ локально распознает речь.
  - `✅ Вставлено!` (Бирюзовый) — Текст вставлен в ваше окно.
- ⌨️ **Настраиваемые горячие клавиши:** В меню **⚙️ Настройки** можно выбрать **Колесико мыши**, **Right Alt**, **Right Ctrl**, **F9** или **F10**.
- 🖥️ **Умная поддержка двух мониторов:** Виджет автоматически появляется вверху того экрана, на котором находится ваш курсор и активное окно!
- 📍 **Размещение виджета:** Выбирайте позицию (Верх по центру, Низ по центру, Верх справа или Произвольное перетаскивание).
- ⚡ **Печать в реальном времени (Live Streaming):** Возможность непрерывного ввода текста каждые 2.5 секунды прямо во время речи.
- 🌐 **Быстрый перевод раскладки (`Pause/Break`):** Смена ошибочно набранного текста между RU ↔ EN (`гшиги` ↔ `github`).

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
