#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI v7.1 - Fixed Size Window with Auto-Scaling UI
Copyright (c) 2026 NotY215

Features:
- Fixed initial window size (1200x800)
- Only maximize and minimize (no manual resize)
- Automatic UI scaling when maximized
- All buttons and elements scale proportionally
- Professional modern design
"""

import os
import sys
import json
import sqlite3
import tempfile
import subprocess
import shutil
import hashlib
import time
import warnings
import re
import glob
from pathlib import Path
from datetime import timedelta
from threading import Thread, Lock
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from functools import partial

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TORCH_USE_RTLD_GLOBAL'] = '1'
os.environ['OMP_NUM_THREADS'] = '4'

# Set paths for packaged mode
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
    PACKAGES_DIR = BASE_DIR / '_pythonPackages_'
    if PACKAGES_DIR.exists():
        sys.path.insert(0, str(PACKAGES_DIR))
else:
    BASE_DIR = Path(__file__).parent

# App paths
APP_DATA_DIR = Path(os.environ.get('APPDATA', Path.home())) / 'NotYCaptionGenAI'
MODELS_DIR = APP_DATA_DIR / 'models'
LOGS_DIR = APP_DATA_DIR / 'logs'
CACHE_DB = APP_DATA_DIR / 'cache.db'
FFMPEG_DIR = BASE_DIR / 'ffmpeg'
PRETRAINED_MODELS_DIR = BASE_DIR / 'pretrained_models'

# Create directories
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Add FFmpeg to PATH
if FFMPEG_DIR.exists():
    os.environ['PATH'] = str(FFMPEG_DIR) + os.pathsep + os.environ['PATH']

# Try to import PyQt5 with fallback to CLI
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QFileDialog, QComboBox, QTextEdit, QSlider,
        QProgressBar, QGroupBox, QCheckBox, QSpinBox, QLineEdit, QDialog,
        QDialogButtonBox, QTabWidget, QMessageBox, QFrame, QScrollArea,
        QGridLayout, QSplitter, QStackedWidget, QToolTip, QSizePolicy
    )
    from PyQt5.QtCore import (
        Qt, QThread, pyqtSignal, QTimer, QUrl, QSettings, QSize, QPropertyAnimation,
        QEasingCurve, QPoint, QRect, QParallelAnimationGroup, QSequentialAnimationGroup
    )
    from PyQt5.QtGui import (
        QFont, QIcon, QPalette, QColor, QLinearGradient, QBrush, QPainter,
        QPen, QFontDatabase, QMovie, QPixmap, QPainterPath, QRegion, QResizeEvent
    )
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("PyQt5 not available. Falling back to CLI mode.")


# ============================================================================
# CLI MODE (Fallback when GUI not available)
# ============================================================================

class Colors:
    """ANSI color codes for console output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ProgressBar:
    """Simple progress bar for console"""
    def __init__(self, total: int, prefix: str = '', suffix: str = '', length: int = 50):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.current = 0
        
    def update(self, current: int = None):
        if current is not None:
            self.current = current
        else:
            self.current += 1
        percent = 100 * (self.current / float(self.total))
        filled = int(self.length * self.current // self.total)
        bar = '█' * filled + '░' * (self.length - filled)
        print(f'\r{self.prefix} |{bar}| {percent:.1f}% {self.suffix}', end='')
        
    def finish(self):
        self.update(self.total)
        print()


class CacheManager:
    """SQLite cache manager for transcriptions"""
    def __init__(self, db_path: Path = CACHE_DB):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    model TEXT NOT NULL,
                    language TEXT NOT NULL,
                    task TEXT NOT NULL,
                    segments TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
    def get(self, file_path: Path, model: str, language: str, task: str) -> Optional[List[Dict]]:
        file_hash = self._get_file_hash(file_path)
        cache_id = f"{file_hash}_{model}_{language}_{task}"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT segments FROM transcriptions WHERE id = ?', (cache_id,))
            row = cursor.fetchone()
        return json.loads(row[0]) if row else None
        
    def set(self, file_path: Path, model: str, language: str, task: str, segments: List[Dict]):
        file_hash = self._get_file_hash(file_path)
        cache_id = f"{file_hash}_{model}_{language}_{task}"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT OR REPLACE INTO transcriptions VALUES (?, ?, ?, ?, ?, ?, datetime("now"))',
                        (cache_id, file_hash, model, language, task, json.dumps(segments)))
                        
    def _get_file_hash(self, file_path: Path) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()


class Transcriber:
    """Handles Whisper transcription"""
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.model = None
        self.model_name = None
        
    def load_model(self, model_name: str):
        if self.model_name == model_name and self.model is not None:
            return
        try:
            import whisper
            model_path = MODELS_DIR / f"{model_name}.pt"
            if not model_path.exists():
                print(f"Downloading {model_name} model...")
            self.model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
            self.model_name = model_name
        except ImportError:
            raise RuntimeError("Whisper not installed. Run: pip install openai-whisper")
            
    def transcribe(self, audio_path: Path, language: str, task: str = 'transcribe', 
                   use_cache: bool = True, progress_callback=None) -> List[Dict]:
        if use_cache:
            cached = self.cache_manager.get(audio_path, self.model_name, language, task)
            if cached:
                return cached
        if progress_callback:
            progress_callback(10, "Loading audio...")
        options = {'language': language, 'task': task, 'verbose': False, 'fp16': False, 'word_timestamps': True}
        if progress_callback:
            progress_callback(30, "Transcribing...")
        result = self.model.transcribe(str(audio_path), **options)
        segments = [{'start': seg['start'], 'end': seg['end'], 'text': seg['text'].strip(), 
                    'words': seg.get('words', [])} for seg in result['segments']]
        if use_cache:
            self.cache_manager.set(audio_path, self.model_name, language, task, segments)
        if progress_callback:
            progress_callback(100, "Complete")
        return segments


