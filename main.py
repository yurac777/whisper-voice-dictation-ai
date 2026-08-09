# -*- coding: utf-8 -*-
import sys, os, time, wave, threading, json, subprocess, traceback, re, shutil, datetime

# Optimize OpenMP thread allocation to prevent C++ thread stack overflow
cpu_cnt = os.cpu_count() or 4
thread_limit = str(min(4, cpu_cnt))
os.environ["OMP_NUM_THREADS"] = thread_limit
os.environ["MKL_NUM_THREADS"] = thread_limit
os.environ["OPENBLAS_NUM_THREADS"] = thread_limit

import sounddevice as sd
import numpy as np
import pyperclip
import win32gui, win32con, win32api, win32process
from pynput import mouse
import keyboard

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, 
                             QVBoxLayout, QLabel, QListWidget, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
                             QSystemTrayIcon, QMenu, QDialog, QFormLayout, QGroupBox, QLineEdit, QFileDialog)
from PyQt6.QtGui import QFont, QIcon, QAction, QColor, QPixmap, QPainter, QBrush, QPen, QCursor

from faster_whisper import WhisperModel

MODELS = {}
APP_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
ICON_PATH = os.path.join(APP_DIR, "whisper_icon.ico")
LOG_PATH = os.path.join(APP_DIR, "app.log")

def log_error(msg):
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception: pass

def global_excepthook(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    log_error(f"UNCAUGHT EXCEPTION:\n{err_msg}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = global_excepthook

MUTEX_NAME = "Global\\WhisperVoiceDictation_SingleInstance_Mutex_v1"

def ensure_single_instance():
    try:
        import win32event, winerror
        mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            print("Whisper Voice AI is already running! Exiting duplicate process.")
            sys.exit(0)
        return mutex
    except Exception as e:
        log_error(f"Single instance check exception: {e}")
        return None

def get_media_playing_state():
    try:
        import asyncio
        from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager, GlobalSystemMediaTransportControlsSessionPlaybackStatus
        async def fetch_state():
            manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
            session = manager.get_current_session()
            if session:
                info = session.get_playback_info()
                return info.playback_status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING
            return False
        return asyncio.run(fetch_state())
    except Exception as e:
        log_error(f"Winsdk media state error: {e}")
        return False

def toggle_media_play_pause():
    try:
        import keyboard
        keyboard.send('play/pause media')
    except Exception as e:
        log_error(f"Media play/pause key error: {e}")

INITIAL_PROMPT = "Привет! Это диктовка: GitHub, Python, Docker, API, Telegram, Wi-Fi, Windows, ChatGPT, YouTube, OpenWrt, SSD."

DEFAULT_CONFIG = {
    "hotkey": "middle_click",
    "hotkey_mode": "toggle",
    "ignore_fast_middle_click": True,
    "middle_click_delay_ms": 120,
    "pause_media_on_record": True,
    "position_mode": "top_center",
    "custom_x": -1,
    "custom_y": -1,
    "realtime_mode": False,
    "autopaste": True,
    "model_size": "turbo",
    "language": "ru",
    "max_duration_sec": 120,
    "min_duration_sec": 0.2,
    "check_silence": True,
    "silence_rms_threshold": 0.00005,
    "save_audio_logs": True,
    "save_audio_dir": "logs/recordings"
}

LANGUAGES = [
    ("🌐 Автоопределение (Auto-detect)", "auto"),
    ("🇷🇺 Русский (Russian)", "ru"),
    ("🇺🇸 English (Английский)", "en"),
    ("🇪🇸 Español (Испанский)", "es"),
    ("🇩🇪 Deutsch (Немецкий)", "de"),
    ("🇫🇷 Français (Французский)", "fr"),
    ("🇨🇳 中文 (Китайский)", "zh"),
    ("🇯🇵 日本語 (Японский)", "ja"),
    ("🇺🇦 Українська (Украинский)", "uk"),
    ("🇵🇱 Polski (Польский)", "pl"),
    ("🇹🇷 Türkçe (Турецкий)", "tr")
]

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return {**DEFAULT_CONFIG, **cfg}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save config error:", e)

EN_TO_RU = str.maketrans(
    "`qwertzuiop[]asdfghjkl;'zxcvbnm,./~QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?",
    "ёйцукенгшщзхъфывапролджэячсмитьбю.ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,"
)
RU_TO_EN = str.maketrans(
    "ёйцукенгшщзхъфывапролджэячсмитьбю.ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,",
    "`qwertzuiop[]asdfghjkl;'zxcvbnm,./~QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?"
)

def create_tray_icon_pixmap(color_hex, recording=False):
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    painter.setBrush(QBrush(QColor(color_hex)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    
    if recording:
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(10, 10, 12, 12)
    else:
        painter.setBrush(QBrush(QColor("#1e1e2e")))
        painter.drawEllipse(8, 8, 16, 16)
        
    painter.end()
    return QIcon(pixmap)

def convert_current_selection_layout():
    try:
        pyperclip.copy("")
        time.sleep(0.02)
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('C'), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        
        text = pyperclip.paste()
        if text:
            ru_cnt = sum(1 for c in text if 'а' <= c <= 'я' or 'А' <= c <= 'Я')
            en_cnt = sum(1 for c in text if 'a' <= c <= 'z' or 'A' <= c <= 'Z')
            if en_cnt >= ru_cnt:
                converted = text.translate(EN_TO_RU)
            else:
                converted = text.translate(RU_TO_EN)
                
            pyperclip.copy(converted)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.03)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print("Layout conversion error:", e)

def get_whisper_model(size="turbo"):
    global MODELS
    if size not in MODELS:
        device = "cpu"
        compute_type = "int8"
        try:
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                device = "cuda"
                compute_type = "float16"
        except Exception:
            pass

        thread_cnt = min(4, os.cpu_count() or 4)
        if device == "cuda":
            print(f"Loading OpenAI Whisper model '{size}' on NVIDIA GPU (CUDA, float16)...")
            MODELS[size] = WhisperModel(size, device="cuda", compute_type="float16")
        else:
            print(f"Loading OpenAI Whisper model '{size}' on CPU (int8, {thread_cnt} OpenMP threads)...")
            MODELS[size] = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=thread_cnt)
        print(f"Model '{size}' loaded successfully!")
    return MODELS[size]

def paste_text_to_window(target_hwnd, text):
    if not text or not target_hwnd:
        return
    try:
        pyperclip.copy(text)
        time.sleep(0.08)
        
        current_thread = win32api.GetCurrentThreadId()
        target_thread, _ = win32process.GetWindowThreadProcessId(target_hwnd)
        
        if current_thread != target_thread and target_thread != 0:
            win32process.AttachThreadInput(current_thread, target_thread, True)

        try:
            win32gui.ShowWindow(target_hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(target_hwnd)
            win32gui.BringWindowToTop(target_hwnd)
        except Exception as ex:
            print("SetForegroundWindow warning:", ex)
            
        if current_thread != target_thread and target_thread != 0:
            win32process.AttachThreadInput(current_thread, target_thread, False)

        time.sleep(0.12)

        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.03)

        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.04)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print("Error pasting text:", e)

class AudioRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        self.record_thread = None
        self.start_time = 0
        self.stream_error = None
        self.last_rms = 0.0

    def _record_loop(self):
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32') as stream:
                while self.recording:
                    data, _ = stream.read(1024)
                    if self.recording and len(data) > 0:
                        self.audio_data.append(data.copy())
                        self.last_rms = float(np.sqrt(np.mean(data**2)))
        except Exception as e:
            self.stream_error = str(e)
            log_error(f"Recording loop error: {e}")

    def start(self):
        self.audio_data = []
        self.stream_error = None
        self.last_rms = 0.0
        self.start_time = time.time()
        self.recording = True
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()

    def get_stats(self):
        if not self.audio_data:
            return 0.0, 0.0, 0.0
        try:
            data = np.concatenate(self.audio_data, axis=0)
            duration = len(data) / float(self.sample_rate)
            mean_rms = float(np.sqrt(np.mean(data**2)))
            max_peak = float(np.max(np.abs(data)))
            return duration, mean_rms, max_peak
        except Exception as e:
            log_error(f"get_stats error: {e}")
            return 0.0, 0.0, 0.0

    def get_current_audio_file(self, out_filename):
        if not self.audio_data:
            return False
        try:
            data = np.concatenate(self.audio_data, axis=0)
            data_int16 = (data * 32767).astype(np.int16)
            with wave.open(out_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(data_int16.tobytes())
            return True
        except Exception as e:
            log_error(f"Save audio file error: {e}")
            return False

    def get_numpy_audio(self):
        if not self.audio_data:
            return None
        try:
            return np.concatenate(self.audio_data, axis=0).flatten().astype(np.float32)
        except Exception as e:
            log_error(f"get_numpy_audio error: {e}")
            return None

    def stop(self, out_filename):
        self.recording = False
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=1.0)
        return self.get_current_audio_file(out_filename)

    def cancel(self):
        self.recording = False
        self.audio_data = []
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=0.5)

