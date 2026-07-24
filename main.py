# -*- coding: utf-8 -*-
import sys, os, time, wave, threading, psutil, subprocess
import sounddevice as sd
import numpy as np
import pyperclip
import win32gui, win32con, win32api, win32process
from pynput import mouse
import keyboard

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, 
                             QVBoxLayout, QLabel, QListWidget, QComboBox,
                             QSystemTrayIcon, QMenu)
from PyQt6.QtGui import QFont, QIcon, QAction, QColor, QPixmap, QPainter, QBrush, QPen, QCursor

from faster_whisper import WhisperModel

MODELS = {}
PROJ_DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(PROJ_DIR, "whisper_icon.ico")

INITIAL_PROMPT = "Привет! Это диктовка: GitHub, Python, Docker, API, Telegram, Wi-Fi, Windows, ChatGPT, YouTube, OpenWrt, SSD."

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
    
    # Outer Glow Ring
    painter.setBrush(QBrush(QColor(color_hex)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    
    # Inner Mic Dot
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
            print("Converted layout for selected text:", converted)
    except Exception as e:
        print("Layout conversion error:", e)

def get_whisper_model(size="small"):
    global MODELS
    if size not in MODELS:
        print(f"Loading Western OpenAI Whisper model '{size}'...")
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
        
        if current_thread != target_thread:
            win32process.AttachThreadInput(current_thread, target_thread, True)

        try:
            win32gui.ShowWindow(target_hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(target_hwnd)
            win32gui.BringWindowToTop(target_hwnd)
        except Exception:
            pass
            
        if current_thread != target_thread:
            win32process.AttachThreadInput(current_thread, target_thread, False)

        time.sleep(0.1)

        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)

        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.03)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        print("Pasted directly into target window!")
    except Exception as e:
        print("Error pasting text:", e)

class AudioRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        self.record_thread = None

    def _record_loop(self):
        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32') as stream:
                while self.recording:
                    data, _ = stream.read(1024)
                    if self.recording and len(data) > 0:
                        self.audio_data.append(data.copy())
        except Exception as e:
            print("Recording loop error:", e)

    def start(self):
        self.audio_data = []
        self.recording = True
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()

    def stop(self, out_filename):
        self.recording = False
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=1.0)
        
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
            print("Error writing WAV file:", e)
            return False

    def cancel(self):
        self.recording = False
        self.audio_data = []
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=0.5)

class TranscribeThread(QThread):
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, audio_file, model_size="small"):
        super().__init__()
        self.audio_file = audio_file
        self.model_size = model_size

    def run(self):
        try:
            model = get_whisper_model(self.model_size)
            segments, info = model.transcribe(
                self.audio_file, 
                beam_size=1, 
                best_of=1,
                temperature=0.0,
                condition_on_previous_text=False,
                language="ru", 
                initial_prompt=INITIAL_PROMPT,
                vad_filter=True, 
                vad_parameters=dict(min_silence_duration_ms=400)
            )
            text = " ".join([segment.text for segment in segments]).strip()
            self.finished_signal.emit(text)
        except Exception as e:
            print("Transcription thread error:", e)
            self.error_signal.emit(str(e))

