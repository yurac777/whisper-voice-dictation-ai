# -*- coding: utf-8 -*-
import sys, os, time, wave, threading, psutil
import sounddevice as sd
import numpy as np
import pyperclip
import win32gui, win32con, win32api
from pynput import mouse
import keyboard

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, 
                             QVBoxLayout, QLabel, QListWidget, QCheckBox, QComboBox,
                             QSystemTrayIcon, QMenu, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QFont, QIcon, QAction, QColor

# Kill previous instances of main.py
def kill_old_instances():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] != current_pid and proc.info['cmdline']:
                cmd = " ".join(proc.info['cmdline'])
                if "main.py" in cmd or "whisper_dictation" in cmd:
                    if proc.info['pid'] != current_pid:
                        print(f"Terminating old process PID {proc.info['pid']}...")
                        proc.kill()
        except Exception:
            pass

kill_old_instances()

from faster_whisper import WhisperModel

MODELS = {}
ICON_PATH = os.path.join(os.path.dirname(__file__), "whisper_icon.ico")

def get_whisper_model(size="small"):
    global MODELS
    if size not in MODELS:
        print(f"Loading faster-whisper '{size}' INT8 model for AMD Ryzen AI...")
        MODELS[size] = WhisperModel(size, device="cpu", compute_type="int8", cpu_threads=10)
        print(f"Model '{size}' loaded successfully!")
    return MODELS[size]