class ModelPreloaderThread(QThread):
    finished_signal = pyqtSignal(str, bool)
    
    def __init__(self, model_size):
        super().__init__()
        self.model_size = model_size

    def run(self):
        try:
            get_whisper_model(self.model_size)
            self.finished_signal.emit(self.model_size, True)
        except Exception as e:
            log_error(f"Model preload error: {e}")
            self.finished_signal.emit(self.model_size, False)

HALLUCINATION_PATTERNS = [
    r'(?:продолжение следует|продолжение в следующем видео)',
    r'(?:субтитры создавал|субтитры сделал|субтитры добавил|субтитры|автор субтитров|сообщество субтитров|редактор субтитров)',
    r'(?:спасибо за просмотр|до скорой встречи|подписывайтесь на канал|ставьте лайки|ставьте лайк)',
    r'(?:благодарю за внимание|переводчик|корректор)',
]

END_HALLUCINATION_REGEX = re.compile(
    r'[\s.,!?:;\-\(\)]*(' + '|'.join(HALLUCINATION_PATTERNS) + r')[\s.,!?:;\-\(\)]*$',
    re.IGNORECASE
)
START_HALLUCINATION_REGEX = re.compile(
    r'^[\s.,!?:;\-\(\)]*(' + '|'.join(HALLUCINATION_PATTERNS) + r')[\s.,!?:;\-\(\)]*',
    re.IGNORECASE
)

def clean_hallucinated_subtitles(text):
    if not text:
        return ""
    text_clean = text.strip()
    
    old_len = -1
    while len(text_clean) != old_len and text_clean:
        old_len = len(text_clean)
        if START_HALLUCINATION_REGEX.fullmatch(text_clean) or END_HALLUCINATION_REGEX.fullmatch(text_clean):
            print(f"Filtered out complete Whisper hallucination: '{text_clean}'")
            return ""
        m = END_HALLUCINATION_REGEX.search(text_clean)
        if m:
            stripped = text_clean[:m.start()].strip()
            print(f"Trimmed trailing Whisper hallucination '{m.group(0).strip()}' -> remaining: '{stripped}'")
            text_clean = stripped

    return text_clean

