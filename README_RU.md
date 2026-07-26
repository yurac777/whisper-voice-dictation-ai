# 🎙️ Whisper Voice Dictation AI (Офлайн Голосовой Диктант)

<p align="center">
  <img src="https://img.shields.io/github/v/release/yurac777/whisper-voice-dictation-ai?style=for-the-badge&color=74c7ec&logo=github" alt="Release">
  <img src="https://img.shields.io/github/downloads/yurac777/whisper-voice-dictation-ai/total?style=for-the-badge&color=a6e3a1&logo=github" alt="Downloads">
  <img src="https://img.shields.io/badge/Платформы-Windows%20%7C%20Linux%20%7C%20macOS-89b4fa?style=for-the-badge&logo=windows" alt="Платформы">
  <img src="https://img.shields.io/badge/GPU%20Ускорение-AMD%20DirectML%20%7C%20NVIDIA%20CUDA-fab387?style=for-the-badge&logo=amd" alt="GPU Ускорение">
  <img src="https://img.shields.io/badge/Задержка-0.2%20сек-f9e2af?style=for-the-badge&logo=lightning" alt="Задержка">
  <img src="https://img.shields.io/badge/Лицензия-MIT-green?style=for-the-badge" alt="Лицензия">
</p>

<p align="center">
  <b>[ 🇺🇸 English ](README.md) | [ 🇷🇺 Русский ](README_RU.md)</b>
</p>

<p align="center">
  <b>Ультрабыстрый, 100% локальный ИИ-виджет голосовой надиктовки текста для Windows, Linux и macOS. Работает на базе OpenAI Whisper Turbo, DirectML GPU ускорения (AMD/NVIDIA/Intel), прямым декодированием в RAM и автовставкой текста в активное окно.</b>
</p>

---

## 🌟 Почему Whisper Voice Dictation AI?

| Возможность | 🎙️ Whisper Dictation AI | ☁️ Облачные сервисы (Яндекс/Whisper API) | 🪟 Встроенный ввод Windows |
| :--- | :---: | :---: | :---: |
| **Приватность и Офлайн** | 🔒 **100% Локально и Офлайн** | ❌ Отправляет ваш голос на серверы | ❌ Требует интернет |
| **Скорость распознавания** | ⚡ **~0.25 секунды (Рекорд)** | 🐢 1.5 - 3.0 секунды | 🐢 Задержки ввода |
| **Ускорение на GPU** | 🚀 **AMD Radeon, NVIDIA, Intel** | ❌ Зависит от сервера | ❌ Нет |
| **Автоматическая вставка** | 🎯 **Отслеживание активного окна** | ❌ Только вручную через буфер | ⚠️ Ограничено |
| **Защита от галлюцинаций** | 🛡️ **Фильтр YouTube-титров** | ❌ Сырые «субтитры» | ❌ Ошибки распознавания |
| **Цена** | 🆓 **Бесплатно навсегда (MIT)** | 💰 Платно за каждую минуту | ⚠️ Завязано на подписку |

---

## 📥 Скачать готовые программы (Не требуют установки Python)

Выберите вашу операционную систему и запустите в 1 клик!

| ОС Платформа | Ссылка на скачивание | Примечание |
| :--- | :--- | :--- |
| **🪟 Windows (10 / 11)** | 👉 **[Скачать `WhisperVoiceDictation.exe`](https://github.com/yurac777/whisper-voice-dictation-ai/releases/latest/download/WhisperVoiceDictation.exe)** | Портативный `.exe` (не требует установки) |
| **🐧 Linux (Ubuntu / Arch / Fedora)** | 👉 **[Скачать `WhisperVoiceDictation-Linux.tar.gz`](https://github.com/yurac777/whisper-voice-dictation-ai/releases)** | Архив с исполняемым бинарником |
| **🍎 macOS (Intel / Apple Silicon)** | 👉 **[Скачать `WhisperVoiceDictation-macOS.zip`](https://github.com/yurac777/whisper-voice-dictation-ai/releases)** | Архив готовой программы macOS |

---

## 🚀 Главные преимущества и фичи

- ⚡ **Передача аудио прямо в RAM памяти:** Звук из микрофона передаётся напрямую в нейросеть без записи и чтения с жесткого диска, снижая задержку после отжатия кнопки до **~0.25 сек**!
- 🎮 **Аппаратное GPU-ускорение (AMD / NVIDIA / Intel):** Встроенная поддержка **Microsoft DirectML (`DmlExecutionProvider`)** задействует графические ядра AMD Radeon (880M / 780M / 680M), NVIDIA и Intel Arc!
- 🎯 **Умное отслеживание фокуса окон:** Программа автоматически запоминает ваше рабочее приложение (Telegram, Word, браузер, VS Code) и вставляет текст точно в него, даже если вы кликаете по кнопке мышкой!
- 🛡️ **Фильтр фантомных субтитров:** Алгоритм `clean_hallucinated_subtitles` мгновенно вычищает титры из YouTube (вроде *«Субтитры создавал...»*, *«Редактор...»*), если вы молчали при записи.
- 🌍 **99+ языков:** Встроенная поддержка русского, английского, немецкого, французского, испанского, китайского и др.
- ⌨️ **Горячие клавиши:** Привязка запуска на клик колёсиком мыши, Правый Alt, Правый Ctrl, F9, F10.

---

## ⌨️ Горячие клавиши

| Сочетание | Действие |
| :--- | :--- |
| **Клик колесиком / R-Alt / R-Ctrl / F9 / F10** | Начать / Завершить голосовую надиктовку |
| **`ESC`** | Мгновенно отменить запись |
| **`Pause / Break`** | Сменить раскладку выделенного текста (RU ↔ EN) |

---

## 📄 Лицензия

Распространяется по лицензии **MIT**. Бесплатно для личного и коммерческого использования.