def paste_text_to_window(target_hwnd, text):
    if not text or not target_hwnd:
        return
    try:
        pyperclip.copy(text)
        time.sleep(0.05)
        try:
            win32gui.SetForegroundWindow(target_hwnd)
        except Exception:
            win32gui.ShowWindow(target_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(target_hwnd)
        time.sleep(0.05)

        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
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

    def start(self):
        self.audio_data = []
        self.recording = True
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())
        
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, callback=callback)
        self.stream.start()

    def stop(self, out_filename):
        self.recording = False
        if hasattr(self, 'stream'):
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        
        if not self.audio_data:
            return False
            
        data = np.concatenate(self.audio_data, axis=0)
        data_int16 = (data * 32767).astype(np.int16)
        
        with wave.open(out_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(data_int16.tobytes())
        return True

    def cancel(self):
        self.recording = False
        self.audio_data = []
        if hasattr(self, 'stream'):
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass

class TranscribeThread(QThread):
    finished_signal = pyqtSignal(str)
    
    def __init__(self, audio_file, model_size="small"):
        super().__init__()
        self.audio_file = audio_file
        self.model_size = model_size

    def run(self):
        model = get_whisper_model(self.model_size)
        segments, info = model.transcribe(
            self.audio_file, 
            beam_size=1, 
            language="ru", 
            vad_filter=True, 
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        text = " ".join([segment.text for segment in segments]).strip()
        self.finished_signal.emit(text)

class DictationWidget(QWidget):
    toggle_signal = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.is_recording = False
        self.target_hwnd = None
        self.history = []
        self.audio_file = os.path.join(os.environ.get("TEMP", "."), "dictation_recording.wav")
        
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
        
        # Outer main container layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.setSpacing(0)

        # Sleek Glassmorphic Floating Pill Bar Container
        self.pill_bar = QWidget()
        self.pill_bar.setObjectName("PillBar")
        self.pill_bar.setStyleSheet("""
            QWidget#PillBar {
                background-color: rgba(24, 24, 37, 0.95);
                border: 1px solid rgba(137, 180, 250, 0.4);
                border-radius: 20px;
            }
        """)

        # Drop shadow for float depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffsetY(6)
        self.pill_bar.setGraphicsEffect(shadow)

        pill_layout = QHBoxLayout(self.pill_bar)
        pill_layout.setContentsMargins(10, 5, 10, 5)
        pill_layout.setSpacing(6)

        # 1. Record / Stop Pill Button
        self.status_btn = QPushButton("🖱️ Колесико: Запись")
        self.status_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.status_btn.setFixedHeight(28)
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #89b4fa;
                border-radius: 14px;
                padding: 0px 12px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        self.status_btn.clicked.connect(self.toggle_recording)
        pill_layout.addWidget(self.status_btn)

        # 2. Cancel Button
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.cancel_btn.setFixedHeight(28)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #f38ba8;
                border: 1px solid #f38ba8;
                border-radius: 14px;
                padding: 0px 10px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_dictation)
        pill_layout.addWidget(self.cancel_btn)

        # 3. Auto-Paste Toggle Button (Sleek custom styled)
        self.autopaste_btn = QPushButton("⚡ В окно: ВКЛ")
        self.autopaste_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.autopaste_btn.setFixedHeight(28)
        self.autopaste_enabled = True
        self.autopaste_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #a6e3a1;
                border: 1px solid #a6e3a1;
                border-radius: 14px;
                padding: 0px 10px;
            }
            QPushButton:hover {
                background-color: #a6e3a1;
                color: #11111b;
            }
        """)
        self.autopaste_btn.clicked.connect(self.toggle_autopaste)
        pill_layout.addWidget(self.autopaste_btn)

        # 4. History Button
        self.history_btn = QPushButton("📋 История")
        self.history_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.history_btn.setFixedHeight(28)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cba6f7;
                border: 1px solid #cba6f7;
                border-radius: 14px;
                padding: 0px 10px;
            }
            QPushButton:hover {
                background-color: #cba6f7;
                color: #11111b;
            }
        """)
        self.history_btn.clicked.connect(self.toggle_history_drawer)
        pill_layout.addWidget(self.history_btn)

        # 5. Model Selector Combo
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Быстрый (small)", "Точный (medium)"])
        self.model_combo.setFixedHeight(28)
        self.model_combo.setFont(QFont("Segoe UI", 8))
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                color: #89dceb;
                border: 1px solid #89dceb;
                border-radius: 14px;
                padding: 0px 8px;
            }
            QComboBox::drop-down {
                border: none;
                width: 15px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e2e;
                color: #cdd6f4;
                selection-background-color: #45475a;
                border: 1px solid #89dceb;
            }
        """)
        pill_layout.addWidget(self.model_combo)

        # 6. Circular Close Button (X)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #f38ba8;
                border: 1px solid #f38ba8;
                border-radius: 13px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #11111b;
            }
        """)
        self.close_btn.setToolTip("Выйти из приложения")
        self.close_btn.clicked.connect(QApplication.quit)
        pill_layout.addWidget(self.close_btn)

        outer_layout.addWidget(self.pill_bar)

        # History Drawer Widget (Hidden by default, expands nicely)
        self.history_drawer = QWidget()
        self.history_drawer.setObjectName("HistoryDrawer")
        self.history_drawer.setStyleSheet("""
            QWidget#HistoryDrawer {
                background-color: rgba(24, 24, 37, 0.95);
                border: 1px solid #45475a;
                border-radius: 14px;
                margin-top: 6px;
            }
        """)
        drawer_layout = QVBoxLayout(self.history_drawer)
        drawer_layout.setContentsMargins(8, 8, 8, 8)
        
        hist_title = QLabel("📋 История надиктованного текста (клик для копирования):")
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
                padding: 4px 6px;
            }
            QListWidget::item:hover {
                background-color: #45475a;
            }
        """)
        self.history_list.itemClicked.connect(self.copy_history_item)
        drawer_layout.addWidget(self.history_list)

        self.history_drawer.hide()
        outer_layout.addWidget(self.history_drawer)

        # Screen Top-Center Position
        screen = QApplication.primaryScreen().geometry()
        self.setFixedWidth(610)
        self.move((screen.width() - 610) // 2, 35)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(ICON_PATH):
            self.tray_icon.setIcon(QIcon(ICON_PATH))
            self.setWindowIcon(QIcon(ICON_PATH))

        tray_menu = QMenu()
        show_action = QAction("Показать / Скрыть виджет", self)
        show_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(show_action)

        quit_action = QAction("Выйти из Whisper Voice", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Whisper AI Голосовой Ввод (AMD Ryzen AI)")
        self.tray_icon.show()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()

    def toggle_autopaste(self):
        self.autopaste_enabled = not self.autopaste_enabled
        if self.autopaste_enabled:
            self.autopaste_btn.setText("⚡ В окно: ВКЛ")
            self.autopaste_btn.setStyleSheet("""
                QPushButton {
                    background-color: #313244;
                    color: #a6e3a1;
                    border: 1px solid #a6e3a1;
                    border-radius: 14px;
                    padding: 0px 10px;
                }
                QPushButton:hover {
                    background-color: #a6e3a1;
                    color: #11111b;
                }
            """)
        else:
            self.autopaste_btn.setText("📋 В буфер: ВКЛ")
            self.autopaste_btn.setStyleSheet("""
                QPushButton {
                    background-color: #313244;
                    color: #f9e2af;
                    border: 1px solid #f9e2af;
                    border-radius: 14px;
                    padding: 0px 10px;
                }
                QPushButton:hover {
                    background-color: #f9e2af;
                    color: #11111b;
                }
            """)

    def init_listeners(self):
        def on_click(x, y, button, pressed):
            if button == mouse.Button.middle and pressed:
                self.toggle_signal.emit()

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.mouse_listener.start()

        try:
            keyboard.add_hotkey('esc', lambda: self.cancel_signal.emit() if self.is_recording else None)
        except Exception as e:
            print("ESC listener error:", e)

    def toggle_recording(self):
        if not self.is_recording:
            self.target_hwnd = win32gui.GetForegroundWindow()
            self.start_dictation()
        else:
            self.stop_dictation()

    def start_dictation(self):
        self.is_recording = True
        self.status_btn.setText("🔴 Идет запись...")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #11111b;
                border: 1px solid #f38ba8;
                border-radius: 14px;
                padding: 0px 12px;
            }
        """)
        self.recorder.start()

    def cancel_dictation(self):
        if self.is_recording:
            self.recorder.cancel()
            self.is_recording = False
            self.status_btn.setText("🚫 Отменено")
            self.status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f38ba8;
                    color: #11111b;
                    border: 1px solid #f38ba8;
                    border-radius: 14px;
                    padding: 0px 12px;
                }
            """)
            QTimer.singleShot(1200, self.reset_btn)

    def stop_dictation(self):
        self.is_recording = False
        self.status_btn.setText("⚡ Распознавание ИИ...")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #f9e2af;
                color: #11111b;
                border: 1px solid #f9e2af;
                border-radius: 14px;
                padding: 0px 12px;
            }
        """)
        
        has_data = self.recorder.stop(self.audio_file)
        if has_data:
            model_choice = "small" if self.model_combo.currentIndex() == 0 else "medium"
            self.thread = TranscribeThread(self.audio_file, model_size=model_choice)
            self.thread.finished_signal.connect(self.on_transcribe_finished)
            self.thread.start()
        else:
            self.reset_btn()

    def on_transcribe_finished(self, text):
        if text:
            print("Recognized Text:", text)
            pyperclip.copy(text)
            
            self.history.insert(0, text)
            self.history_list.insertItem(0, text)
            
            if self.autopaste_enabled:
                paste_text_to_window(self.target_hwnd, text)
                self.status_btn.setText("🟢 Вставлено в окно!")
            else:
                self.status_btn.setText("📋 В буфере обмена!")

            self.status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a6e3a1;
                    color: #11111b;
                    border: 1px solid #a6e3a1;
                    border-radius: 14px;
                    padding: 0px 12px;
                }
            """)
            QTimer.singleShot(1500, self.reset_btn)
        else:
            self.reset_btn()

    def reset_btn(self):
        self.status_btn.setText("🖱️ Колесико: Запись")
        self.status_btn.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #89b4fa;
                border-radius: 14px;
                padding: 0px 12px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)

    def toggle_history_drawer(self):
        if self.history_drawer.isVisible():
            self.history_drawer.hide()
            self.adjustSize()
        else:
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