class TranscribeThread(QThread):
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, audio_data, model_size="turbo", language="ru"):
        super().__init__()
        self.audio_data = audio_data
        self.model_size = model_size
        self.language = language

    def run(self):
        try:
            model = get_whisper_model(self.model_size)
            lang_param = None if self.language == "auto" else self.language
            
            # Hyper-Optimized 25x Speed Decoding
            segments, info = model.transcribe(
                self.audio_data, 
                beam_size=1, 
                best_of=1,
                temperature=0.0,
                without_timestamps=True,
                suppress_blank=True,
                condition_on_previous_text=False,
                language=lang_param, 
                initial_prompt=INITIAL_PROMPT,
                vad_filter=True, 
                vad_parameters=dict(
                    min_silence_duration_ms=250,
                    threshold=0.5,
                    min_speech_duration_ms=250
                )
            )
            text_parts = []
            for segment in segments:
                if segment.text:
                    text_parts.append(segment.text.strip())
            
            full_text = " ".join(text_parts).strip()
            full_text = clean_hallucinated_subtitles(full_text)
            self.finished_signal.emit(full_text)
        except Exception as e:
            err_str = traceback.format_exc()
            log_error(f"TranscribeThread crash exception:\n{err_str}")
            self.error_signal.emit(str(e))