class SubtitleGenerator:
    def __init__(self, break_type: str = 'auto', word_limit: int = 10, char_limit: int = 40):
        self.break_type = break_type
        self.word_limit = word_limit
        self.char_limit = char_limit
        
    def generate_srt(self, segments: List[Dict]) -> str:
        subtitles = []
        for i, seg in enumerate(segments, 1):
            text = self._apply_breaks(seg['text'])
            start = self._format_time_srt(seg['start'])
            end = self._format_time_srt(seg['end'])
            subtitles.append(f"{i}\n{start} --> {end}\n{text}\n")
        return '\n'.join(subtitles)
        
    def _apply_breaks(self, text: str) -> str:
        if self.break_type == 'words':
            words = text.split()
            lines = [' '.join(words[i:i+self.word_limit]) for i in range(0, len(words), self.word_limit)]
            return '\\N'.join(lines)
        elif self.break_type == 'letters':
            lines = [text[i:i+self.char_limit] for i in range(0, len(text), self.char_limit)]
            return '\\N'.join(lines)
        else:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            lines = []
            for i in range(0, len(sentences), 3):
                lines.append(' '.join(sentences[i:i+3]))
            return '\\N'.join(lines)
            
    def _format_time_srt(self, seconds: float) -> str:
        td = timedelta(seconds=seconds)
        return f"{td.seconds//3600:02d}:{(td.seconds%3600)//60:02d}:{td.seconds%60:02d},{int((seconds%1)*1000):03d}"


# ============================================================================
# GUI MODE (Fixed Size Window with Auto-Scaling)
# ============================================================================

