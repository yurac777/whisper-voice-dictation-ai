# 🎙️ Whisper Voice Dictation AI (Windows 11)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-UI-purple?style=for-the-badge&logo=qt)
![Whisper AI](https://img.shields.io/badge/OpenAI-Whisper_AI-brightgreen?style=for-the-badge&logo=openai)
![Platform](https://img.shields.io/badge/Windows-11-0078D4?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Плавающий минималистичный виджет для мгновенной голосовой диктовки текста с помощью искусственного интеллекта **OpenAI Whisper** напрямую в любое активное окно Windows (Telegram, VS Code, Браузер, Word, Блокнот и др.).

---

## ✨ Ключевые возможности

- 🎯 **Автоматическая вставка в активное окно (`AttachThreadInput`):** Надиктованный текст мгновенно вставляется в поле ввода вашего активного приложения без необходимости открывать буфер обмена.
- 🖱️ **Управление с колесика мыши (Middle Click):** Кликнули колесико мыши в любом месте системы — началась запись. Кликнули ещё раз — текст вставился.
- 🎨 **Минималистичный виджет 320px (Windows 11 Glassmorphism):** Легкая панель по центру экрана, которая не закрывает обзор и прячет настройки под иконку `⚙️`.
- ❌ **Мгновенная отмена (ESC / ❌):** Прерывает процесс записи и фонового распознавания на лету.
- 🌐 **Встроенный переключатель раскладки (`Pause/Break`):** Мгновенно конвертирует выделенный текст между русским и английским (`гшиги` ↔ `github`).
- ⚡ **Оптимизировано под многоядерные процессоры (INT8):** Задействует все ядер процессора (AVX-512) и офлайн-квантование для распознавания за 0.3 секунды.
- 🔒 **100% Приватность:** Обработка аудио происходит локально на вашем компьютере, звук никуда не отправляется.

---

## 🛠️ Горячие клавиши и управление

| Горячая клавиша | Действие |
| :--- | :--- |
| **Колесико мыши (Middle Button)** | Начать / Завершить голосовую запись |
| **`ESC`** | Мгновенная отмена записи / распознавания |
| **`Pause / Break`** | Сменить раскладку выделенного текста (RU ↔ EN) |

---

## 🚀 Быстрый запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/yurac777/whisper-voice-dictation-ai.git
cd whisper-voice-dictation-ai
```

### 2. Установка зависимостей
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Запуск приложения
Запустите скрипт `run.bat` или выполните:
```bash
pythonw main.py
```

---

## 📁 Структура проекта

```
├── main.py              # Основной PyQt6 UI виджет и обработчик аудио/Whisper
├── run.bat              # 1-click запуск приложения
├── requirements.txt     # Зависимости Python (faster-whisper, PyQt6, pynput)
├── whisper_icon.ico     # Иконка приложения для системного трея
├── .gitignore           # Игнорирование временных файлов и весов моделей
└── README.md            # Документация проекта
```

---

## 📄 Лицензия

Проект распространяется под открытой лицензией **MIT License**.