class SettingsDialog(QDialog):
    def __init__(self, parent_widget, cfg):
        super().__init__(parent_widget)
        self.cfg = cfg
        self.parent_widget = parent_widget
        self.setWindowTitle("⚙️ Settings / Настройки Whisper Voice AI")
        self.setFixedWidth(480)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 12px;
            }
            QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 5px;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Language selector
        self.lang_combo = QComboBox()
        for label, code in LANGUAGES:
            self.lang_combo.addItem(label, code)
        idx_l = self.lang_combo.findData(self.cfg.get("language", "ru"))
        if idx_l >= 0: self.lang_combo.setCurrentIndex(idx_l)
        form.addRow("🌍 Язык / Language:", self.lang_combo)

        # Hotkey selector
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItem("Колесико мыши (Middle Click)", "middle_click")
        self.hotkey_combo.addItem("Правый Alt (Right Alt)", "right_alt")
        self.hotkey_combo.addItem("Правый Ctrl (Right Ctrl)", "right_ctrl")
        self.hotkey_combo.addItem("Клавиша F9", "f9")
        self.hotkey_combo.addItem("Клавиша F10", "f10")
        
        idx = self.hotkey_combo.findData(self.cfg.get("hotkey", "middle_click"))
        if idx >= 0: self.hotkey_combo.setCurrentIndex(idx)
        form.addRow("⌨️ Кнопка записи:", self.hotkey_combo)

        # Hotkey Mode (Toggle vs Hold)
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Переключение (Клик для нач/конца)", "toggle")
        self.mode_combo.addItem("Удерживание (Hold to talk)", "hold")
        idx_hm = self.mode_combo.findData(self.cfg.get("hotkey_mode", "toggle"))
        if idx_hm >= 0: self.mode_combo.setCurrentIndex(idx_hm)
        form.addRow("🔘 Режим кнопки:", self.mode_combo)

        # Ignore fast middle clicks (protect tab closing)
        self.ignore_fast_chk = QCheckBox("🛡️ Защита колесика от клика по вкладкам")
        self.ignore_fast_chk.setToolTip("Игнорирует быстрые клики колесиком мыши, чтобы не включать запись при закрытии вкладок в браузере")
        self.ignore_fast_chk.setChecked(self.cfg.get("ignore_fast_middle_click", True))
        form.addRow("🌐 Защита вкладок:", self.ignore_fast_chk)

        # Middle click delay threshold (ms)
        self.middle_delay_spin = QSpinBox()
        self.middle_delay_spin.setRange(50, 300)
        self.middle_delay_spin.setSingleStep(10)
        self.middle_delay_spin.setSuffix(" мс")
        self.middle_delay_spin.setValue(self.cfg.get("middle_click_delay_ms", 120))
        form.addRow("⏱️ Задержка колесика мыши:", self.middle_delay_spin)

        # Pause media during recording
        self.pause_media_chk = QCheckBox("⏸️ Авто-пауза воспроизведения аудио/музыки при записи")
        self.pause_media_chk.setChecked(self.cfg.get("pause_media_on_record", True))
        form.addRow("🎵 Пауза медиа:", self.pause_media_chk)

        # Position Mode
        self.pos_combo = QComboBox()
        self.pos_combo.addItem("Верх по центру (Top Center)", "top_center")
        self.pos_combo.addItem("Низ по центру (Bottom Center)", "bottom_center")
        self.pos_combo.addItem("Верх справа (Top Right)", "top_right")
        self.pos_combo.addItem("Запоминать перетаскивание (Custom)", "custom")
        
        idx_p = self.pos_combo.findData(self.cfg.get("position_mode", "top_center"))
        if idx_p >= 0: self.pos_combo.setCurrentIndex(idx_p)
        form.addRow("📍 Размещение виджета:", self.pos_combo)

        # Model Selector with Automatic Warmup Indicator
        self.model_combo = QComboBox()
        self.model_combo.addItem("🚀 Турбо ИИ v3 (turbo) [Гипер-скорость ~0.3s]", "turbo")
        self.model_combo.addItem("⚡ Быстрая (small) [Мгновенно]", "small")
        self.model_combo.addItem("🎯 Точная (medium)", "medium")
        self.model_combo.addItem("🏆 Максимум (large-v3)", "large-v3")
        
        idx_m = self.model_combo.findData(self.cfg.get("model_size", "turbo"))
        if idx_m >= 0: self.model_combo.setCurrentIndex(idx_m)
        form.addRow("🤖 Модель ИИ:", self.model_combo)

        # Model Status Label
        self.model_status_lbl = QLabel("ℹ️ Модель подгрузится при выборе")
        self.model_status_lbl.setStyleSheet("color: #89b4fa; font-style: italic; font-size: 11px;")
        form.addRow("", self.model_status_lbl)

        # Max duration limit (seconds)
        self.max_dur_spin = QSpinBox()
        self.max_dur_spin.setRange(10, 300)
        self.max_dur_spin.setSuffix(" сек")
        self.max_dur_spin.setValue(self.cfg.get("max_duration_sec", 120))
        form.addRow("⏱️ Макс. длительность записи:", self.max_dur_spin)

        # Accidental click protection threshold (seconds)
        self.min_dur_spin = QDoubleSpinBox()
        self.min_dur_spin.setRange(0.1, 2.0)
        self.min_dur_spin.setSingleStep(0.1)
        self.min_dur_spin.setSuffix(" сек")
        self.min_dur_spin.setValue(self.cfg.get("min_duration_sec", 0.2))
        form.addRow("⚡ Защита от коротких кликов:", self.min_dur_spin)

        # Real-time streaming checkbox
        self.realtime_chk = QCheckBox("Печать в реальном времени (Live Streaming - 0ms задержка)")
        self.realtime_chk.setChecked(self.cfg.get("realtime_mode", False))
        form.addRow("⚡ Режим ввода:", self.realtime_chk)

        # Autopaste checkbox
        self.autopaste_chk = QCheckBox("Автоматическая вставка в активное окно")
        self.autopaste_chk.setChecked(self.cfg.get("autopaste", True))
        form.addRow("📋 Буфер / Вставка:", self.autopaste_chk)

        # Silence Check toggle
        self.check_silence_chk = QCheckBox("⚠️ Проверять отключенный микрофон (детекция тишины)")
        self.check_silence_chk.setChecked(self.cfg.get("check_silence", True))
        form.addRow("🎙️ Детекция тишины:", self.check_silence_chk)

        # Save audio logs checkbox
        self.savelogs_chk = QCheckBox("Сохранять аудиозаписи (.wav + .txt) для обучения ИИ")
        self.savelogs_chk.setChecked(self.cfg.get("save_audio_logs", True))
        form.addRow("📁 Локальное сохранение:", self.savelogs_chk)

        # Save Dir widget row
        dir_box = QHBoxLayout()
        self.save_dir_edit = QLineEdit(self.cfg.get("save_audio_dir", "logs/recordings"))
        dir_box.addWidget(self.save_dir_edit)
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.setStyleSheet("padding: 4px 8px; font-size: 11px;")
        browse_btn.clicked.connect(self.browse_save_dir)
        dir_box.addWidget(browse_btn)
        form.addRow("📁 Папка записей:", dir_box)

        open_folder_btn = QPushButton("📂 Открыть папку с записями в Проводнике")
        open_folder_btn.setStyleSheet("background-color: #313244; color: #89b4fa; border: 1px solid #45475a; padding: 6px;")
        open_folder_btn.clicked.connect(self.open_save_dir)
        form.addRow("", open_folder_btn)

        layout.addLayout(form)

        save_btn = QPushButton("💾 Сохранить настройки / Save Settings")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)

    def browse_save_dir(self):
        curr = self.save_dir_edit.text().strip()
        start_dir = curr if os.path.exists(curr) else APP_DIR
        chosen = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения аудиозаписей", start_dir)
        if chosen:
            self.save_dir_edit.setText(chosen)

    def open_save_dir(self):
        raw = self.save_dir_edit.text().strip()
        target = raw if os.path.isabs(raw) else os.path.join(APP_DIR, raw)
        os.makedirs(target, exist_ok=True)
        try:
            os.startfile(target)
        except Exception as e:
            log_error(f"Open dir error: {e}")

    def save_and_close(self):
        new_model = self.model_combo.currentData()
        old_model = self.cfg.get("model_size", "turbo")

        self.cfg["language"] = self.lang_combo.currentData()
        self.cfg["hotkey"] = self.hotkey_combo.currentData()
        self.cfg["hotkey_mode"] = self.mode_combo.currentData()
        self.cfg["ignore_fast_middle_click"] = self.ignore_fast_chk.isChecked()
        self.cfg["middle_click_delay_ms"] = self.middle_delay_spin.value()
        self.cfg["pause_media_on_record"] = self.pause_media_chk.isChecked()
        self.cfg["position_mode"] = self.pos_combo.currentData()
        self.cfg["model_size"] = new_model
        self.cfg["max_duration_sec"] = self.max_dur_spin.value()
        self.cfg["min_duration_sec"] = self.min_dur_spin.value()
        self.cfg["realtime_mode"] = self.realtime_chk.isChecked()
        self.cfg["autopaste"] = self.autopaste_chk.isChecked()
        self.cfg["check_silence"] = self.check_silence_chk.isChecked()
        self.cfg["save_audio_logs"] = self.savelogs_chk.isChecked()
        self.cfg["save_audio_dir"] = self.save_dir_edit.text().strip() or "logs/recordings"
        save_config(self.cfg)

        # Trigger background model warmup if model changed
        if new_model != old_model or new_model not in MODELS:
            if hasattr(self.parent_widget, 'start_model_preloader'):
                self.parent_widget.start_model_preloader(new_model)

        self.accept()