if GUI_AVAILABLE:
    
    class ScalableAnimatedButton(QPushButton):
        """Button that scales proportionally with window size"""
        
        def __init__(self, text, color_start="#FF6B35", color_end="#F7931E", parent=None, base_height=40):
            super().__init__(text, parent)
            self.color_start = color_start
            self.color_end = color_end
            self.base_height = base_height
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(150)
            self.setCursor(Qt.PointingHandCursor)
            self._setup_style()
            
        def _setup_style(self):
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.color_start}, stop:1 {self.color_end});
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self._adjust_brightness(self.color_start, 1.1)},
                        stop:1 {self._adjust_brightness(self.color_end, 1.1)});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self._adjust_brightness(self.color_start, 0.8)},
                        stop:1 {self._adjust_brightness(self.color_end, 0.8)});
                }}
                QPushButton:disabled {{
                    background: #555555;
                    color: #888888;
                }}
            """)
            
        def _adjust_brightness(self, color, factor):
            r = int(int(color[1:3], 16) * factor)
            g = int(int(color[3:5], 16) * factor)
            b = int(int(color[5:7], 16) * factor)
            return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"
            
        def resize_to_scale(self, scale_factor):
            """Resize button based on scale factor"""
            new_height = int(self.base_height * scale_factor)
            self.setMinimumHeight(new_height)
            self.setMaximumHeight(new_height)
            font = self.font()
            font.setPointSize(int(14 * scale_factor))
            self.setFont(font)
            
        def enterEvent(self, event):
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(self.x()-2, self.y()-2, self.width()+4, self.height()+4))
            self.animation.start()
            super().enterEvent(event)
            
        def leaveEvent(self, event):
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(self.x()+2, self.y()+2, self.width()-4, self.height()-4))
            self.animation.start()
            super().leaveEvent(event)
    
    
    class ScalableGradientWidget(QWidget):
        """Widget with gradient background that scales"""
        
        def __init__(self, color1="#1a1a2e", color2="#16213e", parent=None):
            super().__init__(parent)
            self.color1 = color1
            self.color2 = color2
            
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(self.color1))
            gradient.setColorAt(1, QColor(self.color2))
            painter.fillRect(self.rect(), QBrush(gradient))
            
    
    class ScalableModernCard(QFrame):
        """Modern card widget with shadow effect that scales"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("ScalableModernCard")
            self.setStyleSheet("""
                #ScalableModernCard {
                    background-color: rgba(30, 30, 46, 0.9);
                    border-radius: 15px;
                    border: 1px solid rgba(255,255,255,0.1);
                }
            """)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(0, 5)
            self.setGraphicsEffect(shadow)
            
    
    class TranscriptionWorker(QThread):
        """Worker thread for async transcription"""
        progress = pyqtSignal(int, str)
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)
        
        def __init__(self, input_file, settings):
            super().__init__()
            self.input_file = input_file
            self.settings = settings
            self._is_running = True
            
        def stop(self):
            self._is_running = False
            
        def run(self):
            try:
                import whisper
                import torch
                
                self.progress.emit(10, "Loading Whisper model...")
                model_name = self.settings.get('model', 'base')
                model_path = MODELS_DIR / f"{model_name}.pt"
                
                if not model_path.exists():
                    self.progress.emit(15, f"Downloading {model_name} model...")
                    model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
                else:
                    model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
                
                self.progress.emit(30, "Processing audio...")
                options = {
                    'language': self.settings.get('language', 'en'),
                    'task': 'translate' if self.settings.get('translate', False) else 'transcribe',
                    'verbose': False,
                    'fp16': False
                }
                
                self.progress.emit(50, "Transcribing...")
                result = model.transcribe(self.input_file, **options)
                
                self.progress.emit(80, "Processing segments...")
                segments = [{'start': seg['start'], 'end': seg['end'], 'text': seg['text'].strip()} 
                           for seg in result['segments']]
                
                self.progress.emit(90, "Generating subtitles...")
                subtitles = self._generate_subtitles(segments)
                
                self.progress.emit(100, "Complete!")
                self.finished.emit({'subtitles': subtitles, 'segments': segments})
                
            except Exception as e:
                self.error.emit(str(e))
                
        def _generate_subtitles(self, segments):
            subtitles = []
            for i, seg in enumerate(segments, 1):
                start = self._format_time(seg['start'])
                end = self._format_time(seg['end'])
                subtitles.append(f"{i}\n{start} --> {end}\n{seg['text']}\n")
            return subtitles
            
        def _format_time(self, seconds):
            td = timedelta(seconds=seconds)
            hours = int(td.total_seconds() // 3600)
            minutes = int((td.total_seconds() % 3600) // 60)
            secs = int(td.total_seconds() % 60)
            millis = int((td.total_seconds() % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    
    class FixedSizeWindow(QMainWindow):
        """Main window with fixed size - only maximize and minimize"""
        
        def __init__(self):
            super().__init__()
            self.settings = QSettings('NotY215', 'NotYCaptionGenAI')
            self.current_file = None
            self.current_subtitles = []
            self.current_segments = []
            self.worker = None
            self.media_player = None
            self.scale_factor = 1.0
            self.base_width = 1200
            self.base_height = 800
            
            # Set window flags - no resize border, only maximize/minimize
            self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | 
                               Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
            self.setFixedSize(self.base_width, self.base_height)
            self.setAttribute(Qt.WA_TranslucentBackground)
            
            self._setup_ui()
            self._setup_media_player()
            self._setup_animations()
            self._apply_theme()
            
        def resizeEvent(self, event: QResizeEvent):
            """Handle resize events - scale UI proportionally"""
            if self.isMaximized():
                # When maximized, scale everything based on screen size
                screen = QApplication.primaryScreen().geometry()
                self.scale_factor = min(screen.width() / self.base_width, 
                                       screen.height() / self.base_height)
                self._scale_ui(self.scale_factor)
            else:
                # When restored, reset to base size
                self.scale_factor = 1.0
                self.setFixedSize(self.base_width, self.base_height)
                self._scale_ui(1.0)
            super().resizeEvent(event)
            
        def _scale_ui(self, factor):
            """Scale all UI elements proportionally"""
            # Scale fonts
            font = QFont("Segoe UI", int(10 * factor))
            QApplication.setFont(font)
            
            # Scale all buttons
            for widget in self.findChildren(ScalableAnimatedButton):
                widget.resize_to_scale(factor)
            
            # Scale combo boxes
            for combo in self.findChildren(QComboBox):
                combo.setStyleSheet(f"""
                    QComboBox {{
                        background: #2d2d3d;
                        border: 1px solid #3d3d4d;
                        border-radius: {int(8 * factor)}px;
                        padding: {int(8 * factor)}px;
                        color: white;
                        font-size: {int(12 * factor)}px;
                    }}
                    QComboBox::drop-down {{
                        border: none;
                    }}
                """)
            
            # Scale spin boxes
            for spin in self.findChildren(QSpinBox):
                spin.setStyleSheet(f"""
                    QSpinBox {{
                        background: #2d2d3d;
                        border: 1px solid #3d3d4d;
                        border-radius: {int(8 * factor)}px;
                        padding: {int(5 * factor)}px;
                        color: white;
                        font-size: {int(12 * factor)}px;
                    }}
                """)
            
            # Scale checkboxes
            for check in self.findChildren(QCheckBox):
                check.setStyleSheet(f"""
                    QCheckBox {{
                        color: #aaa;
                        spacing: {int(8 * factor)}px;
                        font-size: {int(12 * factor)}px;
                    }}
                    QCheckBox::indicator {{
                        width: {int(16 * factor)}px;
                        height: {int(16 * factor)}px;
                        border-radius: {int(4 * factor)}px;
                        border: {int(2 * factor)}px solid #FF6B35;
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: #FF6B35;
                    }}
                """)
            
            # Scale labels
            for label in self.findChildren(QLabel):
                if label.objectName() != "media_icon":
                    current_font = label.font()
                    current_font.setPointSize(int(12 * factor))
                    label.setFont(current_font)
            
            # Scale text edit
            self.caption_editor.setStyleSheet(f"""
                QTextEdit {{
                    background: #1a1a2e;
                    border: 1px solid #2d2d3d;
                    border-radius: {int(10 * factor)}px;
                    padding: {int(15 * factor)}px;
                    color: #ddd;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: {int(11 * factor)}px;
                }}
            """)
            
            # Scale progress bar
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: {int(10 * factor)}px;
                    background: #2d2d3d;
                    height: {int(8 * factor)}px;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:1 #F7931E);
                    border-radius: {int(10 * factor)}px;
                }}
            """)
            
            # Scale slider
            self.time_slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    height: {int(4 * factor)}px;
                    background: #2d2d3d;
                    border-radius: {int(2 * factor)}px;
                }}
                QSlider::handle:horizontal {{
                    background: #FF6B35;
                    width: {int(12 * factor)}px;
                    height: {int(12 * factor)}px;
                    margin: -{int(4 * factor)}px 0;
                    border-radius: {int(6 * factor)}px;
                }}
                QSlider::sub-page:horizontal {{
                    background: #FF6B35;
                    border-radius: {int(2 * factor)}px;
                }}
            """)
            
        def _setup_ui(self):
            """Setup the main UI"""
            central = ScalableGradientWidget("#1a1a2e", "#16213e")
            self.setCentralWidget(central)
            
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(20)
            
            # Custom Title Bar
            title_bar = self._create_title_bar()
            main_layout.addWidget(title_bar)
            
            # Main Content Card
            content_card = ScalableModernCard()
            content_layout = QVBoxLayout(content_card)
            content_layout.setContentsMargins(25, 25, 25, 25)
            content_layout.setSpacing(20)
            
            # Header Section
            header = self._create_header()
            content_layout.addWidget(header)
            
            # Main Splitter
            splitter = QSplitter(Qt.Horizontal)
            splitter.setHandleWidth(2)
            splitter.setStyleSheet("QSplitter::handle { background-color: rgba(255,255,255,0.2); border-radius: 2px; }")
            
            # Left Panel - Controls
            left_panel = self._create_control_panel()
            splitter.addWidget(left_panel)
            
            # Right Panel - Caption Editor
            right_panel = self._create_caption_panel()
            splitter.addWidget(right_panel)
            
            splitter.setSizes([450, 750])
            content_layout.addWidget(splitter)
            
            # Progress Section
            progress_section = self._create_progress_section()
            content_layout.addWidget(progress_section)
            
            main_layout.addWidget(content_card)
            
        def _create_title_bar(self):
            """Create custom title bar with window controls"""
            title_bar = QWidget()
            title_bar.setFixedHeight(50)
            layout = QHBoxLayout(title_bar)
            layout.setContentsMargins(10, 0, 10, 0)
            
            # App Icon and Title
            title_label = QLabel("🎬 NotY Caption Generator AI")
            title_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: 'Segoe UI', 'Arial';
                }
            """)
            layout.addWidget(title_label)
            
            layout.addStretch()
            
            # Window Controls - only minimize, maximize, close
            for name, color, action in [
                ("─", "#555555", self.showMinimized),
                ("□", "#555555", self.showMaximized),
                ("✕", "#e74c3c", self.close)
            ]:
                btn = QPushButton(name)
                btn.setFixedSize(35, 30)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 14px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {color};
                    }}
                """)
                btn.clicked.connect(action)
                layout.addWidget(btn)
                
            return title_bar
            
        def _create_header(self):
            """Create header section with gradient"""
            header = QWidget()
            header.setFixedHeight(100)
            header.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:0.5 #F7931E, stop:1 #FF6B35);
                    border-radius: 15px;
                }
            """)
            
            layout = QHBoxLayout(header)
            layout.setContentsMargins(30, 0, 30, 0)
            
            # Left side - Welcome text
            welcome = QLabel("🎯 AI-Powered Subtitle Generator")
            welcome.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    font-family: 'Segoe UI', 'Arial';
                }
            """)
            layout.addWidget(welcome)
            
            layout.addStretch()
            
            # Right side - Quick stats
            stats = QLabel("Ready to create amazing captions")
            stats.setStyleSheet("""
                QLabel {
                    color: rgba(255,255,255,0.9);
                    font-size: 13px;
                }
            """)
            layout.addWidget(stats)
            
            return header
            
        def _create_control_panel(self):
            """Create control panel with modern widgets"""
            panel = QScrollArea()
            panel.setWidgetResizable(True)
            panel.setStyleSheet("""
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    background: rgba(255,255,255,0.1);
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: #FF6B35;
                    border-radius: 4px;
                }
            """)
            
            content = QWidget()
            content.setStyleSheet("background-color: transparent;")
            layout = QVBoxLayout(content)
            layout.setSpacing(15)
            
            # Media Info Card
            media_card = ScalableModernCard()
            media_layout = QVBoxLayout(media_card)
            media_layout.setContentsMargins(15, 15, 15, 15)
            
            self.media_icon = QLabel("📁")
            self.media_icon.setStyleSheet("font-size: 48px;")
            self.media_label = QLabel("No Media Loaded")
            self.media_label.setStyleSheet("color: #888; font-size: 13px;")
            self.media_label.setWordWrap(True)
            self.media_label.setAlignment(Qt.AlignCenter)
            
            media_layout.addWidget(self.media_icon, alignment=Qt.AlignCenter)
            media_layout.addWidget(self.media_label, alignment=Qt.AlignCenter)
            layout.addWidget(media_card)
            
            # Import Buttons
            import_group = QWidget()
            import_layout = QHBoxLayout(import_group)
            import_layout.setSpacing(10)
            
            self.import_btn = ScalableAnimatedButton("📁 Import Media", "#3498db", "#2980b9", base_height=40)
            self.import_btn.clicked.connect(self.import_media)
            import_layout.addWidget(self.import_btn)
            
            self.youtube_btn = ScalableAnimatedButton("▶️ YouTube URL", "#e74c3c", "#c0392b", base_height=40)
            self.youtube_btn.clicked.connect(self.import_youtube)
            import_layout.addWidget(self.youtube_btn)
            
            layout.addWidget(import_group)
            
            # Settings Sections
            sections = [
                ("🎤 Whisper Model", self._create_model_section()),
                ("🌐 Language", self._create_language_section()),
                ("🎵 Vocal Separation", self._create_vocal_section()),
                ("📝 Line Break", self._create_break_section()),
            ]
            
            for title, widget in sections:
                section = ScalableModernCard()
                section_layout = QVBoxLayout(section)
                section_layout.setContentsMargins(15, 10, 15, 10)
                
                title_label = QLabel(title)
                title_label.setStyleSheet("color: #FF6B35; font-weight: bold; font-size: 13px;")
                section_layout.addWidget(title_label)
                section_layout.addWidget(widget)
                
                layout.addWidget(section)
            
            # Generate Button
            self.generate_btn = ScalableAnimatedButton("🚀 GENERATE CAPTIONS", "#FF6B35", "#F7931E", base_height=50)
            self.generate_btn.clicked.connect(self.generate_captions)
            self.generate_btn.setEnabled(False)
            layout.addWidget(self.generate_btn)
            
            layout.addStretch()
            panel.setWidget(content)
            return panel
            
        def _create_model_section(self):
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.model_combo = QComboBox()
            models = ['tiny', 'base', 'small', 'medium', 'large']
            self.model_combo.addItems([f"{m.upper()}" for m in models])
            self.model_combo.setCurrentIndex(1)
            self.model_combo.setStyleSheet("""
                QComboBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 8px;
                    color: white;
                }
                QComboBox::drop-down {
                    border: none;
                }
            """)
            layout.addWidget(self.model_combo)
            
            info_label = QLabel("⚡ Larger = Better accuracy, slower")
            info_label.setStyleSheet("color: #666; font-size: 11px;")
            layout.addWidget(info_label)
            
            return widget
            
        def _create_language_section(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.lang_combo = QComboBox()
            languages = [
                ("English", "en", "High"), ("Spanish", "es", "High"), ("Italian", "it", "High"),
                ("Portuguese", "pt", "High"), ("German", "de", "High"), ("Japanese", "ja", "High"),
                ("French", "fr", "High"), ("Russian", "ru", "Medium"), ("Hindi", "hi", "Low"),
                ("Tamil", "ta", "Low"), ("Bengali", "bn", "Low"), ("Urdu", "ur", "Low")
            ]
            for name, code, acc in languages:
                self.lang_combo.addItem(f"{name} - {acc} Accuracy", code)
            self.lang_combo.setStyleSheet("""
                QComboBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 8px;
                    color: white;
                }
            """)
            layout.addWidget(self.lang_combo)
            
            self.translate_check = QCheckBox("🔄 Translate to English")
            self.translate_check.setStyleSheet("""
                QCheckBox {
                    color: #aaa;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 2px solid #FF6B35;
                }
                QCheckBox::indicator:checked {
                    background-color: #FF6B35;
                }
            """)
            layout.addWidget(self.translate_check)
            
            return widget
            
        def _create_vocal_section(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.vocal_combo = QComboBox()
            self.vocal_combo.addItems(['None', '2stems (Vocals + Accompaniment)', '4stems', '5stems'])
            self.vocal_combo.setStyleSheet("""
                QComboBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 8px;
                    color: white;
                }
            """)
            layout.addWidget(self.vocal_combo)
            
            return widget
            
        def _create_break_section(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.break_combo = QComboBox()
            self.break_combo.addItems(['Auto (Smart sentences)', 'Words', 'Letters'])
            self.break_combo.setStyleSheet("""
                QComboBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 8px;
                    color: white;
                }
            """)
            layout.addWidget(self.break_combo)
            
            limit_row = QHBoxLayout()
            self.word_limit = QSpinBox()
            self.word_limit.setRange(1, 30)
            self.word_limit.setValue(10)
            self.word_limit.setEnabled(False)
            self.word_limit.setStyleSheet("""
                QSpinBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 5px;
                    color: white;
                }
            """)
            limit_row.addWidget(QLabel("Words/line:"))
            limit_row.addWidget(self.word_limit)
            
            self.char_limit = QSpinBox()
            self.char_limit.setRange(10, 80)
            self.char_limit.setValue(40)
            self.char_limit.setEnabled(False)
            self.char_limit.setStyleSheet("""
                QSpinBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 5px;
                    color: white;
                }
            """)
            limit_row.addWidget(QLabel("Chars/line:"))
            limit_row.addWidget(self.char_limit)
            
            layout.addLayout(limit_row)
            self.break_combo.currentIndexChanged.connect(self._on_break_changed)
            
            return widget
            
        def _create_caption_panel(self):
            """Create caption editor panel"""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setSpacing(15)
            
            # Player Controls Card
            player_card = ScalableModernCard()
            player_layout = QVBoxLayout(player_card)
            player_layout.setContentsMargins(15, 15, 15, 15)
            
            # Time Slider
            self.time_slider = QSlider(Qt.Horizontal)
            self.time_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 4px;
                    background: #2d2d3d;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #FF6B35;
                    width: 12px;
                    height: 12px;
                    margin: -4px 0;
                    border-radius: 6px;
                }
                QSlider::sub-page:horizontal {
                    background: #FF6B35;
                    border-radius: 2px;
                }
            """)
            self.time_slider.sliderMoved.connect(self.seek_position)
            player_layout.addWidget(self.time_slider)
            
            # Control Buttons
            controls = QHBoxLayout()
            self.play_btn = ScalableAnimatedButton("▶ Play", "#2ecc71", "#27ae60", base_height=35)
            self.play_btn.setFixedWidth(100)
            self.play_btn.clicked.connect(self.toggle_playback)
            self.play_btn.setEnabled(False)
            controls.addWidget(self.play_btn)
            
            self.stop_btn = ScalableAnimatedButton("⏹ Stop", "#e74c3c", "#c0392b", base_height=35)
            self.stop_btn.setFixedWidth(100)
            self.stop_btn.clicked.connect(self.stop_playback)
            self.stop_btn.setEnabled(False)
            controls.addWidget(self.stop_btn)
            
            self.time_label = QLabel("00:00:00 / 00:00:00")
            self.time_label.setStyleSheet("color: #FF6B35; font-family: monospace; font-size: 13px;")
            controls.addWidget(self.time_label)
            controls.addStretch()
            
            player_layout.addLayout(controls)
            layout.addWidget(player_card)
            
            # Caption Editor Card
            editor_card = ScalableModernCard()
            editor_layout = QVBoxLayout(editor_card)
            editor_layout.setContentsMargins(15, 15, 15, 15)
            
            editor_header = QHBoxLayout()
            editor_header.addWidget(QLabel("📝 Caption Editor"))
            editor_header.addStretch()
            
            self.edit_mode_btn = QPushButton("✏️ Edit Mode")
            self.edit_mode_btn.setCheckable(True)
            self.edit_mode_btn.setStyleSheet("""
                QPushButton {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 6px;
                    padding: 5px 15px;
                    color: #aaa;
                }
                QPushButton:checked {
                    background: #FF6B35;
                    color: white;
                }
            """)
            self.edit_mode_btn.clicked.connect(self.toggle_edit_mode)
            editor_header.addWidget(self.edit_mode_btn)
            
            self.save_edit_btn = QPushButton("💾 Save")
            self.save_edit_btn.setEnabled(False)
            self.save_edit_btn.setStyleSheet("""
                QPushButton {
                    background: #2ecc71;
                    border: none;
                    border-radius: 6px;
                    padding: 5px 15px;
                    color: white;
                }
                QPushButton:disabled {
                    background: #555;
                }
            """)
            self.save_edit_btn.clicked.connect(self.save_caption_edits)
            editor_header.addWidget(self.save_edit_btn)
            
            editor_layout.addLayout(editor_header)
            
            self.caption_editor = QTextEdit()
            self.caption_editor.setFont(QFont("Consolas", 11))
            self.caption_editor.setStyleSheet("""
                QTextEdit {
                    background: #1a1a2e;
                    border: 1px solid #2d2d3d;
                    border-radius: 10px;
                    padding: 15px;
                    color: #ddd;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """)
            self.caption_editor.setPlaceholderText("Generated captions will appear here...")
            editor_layout.addWidget(self.caption_editor)
            
            layout.addWidget(editor_card)
            
            return panel
            
        def _create_progress_section(self):
            """Create progress section"""
            card = ScalableModernCard()
            layout = QVBoxLayout(card)
            layout.setContentsMargins(15, 10, 15, 10)
            
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 10px;
                    background: #2d2d3d;
                    height: 8px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:1 #F7931E);
                    border-radius: 10px;
                }
            """)
            layout.addWidget(self.progress_bar)
            
            self.progress_label = QLabel("")
            self.progress_label.setStyleSheet("color: #888; font-size: 12px;")
            self.progress_label.setVisible(False)
            layout.addWidget(self.progress_label)
            
            return card
            
        def _setup_media_player(self):
            self.media_player = QMediaPlayer()
            self.media_player.positionChanged.connect(self.update_position)
            self.media_player.durationChanged.connect(self.update_duration)
            self.media_player.stateChanged.connect(self.update_playback_state)
            
        def _setup_animations(self):
            self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
            self.fade_animation.setDuration(500)
            self.fade_animation.setStartValue(0)
            self.fade_animation.setEndValue(1)
            self.fade_animation.start()
            
        def _apply_theme(self):
            self.setStyleSheet("""
                QToolTip {
                    background-color: #2d2d3d;
                    color: #FF6B35;
                    border: 1px solid #FF6B35;
                    border-radius: 5px;
                    padding: 5px;
                }
                QLabel {
                    color: #ddd;
                }
            """)
            
        def _on_break_changed(self, index):
            self.word_limit.setEnabled(index == 1)
            self.char_limit.setEnabled(index == 2)
            
        def import_media(self):
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Media", "",
                "Media Files (*.mp4 *.avi *.mkv *.mov *.mp3 *.wav *.flac *.m4a)"
            )
            if file_path:
                self.load_media(file_path)
                
        def import_youtube(self):
            from PyQt5.QtWidgets import QInputDialog
            url, ok = QInputDialog.getText(self, "YouTube URL", "Enter YouTube URL:")
            if ok and url:
                self.statusBar().showMessage("Downloading YouTube video...")
                try:
                    import yt_dlp
                    temp_dir = tempfile.gettempdir()
                    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': output_template,
                        'quiet': True,
                        'no_warnings': True,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        audio_file = Path(filename).with_suffix('.mp3')
                        if audio_file.exists():
                            self.load_media(str(audio_file))
                        elif Path(filename).exists():
                            self.load_media(filename)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to download: {str(e)}")
                    
        def load_media(self, file_path):
            self.current_file = file_path
            self.media_label.setText(f"📹 {Path(file_path).name}")
            self.generate_btn.setEnabled(True)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            
            # Animate media icon
            anim = QPropertyAnimation(self.media_icon, b"geometry")
            anim.setDuration(300)
            anim.setStartValue(self.media_icon.geometry())
            anim.setEndValue(QRect(self.media_icon.x(), self.media_icon.y()-10, 
                                   self.media_icon.width(), self.media_icon.height()))
            anim.start()
            
        def generate_captions(self):
            if not self.current_file:
                return
                
            settings = {
                'model': self.model_combo.currentText().lower(),
                'language': self.lang_combo.currentData(),
                'translate': self.translate_check.isChecked(),
                'vocal_separation': self.vocal_combo.currentIndex(),
                'break_type': ['auto', 'words', 'letters'][self.break_combo.currentIndex()],
                'word_limit': self.word_limit.value(),
                'char_limit': self.char_limit.value()
            }
            
            self.progress_bar.setVisible(True)
            self.progress_label.setVisible(True)
            self.progress_bar.setValue(0)
            self.generate_btn.setEnabled(False)
            
            self.worker = TranscriptionWorker(self.current_file, settings)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.on_transcription_finished)
            self.worker.error.connect(self.on_transcription_error)
            self.worker.start()
            
        def update_progress(self, value, message):
            self.progress_bar.setValue(value)
            self.progress_label.setText(message)
            self.progress_label.setStyleSheet(f"color: #FF6B35; font-size: 12px;")
            
        def on_transcription_finished(self, result):
            self.current_subtitles = result['subtitles']
            self.current_segments = result['segments']
            self.caption_editor.setText('\n'.join(self.current_subtitles))
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            self.generate_btn.setEnabled(True)
            
            # Success animation
            self.progress_label.setText("✓ Complete!")
            self.progress_label.setStyleSheet("color: #2ecc71; font-size: 14px; font-weight: bold;")
            self.progress_label.setVisible(True)
            QTimer.singleShot(2000, lambda: self.progress_label.setVisible(False))
            
            QMessageBox.information(self, "Success", 
                f"✨ Successfully generated {len(self.current_subtitles)} captions!")
            
        def on_transcription_error(self, error):
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            self.generate_btn.setEnabled(True)
            QMessageBox.critical(self, "Error", f"❌ Transcription failed: {error}")
            
        def toggle_playback(self):
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                self.play_btn.setText("▶ Play")
            else:
                self.media_player.play()
                self.play_btn.setText("⏸ Pause")
                
        def stop_playback(self):
            self.media_player.stop()
            self.play_btn.setText("▶ Play")
            
        def seek_position(self, position):
            self.media_player.setPosition(position)
            
        def update_position(self, position):
            self.time_slider.blockSignals(True)
            self.time_slider.setValue(position)
            self.time_slider.blockSignals(False)
            
            current = str(timedelta(milliseconds=position))[:-3]
            total = str(timedelta(milliseconds=self.media_player.duration()))[:-3]
            self.time_label.setText(f"{current} / {total}")
            self.highlight_current_caption(position / 1000)
            
        def update_duration(self, duration):
            self.time_slider.setRange(0, duration)
            
        def update_playback_state(self, state):
            if state == QMediaPlayer.StoppedState:
                self.play_btn.setText("▶ Play")
                
        def highlight_current_caption(self, current_time):
            for caption in self.current_subtitles:
                lines = caption.split('\n')
                if len(lines) >= 2 and '-->' in lines[1]:
                    start_str, end_str = lines[1].split(' --> ')
                    start = self._parse_srt_time(start_str)
                    end = self._parse_srt_time(end_str)
                    if start <= current_time <= end:
                        cursor = self.caption_editor.textCursor()
                        text = self.caption_editor.toPlainText()
                        pos = text.find(caption)
                        if pos >= 0:
                            cursor.setPosition(pos)
                            cursor.movePosition(QTextCursor.NextCharacter, 
                                                QTextCursor.KeepAnchor, len(caption))
                            self.caption_editor.setTextCursor(cursor)
                        break
                        
        def _parse_srt_time(self, time_str):
            time_str = time_str.replace(',', '.')
            parts = time_str.split(':')
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            return 0
            
        def toggle_edit_mode(self):
            self.caption_editor.setReadOnly(not self.edit_mode_btn.isChecked())
            self.save_edit_btn.setEnabled(self.edit_mode_btn.isChecked())
            if self.edit_mode_btn.isChecked():
                self.edit_mode_btn.setStyleSheet("background: #FF6B35; color: white;")
            else:
                self.edit_mode_btn.setStyleSheet("background: #2d2d3d; color: #aaa;")
                
        def save_caption_edits(self):
            text = self.caption_editor.toPlainText()
            blocks = text.strip().split('\n\n')
            self.current_subtitles = [block + '\n' for block in blocks if block.strip()]
            self.save_edit_btn.setEnabled(False)
            self.edit_mode_btn.setChecked(False)
            self.caption_editor.setReadOnly(True)
            self.edit_mode_btn.setStyleSheet("background: #2d2d3d; color: #aaa;")
            QMessageBox.information(self, "Success", "💾 Captions saved!")
            
        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
                
        def mouseMoveEvent(self, event):
            if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
                self.move(event.globalPos() - self.drag_position)
                event.accept()
                
        def closeEvent(self, event):
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                self.worker.wait()
            if self.media_player:
                self.media_player.stop()
            event.accept()


# ============================================================================
# CLI MODE MAIN
# ============================================================================

def run_cli():
    """Run CLI version when GUI is not available"""
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}     NotY Caption Generator AI v7.1 - CLI Mode{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.WARNING}GUI mode not available. Install PyQt5 for GUI.{Colors.ENDC}\n")
    
    cache = CacheManager()
    transcriber = Transcriber(cache)
    
    while True:
        print(f"\n{Colors.GREEN}Main Menu:{Colors.ENDC}")
        print("  1. Process Media File")
        print("  2. Download YouTube Video")
        print("  3. Settings")
        print("  4. Clear Cache")
        print("  5. Exit")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.ENDC}").strip()
        
        if choice == '1':
            file_path = input("Enter file path: ").strip().strip('"')
            path = Path(file_path)
            if not path.exists():
                print(f"{Colors.FAIL}File not found!{Colors.ENDC}")
                continue
                
            model = input(f"Model (tiny/base/small/medium/large) [base]: ").strip() or 'base'
            language = input(f"Language code [en]: ").strip() or 'en'
            translate = input(f"Translate to English? (y/n) [n]: ").strip().lower() == 'y'
            
            print(f"\n{Colors.BLUE}Loading model...{Colors.ENDC}")
            transcriber.load_model(model)
            
            print(f"{Colors.BLUE}Transcribing...{Colors.ENDC}")
            task = 'translate' if translate else 'transcribe'
            segments = transcriber.transcribe(path, language, task, progress_callback=lambda p,m: print(f"  {p}% - {m}"))
            
            generator = SubtitleGenerator('auto', 10, 40)
            srt_content = generator.generate_srt(segments)
            
            output_path = path.with_suffix('.srt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
                
            print(f"{Colors.GREEN}✓ Subtitles saved to: {output_path}{Colors.ENDC}")
            
        elif choice == '2':
            try:
                import yt_dlp
                url = input("Enter YouTube URL: ").strip()
                if url:
                    print(f"{Colors.BLUE}Downloading...{Colors.ENDC}")
                    temp_dir = Path(tempfile.gettempdir()) / 'NotYCaptionGenAI'
                    temp_dir.mkdir(exist_ok=True)
                    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': str(temp_dir / '%(title)s.%(ext)s'), 'quiet': True}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        print(f"{Colors.GREEN}Downloaded: {filename}{Colors.ENDC}")
            except ImportError:
                print(f"{Colors.FAIL}yt-dlp not installed. Run: pip install yt-dlp{Colors.ENDC}")
                
        elif choice == '3':
            print(f"{Colors.CYAN}Settings (placeholder - use config file){Colors.ENDC}")
            
        elif choice == '4':
            # Clear old cache (0 days = all)
            with sqlite3.connect(CACHE_DB) as conn:
                conn.execute('DELETE FROM transcriptions')
            print(f"{Colors.GREEN}Cache cleared{Colors.ENDC}")
            
        elif choice == '5':
            print(f"{Colors.GREEN}Goodbye!{Colors.ENDC}")
            break


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point - automatically selects GUI or CLI"""
    if GUI_AVAILABLE:
        app = QApplication(sys.argv)
        app.setApplicationName("NotY Caption Generator AI")
        app.setOrganizationName("NotY215")
        
        # Set application icon
        app.setWindowIcon(QIcon())
        
        window = FixedSizeWindow()
        window.show()
        
        sys.exit(app.exec_())
    else:
        run_cli()


if __name__ == "__main__":
    main()