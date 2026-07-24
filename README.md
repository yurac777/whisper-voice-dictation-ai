# 🎙️ Whisper Voice Dictation AI for Windows 11

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-UI-purple?style=for-the-badge&logo=qt" alt="PyQt6">
  <img src="https://img.shields.io/badge/OpenAI-Whisper_AI-brightgreen?style=for-the-badge&logo=openai" alt="Whisper AI">
  <img src="https://img.shields.io/badge/Windows-11-0078D4?style=for-the-badge&logo=windows" alt="Windows 11">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>Ультра-быстрый офлайн голосовой ввод с ИИ (Whisper AI) в любое активное окно Windows 11 с интерфейсом в стиле Dynamic Island!</b><br>
  <i>Ultra-fast offline AI voice dictation portable widget for Windows 11 with direct window auto-typing.</i>
</p>

---

## 📦 1-Click Download (Скачать готовую портативную версию)

Вам **не нужно устанавливать Python**, библиотеки или открывать консоль! Просто скачайте готовый `.exe` файл из раздела **Releases**:

👉 **[📥 СКАЧАТЬ ПОСЛЕДНЮЮ ВЕРСИЮ (WhisperVoiceDictation.exe)](https://github.com/yurac777/whisper-voice-dictation-ai/releases)**

* 🚀 **100% Портативно:** Работает без установки, можно запускать с флешки.
* 🛡️ **Авто-логирование (`app.log`):** Логи всех событий создаются рядом с приложением.

---

## ✨ Ключевые возможности

- 🎯 **Прямой ввод в фокусное окно (`AttachThreadInput`):** Текст вставляется мгновенно по нажатию кнопки прямо в Telegram, VS Code, браузер, Discord, Word или любой текстовый редактор.
- 🖱️ **Активация с колесика мыши (Middle Click):** Кликнули колесико мыши в любом месте системы — начинается запись. Повторный клик — мгновенная вставка.
- 🖥️ **Умная поддержка двух мониторов:** Плашка автоматически появляется вверху того экрана, на котором находится ваш курсор и активное окно!
- 🎨 **Минималистичный виджет 320px (Glassmorphism):** Легкая панель вверху экрана в стиле Apple Dynamic Island.
- 🔴 **Динамическая иконка в трее:** Отображает статус записи (Синий = Готов, Красный = Запись, Желтый = ИИ-обработка).
- ❌ **Мгновенная отмена (ESC / ❌):** Возможность мгновенно отменить запись или прервать процесс распознавания.
- 🌐 **Быстрый помощник раскладки (`Pause/Break`):** Автоматический перевод ошибочно набранного текста между RU ↔ EN (`гшиги` ↔ `github`).
- ⚡ **Оптимизирован для CPU (INT8):** Работает на локальной машине с задержкой 0.3 секунды без подписок и API-ключей.

---

## 🛠️ Горячие клавиши (Hotkeys)

| Клавиша | Функция |
| :--- | :--- |
| **Middle Mouse Click** | Начать / Завершить голосовой ввод |
| **`ESC`** | Мгновенная отмена записи или распознавания |
| **`Pause / Break`** | Сменить раскладку выделенного текста (RU ↔ EN) |

---

## 🚀 Сборка из исходников (For Developers)

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
