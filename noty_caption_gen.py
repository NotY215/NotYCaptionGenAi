#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI v7.1 - Colorful Animated Professional UI
Copyright (c) 2026 NotY215

Features:
- Fixed window size (1200x800) with maximize/minimize only
- Auto-scaling UI when maximized
- Vibrant colors and smooth animations
- 2000+ lines of rich functionality
- Professional gradient designs
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
import random
from pathlib import Path
from datetime import timedelta
from threading import Thread, Lock
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from functools import partial
from collections import deque

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
        QGridLayout, QSplitter, QStackedWidget, QToolTip, QSizePolicy,
        QGraphicsDropShadowEffect
    )
    from PyQt5.QtCore import (
        Qt, QThread, pyqtSignal, QTimer, QUrl, QSettings, QSize, QPropertyAnimation,
        QEasingCurve, QPoint, QRect, QParallelAnimationGroup, QSequentialAnimationGroup,
        QPointF, QDateTime, QEvent
    )
    from PyQt5.QtGui import (
        QFont, QIcon, QPalette, QColor, QLinearGradient, QBrush, QPainter,
        QPen, QFontDatabase, QMovie, QPixmap, QPainterPath, QRegion, QResizeEvent,
        QGradient, QRadialGradient, QConicalGradient
    )
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    GUI_AVAILABLE = True
except ImportError as e:
    GUI_AVAILABLE = False
    print(f"PyQt5 not available: {e}. Falling back to CLI mode.")


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
    
    # Extended color palette
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    YELLOW = '\033[93m'
    WHITE = '\033[97m'


class ProgressBar:
    """Animated progress bar for console"""
    def __init__(self, total: int, prefix: str = '', suffix: str = '', length: int = 50):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.current = 0
        self.start_time = time.time()
        
    def update(self, current: int = None):
        if current is not None:
            self.current = current
        else:
            self.current += 1
            
        percent = 100 * (self.current / float(self.total))
        filled = int(self.length * self.current // self.total)
        bar = '█' * filled + '░' * (self.length - filled)
        
        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {int(eta)}s"
        else:
            eta_str = "ETA: --s"
            
        print(f'\r{self.prefix} |{bar}| {percent:.1f}% {self.suffix} {eta_str}', end='')
        
    def finish(self):
        self.update(self.total)
        print(f"\n{Colors.GREEN}✓ Complete! Time: {time.time() - self.start_time:.1f}s{Colors.ENDC}")


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
            conn.execute('CREATE INDEX IF NOT EXISTS idx_hash ON transcriptions(file_hash, model, language, task)')
            
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
    
    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM transcriptions')
            
    def get_stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*), SUM(LENGTH(segments)) FROM transcriptions')
            count, size = cursor.fetchone()
            return {'count': count or 0, 'size': size or 0}


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
                print(f"{Colors.CYAN}📥 Downloading {model_name} model...{Colors.ENDC}")
            self.model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
            self.model_name = model_name
            print(f"{Colors.GREEN}✓ Model loaded: {model_name}{Colors.ENDC}")
        except ImportError:
            raise RuntimeError("Whisper not installed. Run: pip install openai-whisper")
            
    def transcribe(self, audio_path: Path, language: str, task: str = 'transcribe', 
                   use_cache: bool = True, progress_callback=None) -> List[Dict]:
        if use_cache:
            cached = self.cache_manager.get(audio_path, self.model_name, language, task)
            if cached:
                if progress_callback:
                    progress_callback(100, "Using cached transcription")
                return cached
                
        if progress_callback:
            progress_callback(10, "🎵 Loading audio...")
            
        options = {
            'language': language, 
            'task': task, 
            'verbose': False, 
            'fp16': False, 
            'word_timestamps': True
        }
        
        if progress_callback:
            progress_callback(30, "🎤 Transcribing...")
            
        result = self.model.transcribe(str(audio_path), **options)
        
        if progress_callback:
            progress_callback(80, "📝 Processing segments...")
            
        segments = [{
            'start': seg['start'], 
            'end': seg['end'], 
            'text': seg['text'].strip(), 
            'words': seg.get('words', [])
        } for seg in result['segments']]
        
        if use_cache:
            self.cache_manager.set(audio_path, self.model_name, language, task, segments)
            
        if progress_callback:
            progress_callback(100, "✅ Complete!")
            
        return segments


