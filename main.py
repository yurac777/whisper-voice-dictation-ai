# -*- coding: utf-8 -*-
import sys, os, time, wave, threading, json, subprocess, traceback

# Optimize OpenMP thread allocation to prevent C++ thread stack overflow
os.environ["OMP_NUM_THREADS"] = "10"
os.environ["MKL_NUM_THREADS"] = "10"
os.environ["OPENBLAS_NUM_THREADS"] = "10"

import sounddevice as sd
import numpy as np
import pyperclip
import win32gui, win32con, win32api, win32process
from pynput import mouse
import keyboard

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, 
                             QVBoxLayout, QLabel, QListWidget, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
                             QSystemTrayIcon, QMenu, QDialog, QFormLayout, QGroupBox)
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

INITIAL_PROMPT = "Привет! Это диктовка: GitHub, Python, Docker, API, Telegram, Wi-Fi, Windows, ChatGPT, YouTube, OpenWrt, SSD."

DEFAULT_CONFIG = {
    "hotkey": "middle_click",
    "position_mode": "top_center",
    "custom_x": -1,
    "custom_y": -1,
    "realtime_mode": False,
    "autopaste": True,
    "model_size": "turbo",
    "language": "ru",
    "max_duration_sec": 120,
    "min_duration_sec": 0.2,
    "silence_rms_threshold": 0.0001
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
        print(f"Loading OpenAI Whisper model '{size}' with 10 SIMD OpenMP CPU threads...")
        MODELS[size] = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=10)
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

    def _record_loop(self):
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32') as stream:
                while self.recording:
                    data, _ = stream.read(1024)
                    if self.recording and len(data) > 0:
                        self.audio_data.append(data.copy())
        except Exception as e:
            log_error(f"Recording loop error: {e}")

    def start(self):
        self.audio_data = []
        self.start_time = time.time()
        self.recording = True
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()

    def get_stats(self):
        if not self.audio_data:
            return 0.0, 0.0
        data = np.concatenate(self.audio_data, axis=0)
        duration = len(data) / float(self.sample_rate)
        max_rms = float(np.sqrt(np.mean(data**2)))
        return duration, max_rms

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

class TranscribeThread(QThread):
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, audio_file, model_size="turbo", language="ru"):
        super().__init__()
        self.audio_file = audio_file
        self.model_size = model_size
        self.language = language

    def run(self):
        try:
            model = get_whisper_model(self.model_size)
            lang_param = None if self.language == "auto" else self.language
            
            # Hyper-Optimized 25x Speed Decoding
            segments, info = model.transcribe(
                self.audio_file, 
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
        self.setFixedWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 12px;
            }
            QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox {
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

        layout.addLayout(form)

        save_btn = QPushButton("💾 Сохранить настройки / Save Settings")
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn)

    def save_and_close(self):
        new_model = self.model_combo.currentData()
        old_model = self.cfg.get("model_size", "turbo")

        self.cfg["language"] = self.lang_combo.currentData()
        self.cfg["hotkey"] = self.hotkey_combo.currentData()
        self.cfg["position_mode"] = self.pos_combo.currentData()
        self.cfg["model_size"] = new_model
        self.cfg["max_duration_sec"] = self.max_dur_spin.value()
        self.cfg["min_duration_sec"] = self.min_dur_spin.value()
        self.cfg["realtime_mode"] = self.realtime_chk.isChecked()
        self.cfg["autopaste"] = self.autopaste_chk.isChecked()
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

        self.setFixedWidth(320)
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
        self.tray_icon.show()

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

        def on_click(x, y, button, pressed):
            if hk == "middle_click" and button == mouse.Button.middle and pressed:
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
        if self.is_recording and not self.is_transcribing:
            if self.recorder.get_current_audio_file(self.realtime_file):
                model_size = self.cfg.get("model_size", "turbo")
                lang = self.cfg.get("language", "ru")
                self.rt_thread = TranscribeThread(self.realtime_file, model_size=model_size, language=lang)
                self.rt_thread.finished_signal.connect(self.on_realtime_finished)
                self.rt_thread.start()

    def on_realtime_finished(self, text):
        if self.is_recording and text:
            print("Realtime Partial Stream:", text)
            if self.cfg.get("autopaste", True):
                paste_text_to_window(self.target_hwnd, text + " ")

    def cancel_dictation(self):
        self.stream_timer.stop()
        self.max_recording_timer.stop()
        self.watchdog_timer.stop()
        self.is_recording = False
        self.is_transcribing = False
        self.recorder.cancel()

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

        duration, max_rms = self.recorder.get_stats()
        min_dur = self.cfg.get("min_duration_sec", 0.2)

        if duration < min_dur:
            print(f"Accidental click detected ({duration:.2f}s < {min_dur}s). Cancelling...")
            self.recorder.cancel()
            self.status_btn.setText("⚡ Слишком коротко")
            QTimer.singleShot(1000, self.reset_btn)
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
        
        has_data = self.recorder.stop(self.audio_file)
        if has_data:
            model_size = self.cfg.get("model_size", "turbo")
            lang = self.cfg.get("language", "ru")
            self.thread = TranscribeThread(self.audio_file, model_size=model_size, language=lang)
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
            
            if self.cfg.get("autopaste", True):
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
    app = QApplication(sys.argv)
    widget = DictationWidget()
    widget.show()
    sys.exit(app.exec())