class DictationWidget(QWidget):
    toggle_signal = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.recorder = AudioRecorder()
        self.is_recording = False
        self.is_transcribing = False
        self.is_rt_transcribing = False
        self.last_rt_text = ""
        self.target_hwnd = None
        self.history = []
        self.thread = None
        self.preloader_thread = None
        
        self.audio_file = os.path.join(os.environ.get("TEMP", "."), "dictation_recording.wav")
        self.realtime_file = os.path.join(os.environ.get("TEMP", "."), "dictation_realtime.wav")
        
        self.idle_icon = create_tray_icon_pixmap("#a6e3a1", False)
        self.rec_icon = create_tray_icon_pixmap("#f38ba8", True)
        self.proc_icon = create_tray_icon_pixmap("#f9e2af", False)
        
        self.toggle_signal.connect(self.toggle_recording)
        self.cancel_signal.connect(self.cancel_dictation)
        
        self.stream_timer = QTimer(self)
        self.stream_timer.setInterval(2000)
        self.stream_timer.timeout.connect(self.process_realtime_chunk)

        self.max_recording_timer = QTimer(self)
        self.max_recording_timer.setSingleShot(True)
        self.max_recording_timer.timeout.connect(self.auto_stop_max_duration)

        # Dynamic Watchdog Timer scaling for long recordings
        self.watchdog_timer = QTimer(self)
        self.watchdog_timer.setSingleShot(True)
        self.watchdog_timer.timeout.connect(self.on_watchdog_timeout)
        
        self.last_external_hwnd = None
        self.window_tracker = QTimer(self)
        self.window_tracker.setInterval(150)
        self.window_tracker.timeout.connect(self._track_active_window)
        self.window_tracker.start()

        self.init_ui()
        self.init_tray()
        self.init_listeners()

        # Warmup default configured model in background on startup
        QTimer.singleShot(500, lambda: self.start_model_preloader(self.cfg.get("model_size", "turbo")))

    def start_model_preloader(self, model_size):
        if model_size in MODELS:
            return
        self.status_btn.setText(f"⏳ Загрузка {model_size}...")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #f9e2af;
                color: #11111b;
                border: 1px solid #f9e2af;
                border-radius: 14px;
                padding: 0px 14px;
            }
        """)
        self.preloader_thread = ModelPreloaderThread(model_size)
        self.preloader_thread.finished_signal.connect(self.on_model_preloaded)
        self.preloader_thread.start()

    def on_model_preloaded(self, model_size, success):
        if success:
            self.status_btn.setText(f"✅ {model_size.upper()} Готова!")
            self.status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a6e3a1;
                    color: #11111b;
                    border: 1px solid #a6e3a1;
                    border-radius: 14px;
                    padding: 0px 14px;
                }
            """)
        else:
            self.status_btn.setText(f"⚠️ Ошибка {model_size}")
        QTimer.singleShot(1500, self.reset_btn)

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.pill_bar = QWidget(self)
        self.pill_bar.setObjectName("PillBar")
        self.pill_bar.setStyleSheet("""
            QWidget#PillBar {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 19px;
            }
        """)

        pill_layout = QHBoxLayout(self.pill_bar)
        pill_layout.setContentsMargins(8, 4, 8, 4)
        pill_layout.setSpacing(6)

        self.status_btn = QPushButton("🟢 Надиктовать")
        self.status_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.status_btn.setFixedHeight(30)
        self.status_btn.setMinimumWidth(170)
        self.set_btn_ready_style()
        self.status_btn.clicked.connect(self.toggle_recording)
        pill_layout.addWidget(self.status_btn)

        self.menu_btn = QPushButton("⚙️")
        self.menu_btn.setFixedSize(30, 30)
        self.menu_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #45475a;
                color: #ffffff;
            }
        """)
        self.menu_btn.setToolTip("Настройки / Settings")
        self.menu_btn.clicked.connect(self.open_settings_dialog)
        pill_layout.addWidget(self.menu_btn)

        self.minimize_btn = QPushButton("➖")
        self.minimize_btn.setFixedSize(30, 30)
        self.minimize_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #89b4fa;
                border: 1px solid #45475a;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
                color: #11111b;
            }
        """)
        self.minimize_btn.setToolTip("Свернуть в трей / Minimize to Tray")
        self.minimize_btn.clicked.connect(self.hide_to_tray)
        pill_layout.addWidget(self.minimize_btn)

        self.cancel_btn = QPushButton("❌")
        self.cancel_btn.setFixedSize(30, 30)
        self.cancel_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #f38ba8;
                border: 1px solid #f38ba8;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
        """)
        self.cancel_btn.setToolTip("Отменить запись (ESC)")
        self.cancel_btn.clicked.connect(self.cancel_dictation)
        pill_layout.addWidget(self.cancel_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #a6adc8;
                border: 1px solid #45475a;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
        """)
        self.close_btn.setToolTip("Закрыть / Exit")
        self.close_btn.clicked.connect(QApplication.quit)
        pill_layout.addWidget(self.close_btn)

        outer_layout.addWidget(self.pill_bar)

        self.history_drawer = QWidget()
        self.history_drawer.setObjectName("HistoryDrawer")
        self.history_drawer.setStyleSheet("""
            QWidget#HistoryDrawer {
                background-color: #181825;
                border: 1px solid #45475a;
                border-radius: 14px;
                margin-top: 6px;
            }
        """)
        drawer_layout = QVBoxLayout(self.history_drawer)
        drawer_layout.setContentsMargins(10, 10, 10, 10)
        
        hist_title = QLabel("📜 History / История:")
        hist_title.setStyleSheet("color: #cdd6f4; font-size: 11px; border: none; font-weight: bold;")
        drawer_layout.addWidget(hist_title)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 8px;
            }
            QListWidget::item:hover {
                background-color: #45475a;
            }
        """)
        self.history_list.itemClicked.connect(self.copy_history_item)
        drawer_layout.addWidget(self.history_list)

        self.history_drawer.hide()
        outer_layout.addWidget(self.history_drawer)

        self.setFixedWidth(360)
        self.reposition_window()

    def set_btn_ready_style(self):
        hotkey_str = self.cfg.get("hotkey", "middle_click")
        lang_str = self.cfg.get("language", "ru").upper()
        label = f"🟢 [{lang_str}] Надиктовать"
        if hotkey_str == "middle_click": label += " (Middle)"
        elif hotkey_str == "right_alt": label += " (R-Alt)"
        elif hotkey_str == "right_ctrl": label += " (R-Ctrl)"
        elif hotkey_str == "f9": label += " (F9)"
        elif hotkey_str == "f10": label += " (F10)"
        
        self.status_btn.setText(label)
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e2030;
                color: #a6e3a1;
                border: 1px solid #a6e3a1;
                border-radius: 14px;
                padding: 0px 14px;
            }
            QPushButton:hover {
                background-color: #a6e3a1;
                color: #11111b;
            }
        """)

    def reposition_window(self):
        mode = self.cfg.get("position_mode", "top_center")
        if mode == "custom" and self.cfg.get("custom_x", -1) >= 0 and self.cfg.get("custom_y", -1) >= 0:
            self.move(self.cfg["custom_x"], self.cfg["custom_y"])
            return

        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if not screen:
            screen = QApplication.primaryScreen()
        
        geo = screen.geometry()
        if mode == "bottom_center":
            self.move((geo.x() + (geo.width() - self.width()) // 2), geo.y() + geo.height() - 80)
        elif mode == "top_right":
            self.move(geo.x() + geo.width() - self.width() - 40, geo.y() + 30)
        else: # top_center
            self.move((geo.x() + (geo.width() - self.width()) // 2), geo.y() + 30)

    def open_settings_dialog(self):
        dlg = SettingsDialog(self, self.cfg)
        if dlg.exec():
            self.set_btn_ready_style()
            self.reposition_window()
            self.init_listeners()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(ICON_PATH):
            self.tray_icon.setIcon(QIcon(ICON_PATH))
            self.setWindowIcon(QIcon(ICON_PATH))
        else:
            self.tray_icon.setIcon(self.idle_icon)

        tray_menu = QMenu()
        show_action = QAction("Показать / Скрыть виджет", self)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)

        settings_action = QAction("⚙️ Настройки / Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        tray_menu.addAction(settings_action)

        quit_action = QAction("Выйти из Whisper Voice", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Whisper AI Multilingual Dictation")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def hide_to_tray(self):
        self.hide()
        if hasattr(self, 'tray_icon') and self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                "Whisper Voice AI",
                "Приложение свернуто в трей. Нажмите на иконку в трее, чтобы развернуть.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def on_tray_icon_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle_visibility()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.reposition_window()
            self.show()
            self.activateWindow()

    def init_listeners(self):
        if hasattr(self, 'mouse_listener') and self.mouse_listener:
            try: self.mouse_listener.stop()
            except Exception: pass

        hk = self.cfg.get("hotkey", "middle_click")
        hk_mode = self.cfg.get("hotkey_mode", "toggle")
        ignore_fast = self.cfg.get("ignore_fast_middle_click", True)
        delay_sec = self.cfg.get("middle_click_delay_ms", 120) / 1000.0

        self.middle_press_time = 0.0

        def on_click(x, y, button, pressed):
            if hk == "middle_click" and button == mouse.Button.middle:
                if pressed:
                    self.middle_press_time = time.time()
                else:
                    press_duration = time.time() - getattr(self, 'middle_press_time', 0.0)
                    if self.is_recording:
                        self.toggle_signal.emit()
                    else:
                        if ignore_fast and press_duration < delay_sec:
                            # Ignored quick middle-click (e.g. closing browser tabs)
                            pass
                        else:
                            self.toggle_signal.emit()

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

        try:
            keyboard.unhook_all()
            keyboard.add_hotkey('esc', lambda: self.cancel_signal.emit())
            keyboard.add_hotkey('pause', lambda: convert_current_selection_layout())

            if hk == "right_alt":
                keyboard.add_hotkey('right alt', lambda: self.toggle_signal.emit())
            elif hk == "right_ctrl":
                keyboard.add_hotkey('right ctrl', lambda: self.toggle_signal.emit())
            elif hk == "f9":
                keyboard.add_hotkey('f9', lambda: self.toggle_signal.emit())
            elif hk == "f10":
                keyboard.add_hotkey('f10', lambda: self.toggle_signal.emit())
        except Exception as e:
            print("Hotkey listener error:", e)

    def _track_active_window(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd and hwnd != int(self.winId()):
                self.last_external_hwnd = hwnd
        except Exception:
            pass

    def toggle_recording(self):
        if not self.is_recording and not self.is_transcribing:
            fg = win32gui.GetForegroundWindow()
            if fg and fg != int(self.winId()):
                self.target_hwnd = fg
            else:
                self.target_hwnd = self.last_external_hwnd
            self.start_dictation()
        elif self.is_recording:
            self.stop_dictation()

    def start_dictation(self):
        self.reposition_window()
        self.is_recording = True
        self.is_transcribing = False
        self.is_rt_transcribing = False
        self.last_rt_text = ""
        
        self.was_media_playing = False
        if self.cfg.get("pause_media_on_record", True):
            self.was_media_playing = get_media_playing_state()
            if self.was_media_playing:
                toggle_media_play_pause()
        
        self.tray_icon.setIcon(self.rec_icon)
        self.status_btn.setText("🔴 Идет запись...")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #11111b;
                border: 1px solid #f38ba8;
                border-radius: 14px;
                padding: 0px 14px;
            }
        """)
        self.recorder.start()

        max_sec = self.cfg.get("max_duration_sec", 120)
        self.max_recording_timer.start(max_sec * 1000)

        if self.cfg.get("realtime_mode", False):
            self.stream_timer.start()

    def auto_stop_max_duration(self):
        if self.is_recording:
            print("Max recording duration reached. Auto-stopping...")
            self.stop_dictation()

    def process_realtime_chunk(self):
        if self.is_recording and not self.is_transcribing and not getattr(self, 'is_rt_transcribing', False):
            audio_np = self.recorder.get_numpy_audio()
            if audio_np is not None and len(audio_np) > 0:
                self.is_rt_transcribing = True
                model_size = self.cfg.get("model_size", "turbo")
                lang = self.cfg.get("language", "ru")
                self.rt_thread = TranscribeThread(audio_np, model_size=model_size, language=lang)
                self.rt_thread.finished_signal.connect(self.on_realtime_finished)
                self.rt_thread.error_signal.connect(self.on_realtime_error)
                self.rt_thread.start()

    def on_realtime_error(self, err):
        self.is_rt_transcribing = False

    def on_realtime_finished(self, text):
        self.is_rt_transcribing = False
        if self.is_recording and text:
            # We want to paste only the new words that were recognized
            prev = getattr(self, 'last_rt_text', "")
            
            # Simple diff: if it starts with the previous text, just take the new part
            # Wait, whisper often changes casing or punctuation of the previous text.
            # To be safe, we just strip punctuation and lowercase it to compare, or use a naive approach.
            if len(text) > len(prev):
                # Extremely naive approach for typing into random windows:
                # We can't use backspace safely. So we only append if we find a clear extension.
                if text.lower().startswith(prev.lower()):
                    new_text = text[len(prev):]
                else:
                    # If model rewrote the sentence, it's very hard to fix the window text.
                    # We will just append the difference in length as a raw guess.
                    # This will cause garbage, which is why true realtime into arbitrary windows is hard.
                    # For now, let's just attempt to paste the new suffix.
                    # If we don't have a good match, we just wait until the end.
                    words_new = text.split()
                    words_old = prev.split()
                    if len(words_new) > len(words_old):
                        new_text = " ".join(words_new[len(words_old):])
                    else:
                        new_text = ""
                
                if new_text.strip():
                    if self.cfg.get("autopaste", True):
                        paste_text_to_window(self.target_hwnd, " " + new_text.strip())
            
            self.last_rt_text = text

    def cancel_dictation(self):
        self.stream_timer.stop()
        self.max_recording_timer.stop()
        self.watchdog_timer.stop()
        self.is_recording = False
        self.is_transcribing = False
        self.recorder.cancel()

        if getattr(self, 'was_media_playing', False):
            toggle_media_play_pause()
            self.was_media_playing = False

        if self.thread is not None and self.thread.isRunning():
            try:
                self.thread.terminate()
                self.thread.wait(300)
            except Exception: pass

        self.tray_icon.setIcon(self.idle_icon)
        self.status_btn.setText("🚫 Отменено")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #11111b;
                border: 1px solid #f38ba8;
                border-radius: 14px;
                padding: 0px 14px;
            }
        """)
        QTimer.singleShot(1000, self.reset_btn)

    def stop_dictation(self):
        self.stream_timer.stop()
        self.max_recording_timer.stop()
        self.is_recording = False

        if getattr(self, 'was_media_playing', False):
            toggle_media_play_pause()
            self.was_media_playing = False

        if self.recorder.stream_error:
            print("Audio stream error detected:", self.recorder.stream_error)
            self.recorder.cancel()
            self.status_btn.setText("⚠️ Ошибка микрофона!")
            self.status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f38ba8;
                    color: #11111b;
                    border: 1px solid #f38ba8;
                    border-radius: 14px;
                    padding: 0px 14px;
                }
            """)
            QTimer.singleShot(2500, self.reset_btn)
            return

        duration, mean_rms, max_peak = self.recorder.get_stats()
        self.last_duration = duration
        min_dur = self.cfg.get("min_duration_sec", 0.2)
        silence_thresh = self.cfg.get("silence_rms_threshold", 0.00005)
        check_silence = self.cfg.get("check_silence", True)

        if duration < min_dur:
            print(f"Accidental click detected ({duration:.2f}s < {min_dur}s). Cancelling...")
            self.recorder.cancel()
            self.status_btn.setText("⚡ Слишком коротко")
            QTimer.singleShot(1000, self.reset_btn)
            return

        if check_silence and max_peak < silence_thresh:
            print(f"Silence detected (max peak {max_peak:.6f} < {silence_thresh}). Microphone muted or off.")
            self.recorder.cancel()
            self.status_btn.setText("⚠️ Микрофон молчит / Нет звука")
            self.status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f38ba8;
                    color: #11111b;
                    border: 1px solid #f38ba8;
                    border-radius: 14px;
                    padding: 0px 14px;
                }
            """)
            QTimer.singleShot(2500, self.reset_btn)
            return

        self.is_transcribing = True
        self.tray_icon.setIcon(self.proc_icon)
        self.status_btn.setText("⚡ ИИ-обработка...")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #f9e2af;
                color: #11111b;
                border: 1px solid #f9e2af;
                border-radius: 14px;
                padding: 0px 14px;
            }
        """)

        # Dynamic Watchdog Timer: 30 seconds for long dictations
        watchdog_ms = max(20000, int(duration * 2000))
        self.watchdog_timer.start(watchdog_ms)
        
        audio_np = self.recorder.get_numpy_audio()
        self.recorder.stop(self.audio_file)
        if audio_np is not None and len(audio_np) > 0:
            model_size = self.cfg.get("model_size", "turbo")
            lang = self.cfg.get("language", "ru")
            self.thread = TranscribeThread(audio_np, model_size=model_size, language=lang)
            self.thread.finished_signal.connect(self.on_transcribe_finished)
            self.thread.error_signal.connect(self.on_transcribe_error)
            self.thread.start()
        else:
            self.reset_btn()

    def on_watchdog_timeout(self):
        if self.is_transcribing:
            print("Watchdog timeout triggered! Unfreezing GUI button...")
            if self.thread and self.thread.isRunning():
                try:
                    self.thread.terminate()
                    self.thread.wait(300)
                except Exception: pass
            self.is_transcribing = False
            self.status_btn.setText("⚠️ Таймаут / Попробуйте еще раз")
            QTimer.singleShot(2000, self.reset_btn)

    def on_transcribe_error(self, err):
        self.watchdog_timer.stop()
        self.is_transcribing = False
        self.tray_icon.setIcon(self.idle_icon)
        self.status_btn.setText("⚠️ Ошибка")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #11111b;
                border: 1px solid #f38ba8;
                border-radius: 14px;
                padding: 0px 14px;
            }
        """)
        QTimer.singleShot(2000, self.reset_btn)

    def on_transcribe_finished(self, text):
        self.watchdog_timer.stop()
        self.is_transcribing = False
        if text:
            pyperclip.copy(text)
            self.history.insert(0, text)
            self.history_list.insertItem(0, text)

            if self.cfg.get("save_audio_logs", True):
                try:
                    rel_dir = self.cfg.get("save_audio_dir", "logs/recordings")
                    save_dir = rel_dir if os.path.isabs(rel_dir) else os.path.join(APP_DIR, rel_dir)
                    os.makedirs(save_dir, exist_ok=True)

                    ts_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_wav_path = os.path.join(save_dir, f"audio_{ts_str}.wav")
                    log_txt_path = os.path.join(save_dir, f"audio_{ts_str}.txt")

                    if os.path.exists(self.audio_file):
                        shutil.copy2(self.audio_file, log_wav_path)
                        with open(log_txt_path, "w", encoding="utf-8") as tf:
                            tf.write(text + "\n")

                    history_file = os.path.join(save_dir, "dictation_history.jsonl")
                    log_entry = {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "audio_file": log_wav_path,
                        "transcript_file": log_txt_path,
                        "duration_sec": getattr(self, "last_duration", 0.0),
                        "model_size": self.cfg.get("model_size", "turbo"),
                        "language": self.cfg.get("language", "ru"),
                        "text": text
                    }
                    with open(history_file, "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                    print(f"Saved audio & transcript dataset: {log_wav_path}")
                except Exception as ex:
                    log_error(f"Error saving audio log: {ex}")

            if self.cfg.get("autopaste", True):
                if not self.cfg.get("realtime_mode", False):
                    target = self.target_hwnd if self.target_hwnd else self.last_external_hwnd
                    paste_text_to_window(target, text)
                self.status_btn.setText("🟢 Вставлено!")
            else:
                self.status_btn.setText("📋 В буфере!")

            self.status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a6e3a1;
                    color: #11111b;
                    border: 1px solid #a6e3a1;
                    border-radius: 14px;
                    padding: 0px 14px;
                }
            """)
            QTimer.singleShot(1500, self.reset_btn)
        else:
            self.reset_btn()

    def reset_btn(self):
        self.watchdog_timer.stop()
        self.is_recording = False
        self.is_transcribing = False
        self.tray_icon.setIcon(self.idle_icon)
        self.set_btn_ready_style()

    def copy_history_item(self, item):
        pyperclip.copy(item.text())
        self.status_btn.setText("📋 Скопировано!")
        QTimer.singleShot(1000, self.reset_btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            new_pos = self.pos() + delta
            self.move(new_pos)
            self.old_pos = event.globalPosition().toPoint()
            
            self.cfg["position_mode"] = "custom"
            self.cfg["custom_x"] = self.x()
            self.cfg["custom_y"] = self.y()
            save_config(self.cfg)

if __name__ == "__main__":
    _single_instance_mutex = ensure_single_instance()
    app = QApplication(sys.argv)
    widget = DictationWidget()
    widget.show()
    sys.exit(app.exec())