class SubtitleGenerator:
    """Generates SRT/ASS subtitles with multiple formatting options"""
    
    def __init__(self, break_type: str = 'auto', word_limit: int = 10, char_limit: int = 40):
        self.break_type = break_type
        self.word_limit = word_limit
        self.char_limit = char_limit
        
    def generate_srt(self, segments: List[Dict]) -> str:
        """Generate SRT formatted subtitles"""
        subtitles = []
        for i, seg in enumerate(segments, 1):
            text = self._apply_breaks(seg['text'])
            start = self._format_time_srt(seg['start'])
            end = self._format_time_srt(seg['end'])
            subtitles.append(f"{i}\n{start} --> {end}\n{text}\n")
        return '\n'.join(subtitles)
    
    def generate_ass(self, segments: List[Dict], width: int = 1920, height: int = 1080) -> str:
        """Generate ASS formatted subtitles with styling"""
        header = f"""[Script Info]
Title: NotY Caption Generator AI
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H00FFFFFF,&H0000FF00,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for seg in segments:
            start = self._format_time_ass(seg['start'])
            end = self._format_time_ass(seg['end'])
            text = self._apply_breaks(seg['text'])
            events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
        return header + '\n'.join(events)
        
    def _apply_breaks(self, text: str) -> str:
        """Apply line breaks based on break type"""
        if self.break_type == 'words':
            words = text.split()
            lines = [' '.join(words[i:i+self.word_limit]) for i in range(0, len(words), self.word_limit)]
            return '\\N'.join(lines)
        elif self.break_type == 'letters':
            lines = [text[i:i+self.char_limit] for i in range(0, len(text), self.char_limit)]
            return '\\N'.join(lines)
        else:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            if len(sentences) <= 2:
                return text
            lines = []
            for i in range(0, len(sentences), 2):
                lines.append(' '.join(sentences[i:i+2]))
            return '\\N'.join(lines)
            
    def _format_time_srt(self, seconds: float) -> str:
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def _format_time_ass(self, seconds: float) -> str:
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = td.total_seconds() % 60
        return f"{hours}:{minutes:02d}:{secs:06.2f}".replace('.', ',')


# ============================================================================
# GUI MODE - Colorful Animated Professional UI
# ============================================================================

if GUI_AVAILABLE:
    
    # Color Palette
    COLORS = {
        'primary': ['#FF6B35', '#F7931E', '#FF3366', '#FF6B6B'],
        'secondary': ['#4ECDC4', '#45B7D1', '#96CEB4', '#2ECC71'],
        'accent': ['#9B59B6', '#8E44AD', '#E74C3C', '#3498DB'],
        'success': ['#2ECC71', '#27AE60'],
        'warning': ['#F39C12', '#E67E22'],
        'danger': ['#E74C3C', '#C0392B'],
        'dark': ['#1a1a2e', '#16213e', '#0f3460'],
        'light': ['#e9ecef', '#f8f9fa', '#dee2e6']
    }
    
    class ColorButton(QPushButton):
        """Beautiful animated button with gradient colors"""
        
        def __init__(self, text, color_scheme='primary', parent=None, base_height=40):
            super().__init__(text, parent)
            self.color_scheme = color_scheme
            self.base_height = base_height
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(200)
            self.animation.setEasingCurve(QEasingCurve.OutBounce)
            self.setCursor(Qt.PointingHandCursor)
            self._setup_style()
            
        def _setup_style(self):
            colors = COLORS.get(self.color_scheme, COLORS['primary'])
            color_start = colors[0]
            color_end = colors[1] if len(colors) > 1 else colors[0]
            
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {color_start}, stop:1 {color_end});
                    border: none;
                    border-radius: 10px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {self._adjust_brightness(color_start, 1.1)},
                        stop:1 {self._adjust_brightness(color_end, 1.1)});
                    transform: scale(1.05);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {self._adjust_brightness(color_start, 0.8)},
                        stop:1 {self._adjust_brightness(color_end, 0.8)});
                }}
                QPushButton:disabled {{
                    background: #555555;
                    color: #888888;
                }}
            """)
            
            # Add shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(0, 4)
            self.setGraphicsEffect(shadow)
            
        def _adjust_brightness(self, color, factor):
            r = int(int(color[1:3], 16) * factor)
            g = int(int(color[3:5], 16) * factor)
            b = int(int(color[5:7], 16) * factor)
            return f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"
            
        def resize_to_scale(self, scale_factor):
            new_height = int(self.base_height * scale_factor)
            self.setMinimumHeight(new_height)
            self.setMaximumHeight(new_height)
            font = self.font()
            font.setPointSize(int(14 * scale_factor))
            self.setFont(font)
            
        def enterEvent(self, event):
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(self.x()-3, self.y()-3, self.width()+6, self.height()+6))
            self.animation.start()
            super().enterEvent(event)
            
        def leaveEvent(self, event):
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(QRect(self.x()+3, self.y()+3, self.width()-6, self.height()-6))
            self.animation.start()
            super().leaveEvent(event)
    
    
    class AnimatedGradientWidget(QWidget):
        """Widget with animated gradient background"""
        
        def __init__(self, colors=None, parent=None):
            super().__init__(parent)
            self.colors = colors or ['#1a1a2e', '#16213e', '#0f3460']
            self.offset = 0
            self.animation = QPropertyAnimation(self, b"offset")
            self.animation.setDuration(3000)
            self.animation.setStartValue(0)
            self.animation.setEndValue(100)
            self.animation.setLoopCount(-1)
            self.animation.start()
            
        def get_offset(self):
            return self._offset
            
        def set_offset(self, value):
            self._offset = value
            self.update()
            
        offset = property(get_offset, set_offset)
        
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            positions = [0, 0.5, 1]
            
            for i, color in enumerate(self.colors):
                pos = (positions[i] + self.offset / 100) % 1.0
                gradient.setColorAt(pos, QColor(color))
                
            painter.fillRect(self.rect(), QBrush(gradient))
    
    
    class ModernCard(QFrame):
        """Modern card widget with shadow and hover effect"""
        
        def __init__(self, parent=None, color="#2d2d3d"):
            super().__init__(parent)
            self.color = color
            self.setObjectName("ModernCard")
            self._setup_style()
            
            # Hover animation
            self.hover_animation = QPropertyAnimation(self, b"geometry")
            self.hover_animation.setDuration(150)
            
        def _setup_style(self):
            self.setStyleSheet(f"""
                #ModernCard {{
                    background-color: {self.color};
                    border-radius: 15px;
                    border: 1px solid rgba(255,255,255,0.1);
                }}
            """)
            
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 5)
            self.setGraphicsEffect(shadow)
            
        def enterEvent(self, event):
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(QRect(self.x(), self.y()-5, self.width(), self.height()+5))
            self.hover_animation.start()
            super().enterEvent(event)
            
        def leaveEvent(self, event):
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(QRect(self.x(), self.y()+5, self.width(), self.height()-5))
            self.hover_animation.start()
            super().leaveEvent(event)
    
    
    class PulsingProgressBar(QProgressBar):
        """Progress bar with pulsing animation"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.pulse_value = 0
            self.pulse_animation = QPropertyAnimation(self, b"pulse_value")
            self.pulse_animation.setDuration(1000)
            self.pulse_animation.setStartValue(0)
            self.pulse_animation.setEndValue(100)
            self.pulse_animation.setLoopCount(-1)
            
        def get_pulse_value(self):
            return self._pulse_value
            
        def set_pulse_value(self, value):
            self._pulse_value = value
            self.update()
            
        pulse_value = property(get_pulse_value, set_pulse_value)
        
        def paintEvent(self, event):
            super().paintEvent(event)
            if self.value() < 100:
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                gradient = QLinearGradient(self.width() * self.pulse_value / 100, 0,
                                          self.width() * (self.pulse_value + 20) / 100, 0)
                gradient.setColorAt(0, QColor(255, 107, 53, 100))
                gradient.setColorAt(1, QColor(247, 147, 30, 0))
                painter.fillRect(self.rect(), QBrush(gradient))
    
    
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
                
                self.progress.emit(5, "🎯 Initializing...")
                model_name = self.settings.get('model', 'base')
                model_path = MODELS_DIR / f"{model_name}.pt"
                
                self.progress.emit(10, f"📥 Loading {model_name} model...")
                if not model_path.exists():
                    self.progress.emit(12, f"⬇️ Downloading {model_name} model...")
                    model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
                else:
                    model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
                
                self.progress.emit(25, "🎵 Processing audio...")
                options = {
                    'language': self.settings.get('language', 'en'),
                    'task': 'translate' if self.settings.get('translate', False) else 'transcribe',
                    'verbose': False,
                    'fp16': False
                }
                
                self.progress.emit(40, "🎤 Transcribing (this may take a while)...")
                result = model.transcribe(self.input_file, **options)
                
                self.progress.emit(75, "📝 Processing segments...")
                segments = [{'start': seg['start'], 'end': seg['end'], 'text': seg['text'].strip()} 
                           for seg in result['segments']]
                
                self.progress.emit(85, "🎨 Generating subtitles...")
                subtitles = self._generate_subtitles(segments)
                
                self.progress.emit(100, "✅ Complete!")
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
    
    
    class NotYCaptionWindow(QMainWindow):
        """Main application window with colorful animated UI"""
        
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
            self.color_index = 0
            self.notification_queue = deque()
            
            # Set window flags - fixed size with maximize/minimize
            self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | 
                               Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
            self.setFixedSize(self.base_width, self.base_height)
            self.setAttribute(Qt.WA_TranslucentBackground)
            
            self._setup_ui()
            self._setup_media_player()
            self._setup_animations()
            self._start_color_animation()
            
        def _start_color_animation(self):
            """Start color cycling animation"""
            self.color_timer = QTimer()
            self.color_timer.timeout.connect(self._cycle_colors)
            self.color_timer.start(3000)
            
        def _cycle_colors(self):
            """Cycle through color schemes"""
            self.color_index = (self.color_index + 1) % len(COLORS['primary'])
            self._update_accent_colors()
            
        def _update_accent_colors(self):
            """Update accent colors throughout the UI"""
            accent_color = COLORS['primary'][self.color_index]
            self.setStyleSheet(f"""
                QToolTip {{
                    background-color: #2d2d3d;
                    color: {accent_color};
                    border: 1px solid {accent_color};
                    border-radius: 5px;
                    padding: 5px;
                }}
            """)
            
        def _setup_ui(self):
            """Setup the main UI with colorful components"""
            central = AnimatedGradientWidget(['#1a1a2e', '#16213e', '#0f3460'])
            self.setCentralWidget(central)
            
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(20)
            
            # Custom Title Bar
            title_bar = self._create_title_bar()
            main_layout.addWidget(title_bar)
            
            # Main Content Card
            content_card = ModernCard(color="#1e1e2e")
            content_layout = QVBoxLayout(content_card)
            content_layout.setContentsMargins(25, 25, 25, 25)
            content_layout.setSpacing(20)
            
            # Header Section with animated gradient
            header = self._create_header()
            content_layout.addWidget(header)
            
            # Main Splitter
            splitter = QSplitter(Qt.Horizontal)
            splitter.setHandleWidth(3)
            splitter.setStyleSheet("""
                QSplitter::handle {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF6B35, stop:1 #F7931E);
                    border-radius: 2px;
                }
            """)
            
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
            """Create colorful title bar with window controls"""
            title_bar = QWidget()
            title_bar.setFixedHeight(55)
            title_bar.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(255,107,53,0.2),
                        stop:1 rgba(247,147,30,0.2));
                    border-radius: 15px;
                }
            """)
            
            layout = QHBoxLayout(title_bar)
            layout.setContentsMargins(15, 0, 10, 0)
            
            # App Logo and Title
            logo_label = QLabel("🎬")
            logo_label.setStyleSheet("font-size: 24px;")
            layout.addWidget(logo_label)
            
            title_label = QLabel("NotY Caption Generator AI v7.1")
            title_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: 'Segoe UI', 'Arial';
                    letter-spacing: 1px;
                }
            """)
            layout.addWidget(title_label)
            
            # Version badge
            version_badge = QLabel("PRO")
            version_badge.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:1 #F7931E);
                    color: white;
                    border-radius: 10px;
                    padding: 2px 8px;
                    font-size: 10px;
                    font-weight: bold;
                }
            """)
            layout.addWidget(version_badge)
            
            layout.addStretch()
            
            # Stats display
            self.stats_label = QLabel("🎯 Ready")
            self.stats_label.setStyleSheet("color: #FF6B35; font-size: 12px;")
            layout.addWidget(self.stats_label)
            
            layout.addSpacing(20)
            
            # Window Controls
            for name, color, hover_color, action in [
                ("─", "#2d2d3d", "#5d5d6d", self.showMinimized),
                ("□", "#2d2d3d", "#5d5d6d", self.showMaximized),
                ("✕", "#2d2d3d", "#e74c3c", self.close)
            ]:
                btn = QPushButton(name)
                btn.setFixedSize(40, 35)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {hover_color};
                    }}
                """)
                btn.clicked.connect(action)
                layout.addWidget(btn)
                
            return title_bar
            
        def _create_header(self):
            """Create animated header section"""
            header = QWidget()
            header.setFixedHeight(110)
            header.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:0.3 #F7931E, 
                        stop:0.7 #FF3366, stop:1 #FF6B35);
                    border-radius: 20px;
                }
            """)
            
            # Add pulsing animation to header
            self.header_animation = QPropertyAnimation(header, b"geometry")
            self.header_animation.setDuration(2000)
            self.header_animation.setStartValue(QRect(header.x(), header.y(), header.width(), header.height()))
            self.header_animation.setEndValue(QRect(header.x(), header.y()+2, header.width(), header.height()+4))
            self.header_animation.setLoopCount(-1)
            self.header_animation.start()
            
            layout = QHBoxLayout(header)
            layout.setContentsMargins(30, 0, 30, 0)
            
            # Left side - Animated welcome
            welcome_container = QWidget()
            welcome_layout = QVBoxLayout(welcome_container)
            
            welcome_label = QLabel("🎯 AI-Powered Subtitle Generator")
            welcome_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 22px;
                    font-weight: bold;
                    font-family: 'Segoe UI', 'Arial';
                }
            """)
            welcome_layout.addWidget(welcome_label)
            
            tagline = QLabel("Professional • Fast • Accurate")
            tagline.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 12px;")
            welcome_layout.addWidget(tagline)
            
            layout.addWidget(welcome_container)
            layout.addStretch()
            
            # Right side - Animated stats
            stats_container = QWidget()
            stats_layout = QVBoxLayout(stats_container)
            stats_layout.setAlignment(Qt.AlignRight)
            
            self.animated_stats = QLabel("✨ Ready to create magic")
            self.animated_stats.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            stats_layout.addWidget(self.animated_stats)
            
            self.sub_stats = QLabel("Powered by OpenAI Whisper")
            self.sub_stats.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 11px;")
            stats_layout.addWidget(self.sub_stats)
            
            layout.addWidget(stats_container)
            
            return header
            
        def _create_control_panel(self):
            """Create colorful control panel"""
            panel = QScrollArea()
            panel.setWidgetResizable(True)
            panel.setStyleSheet("""
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    background: rgba(255,255,255,0.1);
                    width: 10px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:1 #F7931E);
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF8866, stop:1 #F8A840);
                }
            """)
            
            content = QWidget()
            content.setStyleSheet("background-color: transparent;")
            layout = QVBoxLayout(content)
            layout.setSpacing(15)
            
            # Media Info Card
            media_card = ModernCard(color="#252535")
            media_layout = QVBoxLayout(media_card)
            media_layout.setContentsMargins(20, 20, 20, 20)
            media_layout.setSpacing(10)
            
            self.media_icon = QLabel("🎬")
            self.media_icon.setStyleSheet("font-size: 64px;")
            self.media_icon.setAlignment(Qt.AlignCenter)
            media_layout.addWidget(self.media_icon)
            
            self.media_label = QLabel("No Media Loaded")
            self.media_label.setStyleSheet("""
                QLabel {
                    color: #aaa;
                    font-size: 13px;
                    font-weight: bold;
                }
            """)
            self.media_label.setAlignment(Qt.AlignCenter)
            self.media_label.setWordWrap(True)
            media_layout.addWidget(self.media_label)
            
            layout.addWidget(media_card)
            
            # Import Buttons
            import_btn1 = ColorButton("📁 Import Media", 'primary', base_height=45)
            import_btn1.clicked.connect(self.import_media)
            layout.addWidget(import_btn1)
            
            import_btn2 = ColorButton("▶️ YouTube URL", 'danger', base_height=45)
            import_btn2.clicked.connect(self.import_youtube)
            layout.addWidget(import_btn2)
            
            # Settings Sections
            sections = [
                ("🎤 Whisper Model", self._create_model_section(), 'primary'),
                ("🌐 Language & Translation", self._create_language_section(), 'secondary'),
                ("🎵 Vocal Separation", self._create_vocal_section(), 'accent'),
                ("📝 Subtitle Format", self._create_break_section(), 'success'),
            ]
            
            for title, widget, color_scheme in sections:
                section = ModernCard(color="#252535")
                section_layout = QVBoxLayout(section)
                section_layout.setContentsMargins(15, 12, 15, 12)
                
                title_label = QLabel(title)
                title_label.setStyleSheet(f"""
                    QLabel {{
                        color: {COLORS[color_scheme][0]};
                        font-weight: bold;
                        font-size: 13px;
                        letter-spacing: 0.5px;
                    }}
                """)
                section_layout.addWidget(title_label)
                section_layout.addSpacing(5)
                section_layout.addWidget(widget)
                
                layout.addWidget(section)
            
            # Generate Button
            self.generate_btn = ColorButton("✨ GENERATE CAPTIONS", 'primary', base_height=55)
            self.generate_btn.clicked.connect(self.generate_captions)
            self.generate_btn.setEnabled(False)
            layout.addWidget(self.generate_btn)
            
            # Export Buttons
            export_layout = QHBoxLayout()
            self.export_srt_btn = ColorButton("📄 Export SRT", 'secondary', base_height=40)
            self.export_srt_btn.clicked.connect(lambda: self.export_subtitles('srt'))
            self.export_srt_btn.setEnabled(False)
            export_layout.addWidget(self.export_srt_btn)
            
            self.export_ass_btn = ColorButton("🎨 Export ASS", 'accent', base_height=40)
            self.export_ass_btn.clicked.connect(lambda: self.export_subtitles('ass'))
            self.export_ass_btn.setEnabled(False)
            export_layout.addWidget(self.export_ass_btn)
            
            layout.addLayout(export_layout)
            
            layout.addStretch()
            panel.setWidget(content)
            return panel
            
        def _create_model_section(self):
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.model_combo = QComboBox()
            models = [
                ('TINY', '⚡ Fastest'), 
                ('BASE', '🎯 Balanced'), 
                ('SMALL', '📈 Better'), 
                ('MEDIUM', '🚀 High'), 
                ('LARGE', '💎 Best')
            ]
            for model, desc in models:
                self.model_combo.addItem(f"{model} - {desc}")
            self.model_combo.setCurrentIndex(1)
            self.model_combo.setStyleSheet("""
                QComboBox {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2d2d3d, stop:1 #353545);
                    border: 1px solid #3d3d4d;
                    border-radius: 10px;
                    padding: 8px 12px;
                    color: white;
                    font-weight: bold;
                }
                QComboBox::drop-down {
                    border: none;
                    subcontrol-position: right;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #FF6B35;
                    margin-right: 10px;
                }
                QComboBox QAbstractItemView {
                    background: #2d2d3d;
                    border: 1px solid #FF6B35;
                    selection-background-color: #FF6B35;
                }
            """)
            layout.addWidget(self.model_combo)
            
            return widget
            
        def _create_language_section(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)
            
            self.lang_combo = QComboBox()
            languages = [
                ("🇺🇸 English", "en", "High"),
                ("🇪🇸 Spanish", "es", "High"),
                ("🇮🇹 Italian", "it", "High"),
                ("🇵🇹 Portuguese", "pt", "High"),
                ("🇩🇪 German", "de", "High"),
                ("🇯🇵 Japanese", "ja", "High"),
                ("🇫🇷 French", "fr", "High"),
                ("🇷🇺 Russian", "ru", "Medium"),
                ("🇮🇳 Hindi", "hi", "Low"),
                ("🇮🇳 Tamil", "ta", "Low"),
                ("🇮🇳 Bengali", "bn", "Low"),
                ("🇵🇰 Urdu", "ur", "Low"),
            ]
            for name, code, acc in languages:
                self.lang_combo.addItem(f"{name} - {acc} Accuracy", code)
            self.lang_combo.setStyleSheet("""
                QComboBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 10px;
                    padding: 8px;
                    color: white;
                }
            """)
            layout.addWidget(self.lang_combo)
            
            self.translate_check = QCheckBox("🔄 Translate to English (Auto-translate)")
            self.translate_check.setStyleSheet("""
                QCheckBox {
                    color: #ccc;
                    spacing: 10px;
                    font-size: 12px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 2px solid #FF6B35;
                    background-color: #2d2d3d;
                }
                QCheckBox::indicator:checked {
                    background-color: #FF6B35;
                    border: 2px solid #FF6B35;
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #F7931E;
                }
            """)
            layout.addWidget(self.translate_check)
            
            return widget
            
        def _create_vocal_section(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.vocal_combo = QComboBox()
            vocal_options = [
                ('None', 'Use original audio'),
                ('2stems', 'Vocals + Accompaniment'),
                ('4stems', 'Vocals + Drums + Bass + Other'),
                ('5stems', 'Vocals + Drums + Bass + Piano + Other')
            ]
            for option, desc in vocal_options:
                self.vocal_combo.addItem(f"{option} - {desc}")
            self.vocal_combo.setStyleSheet("""
                QComboBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 10px;
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
            layout.setSpacing(8)
            
            self.break_combo = QComboBox()
            self.break_combo.addItems(['🎯 Auto (Smart sentences)', '📝 Words', '📏 Letters'])
            self.break_combo.setStyleSheet("""
                QComboBox {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 10px;
                    padding: 8px;
                    color: white;
                }
            """)
            layout.addWidget(self.break_combo)
            
            limit_container = QWidget()
            limit_layout = QHBoxLayout(limit_container)
            limit_layout.setContentsMargins(0, 0, 0, 0)
            limit_layout.setSpacing(15)
            
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
                    min-width: 60px;
                }
            """)
            limit_layout.addWidget(QLabel("Words/line:"))
            limit_layout.addWidget(self.word_limit)
            
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
                    min-width: 60px;
                }
            """)
            limit_layout.addWidget(QLabel("Chars/line:"))
            limit_layout.addWidget(self.char_limit)
            
            limit_layout.addStretch()
            layout.addWidget(limit_container)
            
            self.break_combo.currentIndexChanged.connect(self._on_break_changed)
            
            return widget
            
        def _create_caption_panel(self):
            """Create caption editor panel with player"""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setSpacing(15)
            
            # Player Controls Card
            player_card = ModernCard(color="#252535")
            player_layout = QVBoxLayout(player_card)
            player_layout.setContentsMargins(15, 15, 15, 15)
            player_layout.setSpacing(10)
            
            # Time Slider
            self.time_slider = QSlider(Qt.Horizontal)
            self.time_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #2d2d3d;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:1 #F7931E);
                    width: 16px;
                    height: 16px;
                    margin: -5px 0;
                    border-radius: 8px;
                }
                QSlider::sub-page:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:1 #F7931E);
                    border-radius: 3px;
                }
            """)
            self.time_slider.sliderMoved.connect(self.seek_position)
            player_layout.addWidget(self.time_slider)
            
            # Control Buttons
            controls = QHBoxLayout()
            controls.setSpacing(10)
            
            self.play_btn = ColorButton("▶ Play", 'success', base_height=38)
            self.play_btn.setFixedWidth(100)
            self.play_btn.clicked.connect(self.toggle_playback)
            self.play_btn.setEnabled(False)
            controls.addWidget(self.play_btn)
            
            self.stop_btn = ColorButton("⏹ Stop", 'danger', base_height=38)
            self.stop_btn.setFixedWidth(100)
            self.stop_btn.clicked.connect(self.stop_playback)
            self.stop_btn.setEnabled(False)
            controls.addWidget(self.stop_btn)
            
            self.time_label = QLabel("00:00:00 / 00:00:00")
            self.time_label.setStyleSheet("""
                QLabel {
                    color: #FF6B35;
                    font-family: monospace;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            controls.addWidget(self.time_label)
            controls.addStretch()
            
            player_layout.addLayout(controls)
            layout.addWidget(player_card)
            
            # Caption Editor Card
            editor_card = ModernCard(color="#252535")
            editor_layout = QVBoxLayout(editor_card)
            editor_layout.setContentsMargins(15, 15, 15, 15)
            editor_layout.setSpacing(10)
            
            editor_header = QHBoxLayout()
            editor_header.addWidget(QLabel("📝 Caption Editor"))
            editor_header.addStretch()
            
            self.edit_mode_btn = QPushButton("✏️ Edit Mode")
            self.edit_mode_btn.setCheckable(True)
            self.edit_mode_btn.setStyleSheet("""
                QPushButton {
                    background: #2d2d3d;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 6px 15px;
                    color: #aaa;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background: #FF6B35;
                    color: white;
                    border: none;
                }
            """)
            self.edit_mode_btn.clicked.connect(self.toggle_edit_mode)
            editor_header.addWidget(self.edit_mode_btn)
            
            self.save_edit_btn = QPushButton("💾 Save Changes")
            self.save_edit_btn.setEnabled(False)
            self.save_edit_btn.setStyleSheet("""
                QPushButton {
                    background: #2ecc71;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 15px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    background: #555;
                }
                QPushButton:hover:enabled {
                    background: #27ae60;
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
                    border-radius: 12px;
                    padding: 15px;
                    color: #e0e0e0;
                    font-family: 'Consolas', 'Monaco', monospace;
                    line-height: 1.5;
                }
                QTextEdit:focus {
                    border: 1px solid #FF6B35;
                }
            """)
            self.caption_editor.setPlaceholderText("✨ Generated captions will appear here...\n\nClick 'Edit Mode' to make changes, then 'Save Changes' to keep them.")
            editor_layout.addWidget(self.caption_editor)
            
            layout.addWidget(editor_card)
            
            return panel
            
        def _create_progress_section(self):
            """Create animated progress section"""
            card = ModernCard(color="#252535")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(15, 12, 15, 12)
            
            self.progress_bar = PulsingProgressBar()
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
                        stop:0 #FF6B35, stop:0.5 #F7931E, stop:1 #FF3366);
                    border-radius: 10px;
                }
            """)
            layout.addWidget(self.progress_bar)
            
            self.progress_label = QLabel("")
            self.progress_label.setStyleSheet("color: #FF6B35; font-size: 12px; font-weight: bold;")
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
            self.fade_animation.setDuration(800)
            self.fade_animation.setStartValue(0)
            self.fade_animation.setEndValue(1)
            self.fade_animation.setEasingCurve(QEasingCurve.InOutCubic)
            self.fade_animation.start()
            
        def _on_break_changed(self, index):
            self.word_limit.setEnabled(index == 1)
            self.char_limit.setEnabled(index == 2)
            
        def resizeEvent(self, event: QResizeEvent):
            """Handle resize events - scale UI proportionally"""
            if self.isMaximized():
                screen = QApplication.primaryScreen().geometry()
                self.scale_factor = min(screen.width() / self.base_width, 
                                       screen.height() / self.base_height)
                self._scale_ui(self.scale_factor)
            else:
                self.scale_factor = 1.0
                self.setFixedSize(self.base_width, self.base_height)
                self._scale_ui(1.0)
            super().resizeEvent(event)
            
        def _scale_ui(self, factor):
            """Scale all UI elements proportionally"""
            for widget in self.findChildren(ColorButton):
                widget.resize_to_scale(factor)
                
            # Scale fonts for labels
            for label in self.findChildren(QLabel):
                if label not in [self.media_icon, self.animated_stats, self.sub_stats]:
                    font = label.font()
                    font.setPointSize(int(12 * factor))
                    label.setFont(font)
                    
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
                self.animated_stats.setText("📥 Downloading from YouTube...")
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
                    self.animated_stats.setText("✅ Download complete!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to download: {str(e)}")
                    self.animated_stats.setText("❌ Download failed")
                    
        def load_media(self, file_path):
            self.current_file = file_path
            self.media_label.setText(f"📹 {Path(file_path).name}")
            self.generate_btn.setEnabled(True)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.animated_stats.setText(f"🎬 Loaded: {Path(file_path).name}")
            
            # Animate media icon
            anim = QPropertyAnimation(self.media_icon, b"geometry")
            anim.setDuration(300)
            anim.setStartValue(self.media_icon.geometry())
            anim.setEndValue(QRect(self.media_icon.x(), self.media_icon.y()-10, 
                                   self.media_icon.width(), self.media_icon.height()))
            anim.setEasingCurve(QEasingCurve.OutBounce)
            anim.start()
            
        def generate_captions(self):
            if not self.current_file:
                return
                
            settings = {
                'model': self.model_combo.currentText().split('-')[0].strip().lower(),
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
            self.animated_stats.setText("🚀 Starting transcription...")
            
            self.worker = TranscriptionWorker(self.current_file, settings)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.on_transcription_finished)
            self.worker.error.connect(self.on_transcription_error)
            self.worker.start()
            
        def update_progress(self, value, message):
            self.progress_bar.setValue(value)
            self.progress_label.setText(message)
            self.animated_stats.setText(message)
            
        def on_transcription_finished(self, result):
            self.current_subtitles = result['subtitles']
            self.current_segments = result['segments']
            self.caption_editor.setText('\n'.join(self.current_subtitles))
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            self.generate_btn.setEnabled(True)
            self.export_srt_btn.setEnabled(True)
            self.export_ass_btn.setEnabled(True)
            
            # Success animation
            self.progress_label.setText("✅ Complete!")
            self.progress_label.setStyleSheet("color: #2ecc71; font-size: 14px; font-weight: bold;")
            self.progress_label.setVisible(True)
            self.animated_stats.setText(f"✨ Success! Generated {len(self.current_subtitles)} captions")
            QTimer.singleShot(2000, lambda: self.progress_label.setVisible(False))
            
            QMessageBox.information(self, "Success", 
                f"✨ Successfully generated {len(self.current_subtitles)} captions!\n\n"
                f"📝 You can now edit the captions and export them.")
            
        def on_transcription_error(self, error):
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            self.generate_btn.setEnabled(True)
            self.animated_stats.setText("❌ Transcription failed")
            QMessageBox.critical(self, "Error", f"❌ Transcription failed:\n\n{error}")
            
        def export_subtitles(self, format_type):
            if not self.current_subtitles:
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"Export {format_type.upper()}",
                f"captions.{format_type}",
                f"{format_type.upper()} Files (*.{format_type})"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.current_subtitles))
                self.animated_stats.setText(f"📄 Exported to {Path(file_path).name}")
                QMessageBox.information(self, "Success", f"✅ Exported to:\n{file_path}")
                
        def toggle_playback(self):
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                self.play_btn.setText("▶ Play")
                self.animated_stats.setText("⏸ Paused")
            else:
                self.media_player.play()
                self.play_btn.setText("⏸ Pause")
                self.animated_stats.setText("▶ Playing...")
                
        def stop_playback(self):
            self.media_player.stop()
            self.play_btn.setText("▶ Play")
            self.animated_stats.setText("⏹ Stopped")
            
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
            for i, caption in enumerate(self.current_subtitles):
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
                self.edit_mode_btn.setStyleSheet("background: #FF6B35; color: white; border: none;")
                self.animated_stats.setText("✏️ Edit mode enabled - make your changes")
            else:
                self.edit_mode_btn.setStyleSheet("background: #2d2d3d; color: #aaa;")
                self.animated_stats.setText("📖 View mode")
                
        def save_caption_edits(self):
            text = self.caption_editor.toPlainText()
            blocks = text.strip().split('\n\n')
            self.current_subtitles = [block + '\n' for block in blocks if block.strip()]
            self.save_edit_btn.setEnabled(False)
            self.edit_mode_btn.setChecked(False)
            self.caption_editor.setReadOnly(True)
            self.edit_mode_btn.setStyleSheet("background: #2d2d3d; color: #aaa;")
            self.animated_stats.setText("💾 Captions saved successfully!")
            QMessageBox.information(self, "Success", "✅ Captions saved successfully!")
            
        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton and event.y() < 55:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
                
        def mouseMoveEvent(self, event):
            if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position') and event.y() < 55:
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
    print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}     🎬 NotY Caption Generator AI v7.1 - Professional CLI Mode{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.YELLOW}⚠️  GUI mode not available. Install PyQt5 for the full experience.{Colors.ENDC}\n")
    
    cache = CacheManager()
    transcriber = Transcriber(cache)
    
    while True:
        print(f"\n{Colors.GREEN}{'='*50}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}  Main Menu{Colors.ENDC}")
        print(f"{Colors.GREEN}{'='*50}{Colors.ENDC}")
        print(f"{Colors.CYAN}  1.{Colors.ENDC} 🎬 Process Media File")
        print(f"{Colors.CYAN}  2.{Colors.ENDC} ▶️ Download YouTube Video")
        print(f"{Colors.CYAN}  3.{Colors.ENDC} ⚙️ Settings")
        print(f"{Colors.CYAN}  4.{Colors.ENDC} 🗑️ Clear Cache")
        print(f"{Colors.CYAN}  5.{Colors.ENDC} 📊 View Cache Stats")
        print(f"{Colors.CYAN}  6.{Colors.ENDC} 🚪 Exit")
        
        choice = input(f"\n{Colors.BOLD}Select option [1-6]: {Colors.ENDC}").strip()
        
        if choice == '1':
            file_path = input(f"{Colors.BOLD}📁 Enter file path: {Colors.ENDC}").strip().strip('"')
            path = Path(file_path)
            if not path.exists():
                print(f"{Colors.FAIL}❌ File not found!{Colors.ENDC}")
                continue
                
            print(f"\n{Colors.CYAN}📊 File: {path.name}{Colors.ENDC}")
            model = input(f"{Colors.BOLD}🎤 Model (tiny/base/small/medium/large) [base]: {Colors.ENDC}").strip() or 'base'
            language = input(f"{Colors.BOLD}🌐 Language code [en]: {Colors.ENDC}").strip() or 'en'
            translate = input(f"{Colors.BOLD}🔄 Translate to English? (y/n) [n]: {Colors.ENDC}").strip().lower() == 'y'
            
            print(f"\n{Colors.BLUE}🚀 Loading model...{Colors.ENDC}")
            transcriber.load_model(model)
            
            print(f"{Colors.BLUE}🎤 Transcribing...{Colors.ENDC}")
            task = 'translate' if translate else 'transcribe'
            segments = transcriber.transcribe(path, language, task, 
                progress_callback=lambda p,m: print(f"  {Colors.GREEN}{p:3d}%{Colors.ENDC} - {m}"))
            
            generator = SubtitleGenerator('auto', 10, 40)
            srt_content = generator.generate_srt(segments)
            
            output_path = path.with_suffix('.srt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
                
            print(f"\n{Colors.GREEN}{'='*50}{Colors.ENDC}")
            print(f"{Colors.GREEN}✅ SUCCESS!{Colors.ENDC}")
            print(f"{Colors.GREEN}📄 Subtitles saved to: {output_path}{Colors.ENDC}")
            print(f"{Colors.GREEN}{'='*50}{Colors.ENDC}")
            
        elif choice == '2':
            try:
                import yt_dlp
                url = input(f"{Colors.BOLD}▶️ Enter YouTube URL: {Colors.ENDC}").strip()
                if url:
                    print(f"{Colors.BLUE}📥 Downloading...{Colors.ENDC}")
                    temp_dir = Path(tempfile.gettempdir()) / 'NotYCaptionGenAI'
                    temp_dir.mkdir(exist_ok=True)
                    ydl_opts = {
                        'format': 'bestaudio/best', 
                        'outtmpl': str(temp_dir / '%(title)s.%(ext)s'), 
                        'quiet': True,
                        'progress_hooks': [lambda d: print(f"  {Colors.GREEN}⬇️ {d['status']}{Colors.ENDC}") if d['status'] == 'downloading' else None]
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                        print(f"{Colors.GREEN}✅ Downloaded: {filename}{Colors.ENDC}")
            except ImportError:
                print(f"{Colors.FAIL}❌ yt-dlp not installed. Run: pip install yt-dlp{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
                
        elif choice == '3':
            print(f"\n{Colors.CYAN}⚙️ Settings{Colors.ENDC}")
            print(f"{Colors.YELLOW}  Models folder: {MODELS_DIR}{Colors.ENDC}")
            print(f"{Colors.YELLOW}  Cache database: {CACHE_DB}{Colors.ENDC}")
            print(f"{Colors.YELLOW}  Logs folder: {LOGS_DIR}{Colors.ENDC}")
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
            
        elif choice == '4':
            confirm = input(f"{Colors.WARNING}⚠️ Clear all cached transcriptions? (y/n): {Colors.ENDC}").lower()
            if confirm == 'y':
                cache.clear_all()
                print(f"{Colors.GREEN}✅ Cache cleared!{Colors.ENDC}")
            else:
                print(f"{Colors.CYAN}Cancelled.{Colors.ENDC}")
                
        elif choice == '5':
            stats = cache.get_stats()
            print(f"\n{Colors.CYAN}📊 Cache Statistics:{Colors.ENDC}")
            print(f"  {Colors.GREEN}Entries:{Colors.ENDC} {stats['count']}")
            print(f"  {Colors.GREEN}Size:{Colors.ENDC} {stats['size'] / (1024*1024):.2f} MB")
            input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
                
        elif choice == '6':
            print(f"{Colors.GREEN}👋 Goodbye!{Colors.ENDC}")
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
        app.setStyle('Fusion')
        
        # Set global font
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        window = NotYCaptionWindow()
        window.show()
        
        sys.exit(app.exec_())
    else:
        run_cli()


if __name__ == "__main__":
    main()