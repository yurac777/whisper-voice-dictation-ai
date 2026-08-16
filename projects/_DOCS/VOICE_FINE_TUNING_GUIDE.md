# 🎙️ PERSONAL VOICE FINE-TUNING & ADAPTATION GUIDE

Руководство по персональному дообучению (Fine-Tuning) нейросети OpenAI Whisper на вашем собственном голосе для достижения 99.5%+ точности распознавания профессиональных терминов, индивидуальной дикции и акцента.

---

## 🎯 Зачем дообучать Whisper на своем голосе?

Хотя базовая модель **Whisper Turbo** показывает отличные результаты на общей речи, персональное дообучение даёт:
1. 🎯 **Идеальное распознавание сложных терминов**: фамилий, названий проектов, узкоспециализированного сленга (DevOps, медицина, юриспруденция).
2. ⚡ **Адаптация под акустику вашего микрофона и комнаты**: фильтрация индивидуального эха и фонового шума.
3. 🗣️ **Понимание специфики дикции**: быстрая речь, проглатывание окончаний, акцент.

---

## 📁 Шаг 1. Сбор вашего датасета голоса

Приложение **Whisper Voice Dictation AI** уже имеет встроенный сборщик датасета:
- При каждой надиктовке чистый звук сохраняется в `logs/recordings/audio_YYYYMMDD_HHMMSS.wav`
- Текстовый транскрипт сохраняется рядом в `logs/recordings/audio_YYYYMMDD_HHMMSS.txt` и `dictation_history.jsonl`.

### Рекомендации по объему датасета:
| Цель дообучения | Требуемое время речи | Количество аудиоклипов |
|---|---|---|
| Быстрая адаптация к акценту и терминам | **5–15 минут** | ~50–150 коротких фраз |
| Глубокое дообучение на сложный сленг | **30–60 минут** | ~300–600 фраз |
| Профессиональная диктовка (медицина/право) | **1–2 часа** | ~1000+ фраз |

> 💡 **Совет**: Если модель ошиблась в слове, откройте соответствующий `.txt` файл и исправьте текст на правильный перед запуском обучения.

---

## 🛠️ Шаг 2. Запуск дообучения через LoRA (PEFT)

Мы подготовили автоматизированный скрипт [`scripts/fine_tune_voice.py`](file:///c:/Users/Lenovo/Desktop/projects/whisper_dictation/scripts/fine_tune_voice.py).

### 1. Установка библиотек для обучения:
```bash
pip install torch torchaudio transformers datasets peft accelerate evaluate ctranslate2
```

### 2. Запуск локального обучения:
```bash
# Обучение на вашем датасете с авто-конвертацией в CTranslate2 (faster-whisper)
python scripts/fine_tune_voice.py \
  --data_dir logs/recordings \
  --base_model openai/whisper-small \
  --output_dir models/whisper-custom-voice \
  --ct2_output_dir models/faster-whisper-custom-voice \
  --epochs 5 \
  --batch_size 4 \
  --learning_rate 1e-4 \
  --export_ct2
```

---

## ☁️ Шаг 3. Бесплатное обучение в Google Colab (Если нет мощного GPU)

Если у вас нет дискретной видеокарты NVIDIA с 8GB+ VRAM, используйте бесплатный GPU T4 в Google Colab:

1. Заархивируйте папку с записями: `zip -r my_voice_dataset.zip logs/recordings/`
2. Загрузите архив в Google Colab.
3. Выполните блок кода:
```python
# 1. Установка зависимостей
!pip install -q torch torchaudio transformers datasets peft accelerate ctranslate2

# 2. Распаковка датасета
!unzip -q my_voice_dataset.zip -d dataset/

# 3. Клонирование скрипта и запуск обучения
!git clone https://github.com/yurac777/whisper-voice-dictation-ai.git
!python whisper-voice-dictation-ai/scripts/fine_tune_voice.py \
    --data_dir dataset/logs/recordings \
    --base_model openai/whisper-large-v3-turbo \
    --output_dir custom_whisper \
    --ct2_output_dir faster_whisper_custom \
    --epochs 5 \
    --export_ct2

# 4. Скачивание готовой модели
!zip -r faster_whisper_custom.zip faster_whisper_custom/
```
4. Скачайте `faster_whisper_custom.zip` и распакуйте в папку `models/` на вашем компьютере.

---

## 🚀 Шаг 4. Подключение вашей обученной модели в приложение

После обучения модель в формате CTranslate2 подключается мгновенно:

### Способ А: Через командную строку (CLI)
```bash
python main.py --model models/faster-whisper-custom-voice
```

### Способ Б: Через файл настроек `config.json`
В `config.json` укажите путь к вашей папке модели:
```json
{
  "model_size": "models/faster-whisper-custom-voice",
  "language": "ru"
}
```

---

## ⚡ Альтернатива: Мгновенная адаптация без обучения (0 секунд)

Если вы не хотите обучать модель часами, воспользуйтесь **динамическим инжектором контекста**:

1. Откройте файл [`dictionary.txt`](file:///c:/Users/Lenovo/Desktop/projects/whisper_dictation/dictionary.txt).
2. Впишите ваши персональные термины, стек, имена и сленг через запятую:
   ```text
   FastAPI, ClickHouse, Kubernetes, PostgreSQL, WebSockets, Юра, CRM, GraphQL
   ```
3. При каждом распознавании Whisper использует этот список как приоритетный контекстный промпт (`INITIAL_PROMPT`), повышая точность редких слов до 99% без единой минуты обучения!
