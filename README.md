# 🎙️ Whisper Voice Dictation AI for Windows 11

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-UI-purple?style=for-the-badge&logo=qt" alt="PyQt6">
  <img src="https://img.shields.io/badge/OpenAI-Whisper_AI-brightgreen?style=for-the-badge&logo=openai" alt="Whisper AI">
  <img src="https://img.shields.io/badge/Windows-11-0078D4?style=for-the-badge&logo=windows" alt="Windows 11">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge" alt="PRs Welcome">
</p>

<p align="center">
  <b>Ультра-быстрый офлайн голосовой ввод с ИИ (Whisper AI) в любое активное окно Windows 11 с интерфейсом в стиле Dynamic Island!</b><br>
  <i>Ultra-fast offline AI voice dictation widget for Windows 11 with direct window auto-typing.</i>
</p>

---

## 🌟 Почему этот проект особенный? (Features)

- ⚡ **Прямой ввод в фокусное окно (`AttachThreadInput`):** Текст вставляется мгновенно по нажатию кнопки прямо в Telegram, VS Code, браузер, Discord, Word или любой текстовый редактор.
- 🖱️ **Активация с колесика мыши (Middle Click):** Кликнули колесико мыши в любом месте системы — начинается запись. Повторный клик — мгновенный текст.
- 🎨 **Минималистичный виджет 320px (Glassmorphism):** Легкая панель вверху экрана, не заслоняет обзор и прячет настройки под иконку `⚙️`.
- ❌ **Мгновенная отмена (ESC / ❌):** Возможность мгновенно отменить запись или прервать процесс распознавания.
- 🌐 **Быстрый помощник раскладки (`Pause/Break`):** Автоматический перевод ошибочно набранного текста между RU ↔ EN (`гшиги` ↔ `github`).
- ⚡ **Оптимизирован для CPU/iGPU (INT8):** Работает на локальной машине с задержкой 0.3 секунды без подписок и API-ключей.
- 🔒 **100% Приватность данных:** Ваша речь обрабатывается локально и никогда не передается на сторонние сервера.

---

## 🛠️ Горячие клавиши (Hotkeys)

| Клавиша | Функция |
| :--- | :--- |
| **Middle Mouse Click** | Начать / Завершить голосовой ввод |
| **`ESC`** | Мгновенная отмена записи или распознавания |
| **`Pause / Break`** | Сменить раскладку выделенного текста (RU ↔ EN) |

---

## 🚀 Быстрый запуск (Quick Start)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/yurac777/whisper-voice-dictation-ai.git
cd whisper-voice-dictation-ai

# 2. Установить зависимости
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Запустить приложение
pythonw main.py
```

Или просто запустите файл `run.bat` для старта в 1 клик!

---

## 🤝 Вклад в развитие (Contributing)

Приветствуются любые Пулл-Реквесты (PR) и идеи по улучшению! Если проект вам понравился, поставьте ⭐ **Star** на GitHub!

---

## 📄 Лицензия

Распространяется под открытой лицензией **MIT License**. Подробности в файле [LICENSE](LICENSE).