class DictationWidget(QWidget):
    toggle_signal = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.is_recording = False
        self.is_transcribing = False
        self.target_hwnd = None
        self.history = []
        self.thread = None
        self.autopaste_enabled = True
        self.current_model = "small"
        self.audio_file = os.path.join(os.environ.get("TEMP", "."), "dictation_recording.wav")
        
        self.idle_icon = create_tray_icon_pixmap("#89b4fa", False)
        self.rec_icon = create_tray_icon_pixmap("#f38ba8", True)
        self.proc_icon = create_tray_icon_pixmap("#f9e2af", False)
        
        self.toggle_signal.connect(self.toggle_recording)
        self.cancel_signal.connect(self.cancel_dictation)
        
        self.init_ui()
        self.init_tray()
        self.init_listeners()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Ultra-Minimalist Glassmorphic Pill Bar
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

        # 1. Main Status & Record Button
        self.status_btn = QPushButton("🔴 Запись (Колесико)")
        self.status_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.status_btn.setFixedHeight(30)
        self.status_btn.setMinimumWidth(180)
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #89b4fa;
                border: 1px solid #89b4fa;
                border-radius: 14px;
                padding: 0px 14px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
                color: #11111b;
            }
        """)
        self.status_btn.clicked.connect(self.toggle_recording)
        pill_layout.addWidget(self.status_btn)

        # 2. Popup Settings & Tools Button (⚙️)
        self.menu_btn = QPushButton("⚙️")
        self.menu_btn.setFixedSize(30, 30)
        self.menu_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #45475a;
                color: #ffffff;
            }
        """)
        self.menu_btn.setToolTip("Настройки и инструменты")
        self.menu_btn.clicked.connect(self.show_tools_menu)
        pill_layout.addWidget(self.menu_btn)

        # 3. Cancel Button (❌)
        self.cancel_btn = QPushButton("❌")
        self.cancel_btn.setFixedSize(30, 30)
        self.cancel_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #f38ba8;
                border: 1px solid #f38ba8;
                border-radius: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
        """)
        self.cancel_btn.setToolTip("Отменить текущую запись / распознавание (ESC)")
        self.cancel_btn.clicked.connect(self.cancel_dictation)
        pill_layout.addWidget(self.cancel_btn)

        # 4. Circular Close Button (✕)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #a6adc8;
                border: 1px solid #45475a;
                border-radius: 14px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
        """)
        self.close_btn.setToolTip("Закрыть программу")
        self.close_btn.clicked.connect(QApplication.quit)
        pill_layout.addWidget(self.close_btn)

        outer_layout.addWidget(self.pill_bar)

        # Hidden History Drawer Widget
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
        
        hist_title = QLabel("📜 История надиктованного текста (клик для копирования):")
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
            QListWidget::item {
                padding: 5px 8px;
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
        self.move_to_active_monitor()

    def move_to_active_monitor(self):
        # Dynamic active monitor positioning based on cursor location!
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if not screen:
            screen = QApplication.primaryScreen()
        
        geo = screen.geometry()
        self.move((geo.x() + (geo.width() - self.width()) // 2), geo.y() + 30)

    def show_tools_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #45475a;
                color: #ffffff;
            }
        """)

        # Action 1: Layout Convert
        act_layout = QAction("🌐 EN ↔ RU Раскладка (Pause)", self)
        act_layout.triggered.connect(convert_current_selection_layout)
        menu.addAction(act_layout)

        # Action 2: Toggle Autopaste
        paste_mode_str = "⚡ Вставка в окно: ВКЛ" if self.autopaste_enabled else "📋 Режим: В буфер"
        act_paste = QAction(paste_mode_str, self)
        act_paste.triggered.connect(self.toggle_autopaste)
        menu.addAction(act_paste)

        # Action 3: History Drawer
        act_hist = QAction("📜 Показать Историю", self)
        act_hist.triggered.connect(self.toggle_history_drawer)
        menu.addAction(act_hist)

        menu.addSeparator()

        # Action 4: Select Small Model
        act_m1 = QAction("⚡ Модель: Быстрая (small)" + (" (✓)" if self.current_model == "small" else ""), self)
        act_m1.triggered.connect(lambda: self.set_model("small"))
        menu.addAction(act_m1)

        # Action 5: Select Medium Model
        act_m2 = QAction("🎯 Модель: Точная (medium)" + (" (✓)" if self.current_model == "medium" else ""), self)
        act_m2.triggered.connect(lambda: self.set_model("medium"))
        menu.addAction(act_m2)

        # Action 6: Select Large Model
        act_m3 = QAction("🚀 Модель: Макс (large-v3)" + (" (✓)" if self.current_model == "large-v3" else ""), self)
        act_m3.triggered.connect(lambda: self.set_model("large-v3"))
        menu.addAction(act_m3)

        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def set_model(self, model_name):
        self.current_model = model_name
        print("Selected model:", model_name)

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

        quit_action = QAction("Выйти из Whisper Voice", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Whisper AI Голосовой Ввод")
        self.tray_icon.show()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.move_to_active_monitor()
            self.show()
            self.activateWindow()

    def toggle_autopaste(self):
        self.autopaste_enabled = not self.autopaste_enabled
        print("Autopaste enabled:", self.autopaste_enabled)

    def init_listeners(self):
        def on_click(x, y, button, pressed):
            if button == mouse.Button.middle and pressed:
                self.toggle_signal.emit()

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

        try:
            keyboard.add_hotkey('esc', lambda: self.cancel_signal.emit())
            keyboard.add_hotkey('pause', lambda: convert_current_selection_layout())
        except Exception as e:
            print("Hotkey listener error:", e)

    def toggle_recording(self):
        if not self.is_recording and not self.is_transcribing:
            self.target_hwnd = win32gui.GetForegroundWindow()
            self.start_dictation()
        elif self.is_recording:
            self.stop_dictation()

    def start_dictation(self):
        self.move_to_active_monitor()
        self.is_recording = True
        self.tray_icon.setIcon(self.rec_icon)
        self.status_btn.setText("🔴 Запись...")
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

    def cancel_dictation(self):
        print("CANCEL DICTATION CALLED!")
        if self.is_recording:
            self.recorder.cancel()
            self.is_recording = False
        
        if self.is_transcribing and self.thread is not None:
            try:
                self.thread.terminate()
                self.thread.wait(500)
            except Exception as e:
                print("Thread terminate exception:", e)
            self.is_transcribing = False

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
        QTimer.singleShot(1200, self.reset_btn)

    def stop_dictation(self):
        self.is_recording = False
        self.is_transcribing = True
        self.tray_icon.setIcon(self.proc_icon)
        self.status_btn.setText("⚡ Распознавание...")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #f9e2af;
                color: #11111b;
                border: 1px solid #f9e2af;
                border-radius: 14px;
                padding: 0px 14px;
            }
        """)
        
        has_data = self.recorder.stop(self.audio_file)
        if has_data:
            self.thread = TranscribeThread(self.audio_file, model_size=self.current_model)
            self.thread.finished_signal.connect(self.on_transcribe_finished)
            self.thread.error_signal.connect(self.on_transcribe_error)
            self.thread.start()
        else:
            self.reset_btn()

    def on_transcribe_error(self, err):
        self.is_transcribing = False
        print("Transcription Error caught gracefully:", err)
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
        self.is_transcribing = False
        if text:
            print("Recognized Text:", text)
            pyperclip.copy(text)
            
            self.history.insert(0, text)
            self.history_list.insertItem(0, text)
            
            if self.autopaste_enabled:
                paste_text_to_window(self.target_hwnd, text)
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
        self.is_recording = False
        self.is_transcribing = False
        self.tray_icon.setIcon(self.idle_icon)
        self.status_btn.setText("🔴 Запись (Колесико)")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2b3d;
                color: #89b4fa;
                border: 1px solid #89b4fa;
                border-radius: 14px;
                padding: 0px 14px;
            }
            QPushButton:hover {
                background-color: #89b4fa;
                color: #11111b;
            }
        """)

    def toggle_history_drawer(self):
        if self.history_drawer.isVisible():
            self.history_drawer.hide()
            self.setFixedWidth(320)
            self.adjustSize()
        else:
            self.setFixedWidth(500)
            self.history_drawer.show()
            self.adjustSize()

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
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = DictationWidget()
    widget.show()
    sys.exit(app.exec())
