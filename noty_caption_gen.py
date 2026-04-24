#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI v7.1 - Complete Professional Application
Copyright (c) 2026 NotY215

Features:
- Fully resizable window with smooth scrolling
- GPU-accelerated animations (60fps)
- Native media playback with audio support
- Cancel/Unload media functionality
- Smart language selection (no translate for English)
- Professional UI with modern design
- 5000+ lines of comprehensive code
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
import platform
import threading
import queue
import datetime
import math
import itertools
from pathlib import Path
from datetime import timedelta
from threading import Thread, Lock, Event
from typing import List, Dict, Optional, Tuple, Any, Callable
from enum import Enum
from functools import partial, wraps
from collections import deque, OrderedDict
from dataclasses import dataclass, field
from contextlib import contextmanager

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
CONFIG_FILE = APP_DATA_DIR / 'config.json'
THEMES_DIR = APP_DATA_DIR / 'themes'

# Create directories
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
THEMES_DIR.mkdir(parents=True, exist_ok=True)

# Add FFmpeg to PATH
if FFMPEG_DIR.exists():
    os.environ['PATH'] = str(FFMPEG_DIR) + os.pathsep + os.environ['PATH']

# Try to import PyQt5
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QFileDialog, QComboBox, QTextEdit, QSlider,
        QProgressBar, QGroupBox, QCheckBox, QSpinBox, QLineEdit, QDialog,
        QDialogButtonBox, QTabWidget, QMessageBox, QFrame, QScrollArea,
        QGridLayout, QSplitter, QStackedWidget, QToolTip, QSizePolicy,
        QGraphicsDropShadowEffect, QStyleFactory, QSpacerItem, QMenu,
        QAction, QToolBar, QSystemTrayIcon, QInputDialog, QApplication
    )
    from PyQt5.QtCore import (
        Qt, QThread, pyqtSignal, QTimer, QUrl, QSettings, QSize, QPropertyAnimation,
        QEasingCurve, QPoint, QRect, QParallelAnimationGroup, QSequentialAnimationGroup,
        QPointF, QDateTime, QEvent, QVariantAnimation, QDir, QStandardPaths,
        QAbstractAnimation, QObject, QMetaObject, Q_ARG, QRunnable, QThreadPool,
        QMutex, QWaitCondition, QLibraryInfo, QTranslator, QLocale
    )
    from PyQt5.QtGui import (
        QFont, QIcon, QPalette, QColor, QLinearGradient, QBrush, QPainter,
        QPen, QFontDatabase, QMovie, QPixmap, QPainterPath, QRegion, QResizeEvent,
        QGradient, QRadialGradient, QConicalGradient, QFontMetrics, QTransform,
        QDesktopServices, QCursor, QClipboard
    )
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaMetaData
    GUI_AVAILABLE = True
except ImportError as e:
    GUI_AVAILABLE = False
    print(f"PyQt5 not available: {e}. Install with: pip install PyQt5 PyQt5-tools PyQtMultimedia")
    
    # Try alternative import
    try:
        from PySide6.QtWidgets import *
        from PySide6.QtCore import *
        from PySide6.QtGui import *
        from PySide6.QtMultimedia import *
        GUI_AVAILABLE = True
        print("Using PySide6 as fallback")
    except ImportError:
        GUI_AVAILABLE = False
        print("No GUI framework available. Install PyQt5 or PySide6")

# ============================================================================
# SECTION 1: Utility Classes and Helpers (0-500 lines)
# ============================================================================

class Logger:
    """Advanced logging system with file rotation"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
            
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.log_file = LOGS_DIR / f"app_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        self.max_size = 10 * 1024 * 1024  # 10MB
        self.log_queue = queue.Queue()
        self.worker_thread = Thread(target=self._process_logs, daemon=True)
        self.worker_thread.start()
        
    def _process_logs(self):
        """Process logs in background thread"""
        while True:
            try:
                level, message, timestamp = self.log_queue.get(timeout=1)
                self._write_log(level, message, timestamp)
            except queue.Empty:
                continue
                
    def _write_log(self, level: str, message: str, timestamp: str):
        """Write log to file with rotation"""
        if self.log_file.exists() and self.log_file.stat().st_size > self.max_size:
            self._rotate_logs()
            
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
            
    def _rotate_logs(self):
        """Rotate log files"""
        for i in range(5, 0, -1):
            old = self.log_file.with_suffix(f".{i}.log")
            new = self.log_file.with_suffix(f".{i+1}.log")
            if old.exists():
                old.rename(new)
        if self.log_file.exists():
            self.log_file.rename(self.log_file.with_suffix(".1.log"))
            
    def log(self, level: str, message: str):
        """Log a message"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.log_queue.put((level, message, timestamp))
        
    def debug(self, message: str):
        self.log("DEBUG", message)
        
    def info(self, message: str):
        self.log("INFO", message)
        
    def warning(self, message: str):
        self.log("WARNING", message)
        
    def error(self, message: str):
        self.log("ERROR", message)
        
    def critical(self, message: str):
        self.log("CRITICAL", message)


class ConfigManager:
    """Configuration manager with JSON storage"""
    
    DEFAULT_CONFIG = {
        'app': {
            'version': '7.1',
            'first_run': True,
            'auto_update': True,
            'language': 'en',
            'theme': 'dark'
        },
        'transcription': {
            'default_model': 'base',
            'default_language': 'en',
            'auto_translate': False,
            'vocal_separation': 'none',
            'break_type': 'auto',
            'word_limit': 10,
            'char_limit': 40,
            'subtitle_style': 'modern'
        },
        'paths': {
            'models_dir': str(MODELS_DIR),
            'output_dir': str(Path.home() / 'Videos' / 'Subtitles'),
            'temp_dir': str(Path(tempfile.gettempdir()) / 'NotYCaptionGenAI')
        },
        'performance': {
            'threads': 4,
            'use_gpu': False,
            'cache_enabled': True,
            'cache_days': 30,
            'max_cache_size': 100
        },
        'ui': {
            'window_width': 1300,
            'window_height': 850,
            'splitter_sizes': [450, 850],
            'show_timestamps': True,
            'auto_scroll': True
        }
    }
    
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config = self.load()
        self.logger = Logger()
        
    def load(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    return self._merge_dicts(self.DEFAULT_CONFIG, loaded)
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
        return self.DEFAULT_CONFIG.copy()
        
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            
    def _merge_dicts(self, default: dict, custom: dict) -> dict:
        """Recursively merge dictionaries"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
        
    def get(self, key: str, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
        
    def set(self, key: str, value):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        target = self.config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save()
        
    def reset(self):
        """Reset to default configuration"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()


class CacheManager:
    """Advanced SQLite cache manager with compression and cleanup"""
    
    def __init__(self, db_path: Path = CACHE_DB):
        self.db_path = db_path
        self.logger = Logger()
        self._init_db()
        self._start_cleanup_scheduler()
        
    def _init_db(self):
        """Initialize database with optimized schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=-10000')  # 10MB cache
            conn.execute('PRAGMA temp_store=MEMORY')
            
            # Main transcriptions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id TEXT PRIMARY KEY,
                    file_hash TEXT NOT NULL,
                    model TEXT NOT NULL,
                    language TEXT NOT NULL,
                    task TEXT NOT NULL,
                    segments TEXT NOT NULL,
                    duration REAL DEFAULT 0,
                    file_name TEXT,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            ''')
            
            # Indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_hash ON transcriptions(file_hash, model, language, task)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_created ON transcriptions(created_at)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_accessed ON transcriptions(last_accessed)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_access_count ON transcriptions(access_count)')
            
            # Metadata table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Models table for tracking downloaded models
            conn.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    name TEXT PRIMARY KEY,
                    size INTEGER,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP
                )
            ''')
            
    def _start_cleanup_scheduler(self):
        """Start automatic cleanup scheduler"""
        def cleanup_worker():
            while True:
                time.sleep(86400)  # Run daily
                self.cleanup_old()
                
        cleanup_thread = Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        
    def get(self, file_path: Path, model: str, language: str, task: str) -> Optional[List[Dict]]:
        """Get cached transcription with access tracking"""
        file_hash = self._get_file_hash(file_path)
        cache_id = f"{file_hash}_{model}_{language}_{task}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT segments FROM transcriptions WHERE id = ?',
                (cache_id,)
            )
            row = cursor.fetchone()
            if row:
                # Update last accessed time and count
                conn.execute(
                    'UPDATE transcriptions SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1 WHERE id = ?',
                    (cache_id,)
                )
                self.logger.debug(f"Cache hit: {cache_id[:16]}")
                return json.loads(row[0])
        self.logger.debug(f"Cache miss: {cache_id[:16]}")
        return None
        
    def set(self, file_path: Path, model: str, language: str, task: str, 
            segments: List[Dict], duration: float = 0):
        """Cache transcription with compression"""
        file_hash = self._get_file_hash(file_path)
        cache_id = f"{file_hash}_{model}_{language}_{task}"
        
        # Compress segments (remove unnecessary data)
        compressed = []
        for seg in segments:
            compressed.append({
                's': seg['start'],
                'e': seg['end'],
                't': seg['text'][:500] if len(seg['text']) > 500 else seg['text']  # Truncate long text
            })
            
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO transcriptions 
                (id, file_hash, model, language, task, segments, duration, file_name, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cache_id, file_hash, model, language, task, json.dumps(compressed), 
                  duration, file_path.name, file_path.stat().st_size))
                  
        self.logger.info(f"Cached: {cache_id[:16]} ({len(segments)} segments)")
        
    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate fast file hash"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(65536), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    def cleanup_old(self, days: int = 30):
        """Remove old cache entries"""
        config = ConfigManager()
        cache_days = config.get('performance.cache_days', days)
        max_size = config.get('performance.max_cache_size', 100)
        
        with sqlite3.connect(self.db_path) as conn:
            # Remove old entries
            conn.execute('''
                DELETE FROM transcriptions 
                WHERE last_accessed < datetime('now', '-' || ? || ' days')
                AND id NOT IN (
                    SELECT id FROM transcriptions 
                    ORDER BY access_count DESC, last_accessed DESC
                    LIMIT ?
                )
            ''', (cache_days, max_size))
            
            # Vacuum if needed
            cursor = conn.execute("SELECT COUNT(*) FROM transcriptions")
            count = cursor.fetchone()[0]
            if count < max_size // 2:
                conn.execute('VACUUM')
                
    def clear_all(self):
        """Clear all cache"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM transcriptions')
        self.logger.info("Cache cleared")
        
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*), 
                    SUM(LENGTH(segments)), 
                    SUM(duration),
                    COUNT(DISTINCT model),
                    MAX(access_count)
                FROM transcriptions
            ''')
            count, size, total_duration, models, max_access = cursor.fetchone()
            
            cursor = conn.execute('''
                SELECT model, COUNT(*), AVG(access_count) 
                FROM transcriptions 
                GROUP BY model 
                ORDER BY COUNT(*) DESC
            ''')
            model_stats = cursor.fetchall()
            
            return {
                'count': count or 0,
                'size': size or 0,
                'duration': total_duration or 0,
                'models_count': models or 0,
                'max_access': max_access or 0,
                'model_stats': [{'model': m, 'count': c, 'avg_access': a} for m, c, a in model_stats]
            }
            
    def vacuum(self):
        """Optimize database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('VACUUM')
        self.logger.info("Database vacuumed")
        
    def search(self, query: str, limit: int = 50) -> List[Dict]:
        """Search cache entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT file_name, model, language, task, duration, created_at, access_count
                FROM transcriptions 
                WHERE file_name LIKE ? OR model LIKE ? OR language LIKE ?
                ORDER BY access_count DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            return [{'file_name': r[0], 'model': r[1], 'language': r[2], 
                    'task': r[3], 'duration': r[4], 'created': r[5], 'access': r[6]} 
                   for r in cursor.fetchall()]


class AudioAnalyzer:
    """Advanced audio analysis and processing"""
    
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.logger = Logger()
        
    def analyze(self, audio_path: Path) -> Dict:
        """Analyze audio file and return comprehensive metadata"""
        try:
            import wave
            import struct
            import numpy as np
            
            result = {
                'duration': 0,
                'sample_rate': 0,
                'channels': 0,
                'volume_db': -60,
                'peak_level': 0,
                'rms_level': 0,
                'bit_depth': 0,
                'codec': 'unknown'
            }
            
            # Try with wave module for WAV files
            if audio_path.suffix == '.wav':
                with wave.open(str(audio_path), 'rb') as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()
                    duration = frames / float(rate)
                    channels = wav.getnchannels()
                    sampwidth = wav.getsampwidth()
                    
                    result['duration'] = duration
                    result['sample_rate'] = rate
                    result['channels'] = channels
                    result['bit_depth'] = sampwidth * 8
                    
                    # Read samples for analysis
                    data = wav.readframes(min(frames, rate * 10))  # First 10 seconds
                    samples = np.frombuffer(data, dtype=np.int16 if sampwidth == 2 else np.int8)
                    
                    # Calculate statistics
                    rms = np.sqrt(np.mean(samples.astype(np.float64)**2))
                    peak = np.max(np.abs(samples))
                    volume_db = 20 * np.log10(rms / (2**(sampwidth*8-1)) + 1e-10)
                    
                    result['rms_level'] = float(rms / (2**(sampwidth*8-1)))
                    result['peak_level'] = float(peak / (2**(sampwidth*8-1)))
                    result['volume_db'] = float(volume_db)
                    
            else:
                # Use ffprobe for other formats
                cmd = [
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_streams', '-show_format', str(audio_path)
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.returncode == 0:
                    data = json.loads(proc.stdout)
                    if 'format' in data:
                        result['duration'] = float(data['format'].get('duration', 0))
                        result['codec'] = data['format'].get('format_name', 'unknown')
                    if 'streams' in data:
                        for stream in data['streams']:
                            if stream.get('codec_type') == 'audio':
                                result['sample_rate'] = int(stream.get('sample_rate', 0))
                                result['channels'] = int(stream.get('channels', 0))
                                result['bit_depth'] = int(stream.get('bits_per_sample', 0))
                                break
                                
            return result
            
        except Exception as e:
            self.logger.error(f"Audio analysis failed: {e}")
            return {'duration': 0, 'volume_db': -60}
            
    def normalize_audio(self, input_path: Path, output_path: Path, target_db: float = -3) -> Optional[Path]:
        """Normalize audio volume using loudnorm"""
        try:
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-af', f'loudnorm=I={target_db}:TP=-1:LRA=11:print_format=json',
                '-ar', '16000', '-ac', '1',
                '-y', str(output_path)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"Normalized: {input_path.name} -> {output_path.name}")
            return output_path
        except Exception as e:
            self.logger.error(f"Normalization failed: {e}")
            return None
            
    def extract_audio(self, video_path: Path, output_path: Path = None) -> Optional[Path]:
        """Extract audio from video file"""
        if output_path is None:
            output_path = video_path.with_suffix('.wav')
            
        cmd = [
            'ffmpeg', '-i', str(video_path),
            '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1',
            '-y', str(output_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"Extracted audio: {video_path.name} -> {output_path.name}")
            return output_path
        except Exception as e:
            self.logger.error(f"Audio extraction failed: {e}")
            return None
            
    def get_spectrogram(self, audio_path: Path, duration: float = 10) -> Optional[np.ndarray]:
        """Generate spectrogram for visualization"""
        try:
            import numpy as np
            import soundfile as sf
            
            data, sr = sf.read(str(audio_path))
            if len(data.shape) > 1:
                data = data.mean(axis=1)  # Convert to mono
                
            # Take first N seconds or whole file
            samples = min(int(duration * sr), len(data))
            data = data[:samples]
            
            # Compute spectrogram
            from scipy import signal
            f, t, Sxx = signal.spectrogram(data, sr, nperseg=256, noverlap=128)
            
            # Convert to dB scale
            Sxx_db = 10 * np.log10(Sxx + 1e-10)
            
            return Sxx_db
            
        except Exception as e:
            self.logger.error(f"Spectrogram generation failed: {e}")
            return None


class SubtitleStyler:
    """Advanced subtitle styling and formatting"""
    
    def __init__(self):
        self.logger = Logger()
        self.styles = {
            'classic': {
                'font': 'Arial',
                'size': 24,
                'color': '&H00FFFFFF',
                'secondary': '&H0000FF00',
                'outline': '&H00000000',
                'shadow': '&H80000000',
                'bold': 0,
                'italic': 0,
                'underline': 0,
                'alignment': 2
            },
            'modern': {
                'font': 'Segoe UI',
                'size': 28,
                'color': '&H00FFFF00',
                'secondary': '&H0000FF00',
                'outline': '&H00000000',
                'shadow': '&H40000000',
                'bold': 1,
                'italic': 0,
                'underline': 0,
                'alignment': 5
            },
            'cinematic': {
                'font': 'Helvetica',
                'size': 32,
                'color': '&H00FFFFFF',
                'secondary': '&H0000FF00',
                'outline': '&H00000000',
                'shadow': '&H00FF0000',
                'bold': 1,
                'italic': 0,
                'underline': 0,
                'alignment': 2
            },
            'neon': {
                'font': 'Impact',
                'size': 36,
                'color': '&H0000FFFF',
                'secondary': '&H0000FF00',
                'outline': '&H00000000',
                'shadow': '&H00FF00FF',
                'bold': 1,
                'italic': 0,
                'underline': 0,
                'alignment': 2
            },
            'subtle': {
                'font': 'Calibri',
                'size': 22,
                'color': '&H00CCCCCC',
                'secondary': '&H0000FF00',
                'outline': '&H00444444',
                'shadow': '&H20000000',
                'bold': 0,
                'italic': 1,
                'underline': 0,
                'alignment': 2
            }
        }
        
    def generate_ass(self, segments: List[Dict], style: str = 'modern', 
                     width: int = 1920, height: int = 1080) -> str:
        """Generate ASS with advanced styling"""
        style_config = self.styles.get(style, self.styles['modern'])
        
        # Calculate margins
        margin_v = int(height * 0.1)  # 10% from bottom
        margin_l = int(width * 0.05)   # 5% from left
        margin_r = int(width * 0.05)   # 5% from right
        
        header = f"""[Script Info]
Title: NotY Caption Generator AI
ScriptType: v4.00+
WrapStyle: 2
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style_config['font']},{style_config['size']},{style_config['color']},{style_config['secondary']},{style_config['outline']},{style_config['shadow']},{style_config['bold']},{style_config['italic']},{style_config['underline']},0,100,100,0,0,1,2,1,{style_config['alignment']},{margin_l},{margin_r},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        for seg in segments:
            start = self._format_time_ass(seg['start'])
            end = self._format_time_ass(seg['end'])
            text = self._apply_effects(seg['text'])
            events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
            
        return header + '\n'.join(events)
        
    def _apply_effects(self, text: str) -> str:
        """Apply text effects (karaoke, fade, etc.)"""
        words = text.split()
        if not words:
            return text
            
        # Add simple karaoke effect for first word
        first_word = words[0]
        rest = ' '.join(words[1:])
        
        # Apply different effects based on text length
        if len(words) <= 5:
            # Short line: add fade effect
            return f"{{\\fad(200,200)}}{{\\k50}}{first_word} {rest}"
        else:
            # Long line: add karaoke for pacing
            return f"{{\\k50}}{first_word} {rest}"
            
    def _format_time_ass(self, seconds: float) -> str:
        """Format time for ASS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        centiseconds = int((secs - int(secs)) * 100)
        return f"{hours}:{minutes:02d}:{int(secs):02d}.{centiseconds:02d}"
        
    def generate_srt_with_styles(self, segments: List[Dict], style: str = 'modern') -> str:
        """Generate styled SRT with HTML-like tags"""
        subtitles = []
        style_config = self.styles.get(style, self.styles['modern'])
        
        for i, seg in enumerate(segments, 1):
            start = self._format_time_srt(seg['start'])
            end = self._format_time_srt(seg['end'])
            
            # Apply HTML-like styling
            text = seg['text']
            text = f'<font color="{style_config["color"].replace("&H", "#")}">{text}</font>'
            
            subtitles.append(f"{i}\n{start} --> {end}\n{text}\n")
            
        return '\n'.join(subtitles)
        
    def _format_time_srt(self, seconds: float) -> str:
        """Format time for SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def preview_style(self, text: str, style: str) -> str:
        """Preview subtitle style with sample text"""
        style_config = self.styles.get(style, self.styles['modern'])
        return f"""[Style Preview]
Font: {style_config['font']}
Size: {style_config['size']}
Color: {style_config['color']}
Outline: {style_config['outline']}
Shadow: {style_config['shadow']}
Bold: {style_config['bold'] == 1}
Italic: {style_config['italic'] == 1}

Sample: {text}"""


# ============================================================================
# SECTION 2: CLI Mode Classes (500-1000 lines)
# ============================================================================

class Colors:
    """ANSI color codes for console output - Complete color palette"""
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKE = '\033[9m'
    
    RESET = '\033[0m'
    
    @classmethod
    def rainbow(cls, text: str) -> str:
        """Create rainbow colored text"""
        colors = [cls.RED, cls.YELLOW, cls.GREEN, cls.CYAN, cls.BLUE, cls.MAGENTA]
        result = ""
        for i, char in enumerate(text):
            if char != ' ':
                result += colors[i % len(colors)] + char
            else:
                result += char
        return result + cls.RESET
        
    @classmethod
    def gradient(cls, text: str, start_color: str, end_color: str) -> str:
        """Create gradient colored text"""
        # Simple gradient simulation
        result = ""
        steps = len(text)
        for i, char in enumerate(text):
            ratio = i / steps if steps > 0 else 0
            # Interpolate between colors (simplified)
            result += start_color + char
        return result + cls.RESET
        
    @classmethod
    def box(cls, text: str, color: str = CYAN, padding: int = 2) -> str:
        """Create a colored box around text"""
        lines = text.split('\n')
        max_len = max(len(line) for line in lines)
        horizontal = '─' * (max_len + padding * 2)
        
        result = f"{color}┌{horizontal}┐{cls.RESET}\n"
        for line in lines:
            result += f"{color}│{' ' * padding}{line}{' ' * (max_len - len(line) + padding)}│{cls.RESET}\n"
        result += f"{color}└{horizontal}┘{cls.RESET}"
        return result


class AnimatedProgressBar:
    """Advanced animated progress bar with smooth animation"""
    
    def __init__(self, total: int, prefix: str = '', suffix: str = '', length: int = 60):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0
        self.speed_history = deque(maxlen=10)
        self.spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.spinner_idx = 0
        
    def update(self, current: int = None):
        """Update progress with smooth animation"""
        if current is not None:
            self.current = current
        else:
            self.current += 1
            
        percent = 100 * (self.current / float(self.total))
        filled = int(self.length * self.current // self.total)
        
        # Create gradient bar
        bar_parts = []
        for i in range(self.length):
            if i < filled:
                if percent < 30:
                    char = f'{Colors.RED}█{Colors.RESET}'
                elif percent < 70:
                    char = f'{Colors.YELLOW}█{Colors.RESET}'
                else:
                    char = f'{Colors.GREEN}█{Colors.RESET}'
                bar_parts.append(char)
            else:
                bar_parts.append(f'{Colors.DIM}░{Colors.RESET}')
        bar = ''.join(bar_parts)
        
        # Calculate ETA and speed
        elapsed = time.time() - self.start_time
        if self.current > 0:
            rate = self.current / elapsed
            eta = (self.total - self.current) / rate if rate > 0 else 0
            eta_str = f"{int(eta//60):02d}:{int(eta%60):02d}"
            speed = rate * 100  # percent per second
            speed_str = f"{speed:5.1f}%/s"
        else:
            eta_str = "--:--"
            speed_str = "   ---%/s"
            
        # Spinner animation
        spinner_char = self.spinner[self.spinner_idx]
        self.spinner_idx = (self.spinner_idx + 1) % len(self.spinner)
        
        # Prepare output
        output = f"\r{self.prefix} {spinner_char} {bar} {percent:5.1f}% {self.suffix}"
        output += f" [{eta_str}] [{speed_str}]"
        
        sys.stdout.write(output)
        sys.stdout.flush()
        
    def finish(self):
        """Complete the progress bar"""
        self.update(self.total)
        elapsed = time.time() - self.start_time
        print(f"\n{Colors.GREEN}✓ Complete! Time: {int(elapsed//60)}m {int(elapsed%60)}s{Colors.RESET}")


class Transcriber:
    """Handles Whisper transcription with advanced features"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.model = None
        self.model_name = None
        self.logger = Logger()
        
    def load_model(self, model_name: str, progress_callback: Callable = None):
        """Load Whisper model with progress tracking"""
        if self.model_name == model_name and self.model is not None:
            if progress_callback:
                progress_callback(100, f"Model {model_name} already loaded")
            return
            
        try:
            import whisper
            
            if progress_callback:
                progress_callback(10, f"Loading {model_name.upper()} model...")
                
            model_path = MODELS_DIR / f"{model_name}.pt"
            if not model_path.exists():
                if progress_callback:
                    progress_callback(20, f"Downloading {model_name} model...")
                    
            self.model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
            self.model_name = model_name
            
            if progress_callback:
                progress_callback(100, f"Model {model_name.upper()} loaded")
                
            self.logger.info(f"Loaded model: {model_name}")
            
        except ImportError:
            raise RuntimeError("Whisper not installed. Run: pip install openai-whisper")
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            raise
            
    def transcribe(self, audio_path: Path, language: str, task: str = 'transcribe', 
                   use_cache: bool = True, progress_callback: Callable = None,
                   word_timestamps: bool = True, initial_prompt: str = None) -> List[Dict]:
        """Transcribe audio with advanced options"""
        
        # Check cache
        if use_cache:
            cached = self.cache_manager.get(audio_path, self.model_name, language, task)
            if cached:
                if progress_callback:
                    progress_callback(100, "Using cached transcription")
                self.logger.debug(f"Using cached transcription for {audio_path.name}")
                return cached
                
        if progress_callback:
            progress_callback(5, "🎵 Preparing audio...")
            
        # Prepare options
        options = {
            'language': language,
            'task': task,
            'verbose': False,
            'fp16': False,
            'word_timestamps': word_timestamps
        }
        
        # Add initial prompt if provided
        if initial_prompt:
            options['initial_prompt'] = initial_prompt
            
        if progress_callback:
            progress_callback(20, "🎤 AI is listening...")
            
        # Perform transcription
        try:
            result = self.model.transcribe(str(audio_path), **options)
            
            if progress_callback:
                progress_callback(70, "📝 Processing segments...")
                
            # Process segments with enhanced metadata
            segments = []
            for seg in result['segments']:
                segment = {
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip(),
                    'words': seg.get('words', []),
                    'confidence': seg.get('confidence', 0),
                    'no_speech_prob': seg.get('no_speech_prob', 0)
                }
                segments.append(segment)
                
            if progress_callback:
                progress_callback(90, "🎨 Formatting output...")
                
            # Cache results
            if use_cache:
                duration = segments[-1]['end'] if segments else 0
                self.cache_manager.set(audio_path, self.model_name, language, task, segments, duration)
                
            if progress_callback:
                progress_callback(100, "✅ Complete!")
                
            self.logger.info(f"Transcribed {audio_path.name}: {len(segments)} segments")
            return segments
            
        except Exception as e:
            self.logger.error(f"Transcription failed for {audio_path.name}: {e}")
            raise


class SubtitleGenerator:
    """Generates SRT/ASS subtitles with multiple formatting options"""
    
    def __init__(self, break_type: str = 'auto', word_limit: int = 10, char_limit: int = 40):
        self.break_type = break_type
        self.word_limit = word_limit
        self.char_limit = char_limit
        self.logger = Logger()
        
    def generate_srt(self, segments: List[Dict], merge_threshold: float = 0.3) -> str:
        """Generate SRT formatted subtitles with smart merging"""
        # Merge short segments
        merged_segments = self._merge_short_segments(segments, merge_threshold)
        
        subtitles = []
        for i, seg in enumerate(merged_segments, 1):
            text = self._apply_breaks(seg['text'])
            start = self._format_time_srt(seg['start'])
            end = self._format_time_srt(seg['end'])
            subtitles.append(f"{i}\n{start} --> {end}\n{text}\n")
            
        return '\n'.join(subtitles)
        
    def generate_vtt(self, segments: List[Dict]) -> str:
        """Generate WebVTT formatted subtitles"""
        header = "WEBVTT\n\n"
        subtitles = []
        
        for i, seg in enumerate(segments, 1):
            text = self._apply_breaks(seg['text'])
            start = self._format_time_vtt(seg['start'])
            end = self._format_time_vtt(seg['end'])
            subtitles.append(f"{i}\n{start} --> {end}\n{text}\n")
            
        return header + '\n'.join(subtitles)
        
    def _merge_short_segments(self, segments: List[Dict], threshold: float) -> List[Dict]:
        """Merge very short segments with adjacent ones"""
        if len(segments) <= 1:
            return segments
            
        merged = []
        current = segments[0].copy()
        
        for seg in segments[1:]:
            duration = seg['end'] - seg['start']
            if duration < threshold and len(current['text'].split()) < 5:
                # Merge short segment with previous
                current['end'] = seg['end']
                current['text'] += ' ' + seg['text']
            else:
                merged.append(current)
                current = seg.copy()
        merged.append(current)
        
        return merged
        
    def _apply_breaks(self, text: str) -> str:
        """Apply line breaks based on break type with intelligent wrapping"""
        if self.break_type == 'words':
            words = text.split()
            if len(words) <= self.word_limit:
                return text
                
            lines = []
            for i in range(0, len(words), self.word_limit):
                lines.append(' '.join(words[i:i + self.word_limit]))
            return '\\N'.join(lines)
            
        elif self.break_type == 'letters':
            if len(text) <= self.char_limit:
                return text
                
            lines = []
            for i in range(0, len(text), self.char_limit):
                # Try to break at word boundaries
                chunk = text[i:i + self.char_limit]
                if i + self.char_limit < len(text):
                    last_space = chunk.rfind(' ')
                    if last_space > 0:
                        chunk = chunk[:last_space]
                        i -= (self.char_limit - last_space)
                lines.append(chunk.strip())
            return '\\N'.join(lines)
            
        else:  # auto - smart sentence detection
            # Split by punctuation
            sentences = re.split(r'(?<=[.!?])\s+', text)
            if len(sentences) <= 2:
                return text
                
            # Group sentences into lines of 2-3
            lines = []
            current_line = []
            char_count = 0
            
            for sentence in sentences:
                if char_count + len(sentence) <= 60 or len(current_line) < 2:
                    current_line.append(sentence)
                    char_count += len(sentence)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [sentence]
                    char_count = len(sentence)
                    
            if current_line:
                lines.append(' '.join(current_line))
                
            return '\\N'.join(lines)
            
    def _format_time_srt(self, seconds: float) -> str:
        """Format time for SRT (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def _format_time_vtt(self, seconds: float) -> str:
        """Format time for WebVTT (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', '.')


class NotyCaptionCLI:
    """Complete CLI application with advanced features"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.cache = CacheManager()
        self.analyzer = AudioAnalyzer()
        self.transcriber = Transcriber(self.cache)
        self.styler = SubtitleStyler()
        self.logger = Logger()
        self.current_file = None
        self.settings = {
            'model': self.config.get('transcription.default_model', 'base'),
            'language': self.config.get('transcription.default_language', 'en'),
            'task': 'translate' if self.config.get('transcription.auto_translate') else 'transcribe',
            'vocal_separation': self.config.get('transcription.vocal_separation', 'none'),
            'break_type': self.config.get('transcription.break_type', 'auto'),
            'word_limit': self.config.get('transcription.word_limit', 10),
            'char_limit': self.config.get('transcription.char_limit', 40),
            'subtitle_style': self.config.get('transcription.subtitle_style', 'modern')
        }
        
    def print_banner(self):
        """Print animated banner"""
        banner = f"""
{Colors.BRIGHT_CYAN}{'█' * 80}{Colors.RESET}
{Colors.rainbow('   ███╗   ██╗ ██████╗ ████████╗██╗   ██╗   ██████╗ █████╗ ██████╗ ████████╗██╗ ██████╗ ███╗   ██╗')}
{Colors.rainbow('   ████╗  ██║██╔═══██╗╚══██╔══╝╚██╗ ██╔╝  ██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██║██╔════╝ ████╗  ██║')}
{Colors.rainbow('   ██╔██╗ ██║██║   ██║   ██║    ╚████╔╝   ██║     ███████║██████╔╝   ██║   ██║██║  ███╗██╔██╗ ██║')}
{Colors.rainbow('   ██║╚██╗██║██║   ██║   ██║     ╚██╔╝    ██║     ██╔══██║██╔══██╗   ██║   ██║██║   ██║██║╚██╗██║')}
{Colors.rainbow('   ██║ ╚████║╚██████╔╝   ██║      ██║     ╚██████╗██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║')}
{Colors.rainbow('   ╚═╝  ╚═══╝ ╚═════╝    ╚═╝      ╚═╝      ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝')}
{Colors.BRIGHT_CYAN}{'█' * 80}{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_YELLOW}                    Professional AI-Powered Subtitle Generator v7.1{Colors.RESET}
{Colors.BRIGHT_CYAN}{'█' * 80}{Colors.RESET}
        """
        print(banner)
        
    def print_menu(self, title: str, options: List[Tuple[str, str]]) -> str:
        """Print formatted menu"""
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}  {title}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}")
        
        for i, (text, value) in enumerate(options, 1):
            icon = text[0] if text else "•"
            print(f"{Colors.BRIGHT_GREEN}{i:2}.{Colors.RESET} {Colors.WHITE}{text}{Colors.RESET}")
            
        print(f"{Colors.BRIGHT_CYAN}{'─' * 60}{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}  0.{Colors.RESET} {Colors.ITALIC}Back / Cancel{Colors.RESET}")
        print(f"{Colors.BRIGHT_RED}  Q.{Colors.RESET} {Colors.ITALIC}Quit{Colors.RESET}")
        
        return input(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Select option: {Colors.RESET}").strip().lower()
        
    def select_file(self) -> Optional[Path]:
        """Select media file interactively"""
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_BLUE}📁 Select Media File{Colors.RESET}")
        
        # Show current directory files
        media_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.flac', '.m4a', '.m4v', '.webm']
        media_files = [f for f in Path.cwd().iterdir() if f.suffix.lower() in media_extensions]
        
        if media_files:
            print(f"\n{Colors.BRIGHT_GREEN}Media files in current directory:{Colors.RESET}")
            for i, file in enumerate(media_files[:15], 1):
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"{Colors.BRIGHT_GREEN}{i:2}.{Colors.RESET} {Colors.WHITE}{file.name}{Colors.RESET} {Colors.DIM}({size_mb:.1f} MB){Colors.RESET}")
                
            choice = input(f"\n{Colors.BOLD}Enter number or file path: {Colors.RESET}").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(media_files):
                return media_files[int(choice) - 1]
            elif Path(choice).exists():
                return Path(choice)
                
        # Manual input
        path = input(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}Enter file path: {Colors.RESET}").strip().strip('"')
        return Path(path) if Path(path).exists() else None
        
    def download_youtube(self) -> Optional[Path]:
        """Download YouTube video with progress"""
        try:
            import yt_dlp
            
            url = input(f"{Colors.BOLD}{Colors.BRIGHT_RED}▶️ Enter YouTube URL: {Colors.RESET}").strip()
            if not url:
                return None
                
            print(f"\n{Colors.BRIGHT_BLUE}📥 Downloading from YouTube...{Colors.RESET}")
            
            temp_dir = Path(tempfile.gettempdir()) / 'NotYCaptionGenAI'
            temp_dir.mkdir(exist_ok=True)
            
            # Find available filename
            base_name = "youtube_audio"
            counter = 1
            while (temp_dir / f"{base_name}_{counter}.mp3").exists():
                counter += 1
            output_path = temp_dir / f"{base_name}_{counter}.mp3"
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                        speed = d.get('speed', 0) / 1024 / 1024
                        print(f"\r  {Colors.BRIGHT_CYAN}⬇️ Downloading:{Colors.RESET} {percent:5.1f}% {Colors.DIM}({speed:.1f} MB/s){Colors.RESET}", end='')
                    elif 'total_bytes_estimate' in d:
                        percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                        print(f"\r  {Colors.BRIGHT_CYAN}⬇️ Downloading:{Colors.RESET} {percent:5.1f}%", end='')
                elif d['status'] == 'finished':
                    print(f"\n  {Colors.BRIGHT_GREEN}✓ Download complete!{Colors.RESET}")
                    
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_path.with_suffix('')),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
                
            if output_path.exists():
                print(f"{Colors.BRIGHT_GREEN}✓ Downloaded: {output_path.name}{Colors.RESET}")
                return output_path
            else:
                raise Exception("Output file not found")
                
        except ImportError:
            print(f"{Colors.BRIGHT_RED}❌ yt-dlp not installed. Run: pip install yt-dlp{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}❌ Error: {e}{Colors.RESET}")
            
        return None
        
    def configure_settings(self):
        """Interactive settings configuration"""
        while True:
            options = [
                (f"🎤 Whisper Model: {self.settings['model'].upper()}", "model"),
                (f"🌐 Language: {self.settings['language']}", "language"),
                (f"🔄 Mode: {'Translate' if self.settings['task'] == 'translate' else 'Transcribe'}", "task"),
                (f"🎵 Vocal Separation: {self.settings['vocal_separation']}", "vocal"),
                (f"📝 Subtitle Format: {self.settings['break_type']}", "break"),
                (f"🎨 Subtitle Style: {self.settings['subtitle_style']}", "style"),
                (f"💾 Save as Default", "save"),
            ]
            
            choice = self.print_menu("Settings", options)
            
            if choice == '0':
                break
            elif choice == 'model':
                models = [
                    ("tiny - Fastest (1GB)", "tiny"),
                    ("base - Balanced (1.5GB)", "base"),
                    ("small - Good (2GB)", "small"),
                    ("medium - High Quality (3GB)", "medium"),
                    ("large - Best Quality (5GB)", "large")
                ]
                print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Select Model:{Colors.RESET}")
                for i, (desc, code) in enumerate(models, 1):
                    print(f"  {Colors.BRIGHT_GREEN}{i}.{Colors.RESET} {desc}")
                model_choice = input(f"\n{Colors.BOLD}Choice [1-5]: {Colors.RESET}").strip()
                model_map = {str(i): code for i, (_, code) in enumerate(models, 1)}
                if model_choice in model_map:
                    self.settings['model'] = model_map[model_choice]
                    
            elif choice == 'language':
                languages = [
                    ("🇺🇸 English", "en"), ("🇪🇸 Spanish", "es"), ("🇮🇹 Italian", "it"),
                    ("🇵🇹 Portuguese", "pt"), ("🇩🇪 German", "de"), ("🇯🇵 Japanese", "ja"),
                    ("🇫🇷 French", "fr"), ("🇷🇺 Russian", "ru"), ("🇮🇳 Hindi", "hi"),
                    ("🇮🇳 Tamil", "ta"), ("🇮🇳 Bengali", "bn"), ("🇵🇰 Urdu", "ur")
                ]
                print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Select Language:{Colors.RESET}")
                for i, (name, code) in enumerate(languages, 1):
                    print(f"  {Colors.BRIGHT_GREEN}{i:2}.{Colors.RESET} {name}")
                lang_choice = input(f"\n{Colors.BOLD}Choice [1-{len(languages)}]: {Colors.RESET}").strip()
                if lang_choice.isdigit() and 1 <= int(lang_choice) <= len(languages):
                    self.settings['language'] = languages[int(lang_choice)-1][1]
                    
            elif choice == 'task':
                print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Select Mode:{Colors.RESET}")
                print(f"  {Colors.BRIGHT_GREEN}1.{Colors.RESET} Transcribe (Keep original language)")
                print(f"  {Colors.BRIGHT_GREEN}2.{Colors.RESET} Translate (Translate to English)")
                task_choice = input(f"\n{Colors.BOLD}Choice [1-2]: {Colors.RESET}").strip()
                if task_choice == '2':
                    self.settings['task'] = 'translate'
                else:
                    self.settings['task'] = 'transcribe'
                    
            elif choice == 'vocal':
                vocal_options = ["none", "2stems", "4stems", "5stems"]
                print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Select Vocal Separation:{Colors.RESET}")
                for i, opt in enumerate(vocal_options, 1):
                    print(f"  {Colors.BRIGHT_GREEN}{i}.{Colors.RESET} {opt}")
                vocal_choice = input(f"\n{Colors.BOLD}Choice [1-4]: {Colors.RESET}").strip()
                if vocal_choice.isdigit() and 1 <= int(vocal_choice) <= 4:
                    self.settings['vocal_separation'] = vocal_options[int(vocal_choice)-1]
                    
            elif choice == 'break':
                print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Select Line Break Type:{Colors.RESET}")
                print(f"  {Colors.BRIGHT_GREEN}1.{Colors.RESET} Auto (Smart sentence detection)")
                print(f"  {Colors.BRIGHT_GREEN}2.{Colors.RESET} Words (Break by word count)")
                print(f"  {Colors.BRIGHT_GREEN}3.{Colors.RESET} Letters (Break by character limit)")
                break_choice = input(f"\n{Colors.BOLD}Choice [1-3]: {Colors.RESET}").strip()
                if break_choice == '1':
                    self.settings['break_type'] = 'auto'
                elif break_choice == '2':
                    self.settings['break_type'] = 'words'
                    word_limit = input(f"{Colors.BRIGHT_CYAN}Words per line [10]: {Colors.RESET}").strip()
                    self.settings['word_limit'] = int(word_limit) if word_limit else 10
                elif break_choice == '3':
                    self.settings['break_type'] = 'letters'
                    char_limit = input(f"{Colors.BRIGHT_CYAN}Characters per line [40]: {Colors.RESET}").strip()
                    self.settings['char_limit'] = int(char_limit) if char_limit else 40
                    
            elif choice == 'style':
                styles = ["classic", "modern", "cinematic", "neon", "subtle"]
                print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}Select Subtitle Style:{Colors.RESET}")
                for i, style in enumerate(styles, 1):
                    print(f"  {Colors.BRIGHT_GREEN}{i}.{Colors.RESET} {style}")
                style_choice = input(f"\n{Colors.BOLD}Choice [1-5]: {Colors.RESET}").strip()
                if style_choice.isdigit() and 1 <= int(style_choice) <= 5:
                    self.settings['subtitle_style'] = styles[int(style_choice)-1]
                    
            elif choice == 'save':
                # Save to config
                self.config.set('transcription.default_model', self.settings['model'])
                self.config.set('transcription.default_language', self.settings['language'])
                self.config.set('transcription.auto_translate', self.settings['task'] == 'translate')
                self.config.set('transcription.vocal_separation', self.settings['vocal_separation'])
                self.config.set('transcription.break_type', self.settings['break_type'])
                self.config.set('transcription.word_limit', self.settings['word_limit'])
                self.config.set('transcription.char_limit', self.settings['char_limit'])
                self.config.set('transcription.subtitle_style', self.settings['subtitle_style'])
                print(f"\n{Colors.BRIGHT_GREEN}✓ Settings saved as default!{Colors.RESET}")
                
    def process_file(self, input_path: Path):
        """Process a single media file with full pipeline"""
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}{'█' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}  Processing: {input_path.name}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{'█' * 80}{Colors.RESET}")
        
        try:
            # Analyze audio first
            print(f"\n{Colors.BRIGHT_BLUE}🎵 Analyzing audio...{Colors.RESET}")
            analysis = self.analyzer.analyze(input_path)
            if analysis['duration'] > 0:
                duration_min = analysis['duration'] / 60
                print(f"  {Colors.BRIGHT_CYAN}Duration:{Colors.RESET} {duration_min:.1f} minutes ({analysis['duration']:.0f}s)")
                print(f"  {Colors.BRIGHT_CYAN}Sample Rate:{Colors.RESET} {analysis['sample_rate']} Hz")
                print(f"  {Colors.BRIGHT_CYAN}Channels:{Colors.RESET} {analysis['channels']}")
                print(f"  {Colors.BRIGHT_CYAN}Volume:{Colors.RESET} {analysis['volume_db']:.1f} dB")
                
            # Load model
            print(f"\n{Colors.BRIGHT_BLUE}🎤 Loading Whisper model ({self.settings['model'].upper()})...{Colors.RESET}")
            
            def model_callback(percent, message):
                print(f"  {percent}% - {message}")
                
            self.transcriber.load_model(self.settings['model'], model_callback)
            
            # Process transcription
            print(f"\n{Colors.BRIGHT_BLUE}🎤 Transcribing...{Colors.RESET}")
            progress = AnimatedProgressBar(100, prefix="Progress:", suffix="Complete", length=60)
            
            def transcribe_callback(percent, message):
                progress.update(percent)
                
            segments = self.transcriber.transcribe(
                input_path,
                self.settings['language'],
                self.settings['task'],
                progress_callback=transcribe_callback
            )
            progress.finish()
            
            # Generate subtitles
            print(f"\n{Colors.BRIGHT_BLUE}📝 Generating subtitles...{Colors.RESET}")
            generator = SubtitleGenerator(
                self.settings['break_type'],
                self.settings['word_limit'],
                self.settings['char_limit']
            )
            
            # Generate multiple formats
            srt_content = generator.generate_srt(segments)
            vtt_content = generator.generate_vtt(segments)
            ass_content = self.styler.generate_ass(segments, self.settings['subtitle_style'])
            
            # Save files
            output_base = input_path.parent / input_path.stem
            srt_path = output_base.with_suffix('.srt')
            vtt_path = output_base.with_suffix('.vtt')
            ass_path = output_base.with_suffix('.ass')
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            with open(vtt_path, 'w', encoding='utf-8') as f:
                f.write(vtt_content)
            with open(ass_path, 'w', encoding='utf-8') as f:
                f.write(ass_content)
                
            # Print summary
            print(f"\n{Colors.BRIGHT_GREEN}{'█' * 80}{Colors.RESET}")
            print(f"{Colors.BRIGHT_GREEN}✅ SUCCESS!{Colors.RESET}")
            print(f"{Colors.BRIGHT_GREEN}{'█' * 80}{Colors.RESET}")
            print(f"  {Colors.BRIGHT_CYAN}📄 SRT:{Colors.RESET} {srt_path}")
            print(f"  {Colors.BRIGHT_CYAN}📄 VTT:{Colors.RESET} {vtt_path}")
            print(f"  {Colors.BRIGHT_CYAN}🎨 ASS:{Colors.RESET} {ass_path}")
            print(f"  {Colors.BRIGHT_CYAN}📊 Segments:{Colors.RESET} {len(segments)}")
            print(f"  {Colors.BRIGHT_CYAN}⏱️  Duration:{Colors.RESET} {analysis['duration']:.1f}s")
            print(f"  {Colors.BRIGHT_CYAN}🎤 Model:{Colors.RESET} {self.settings['model']}")
            print(f"  {Colors.BRIGHT_CYAN}🌐 Language:{Colors.RESET} {self.settings['language']}")
            print(f"  {Colors.BRIGHT_CYAN}🎨 Style:{Colors.RESET} {self.settings['subtitle_style']}")
            print(f"{Colors.BRIGHT_GREEN}{'█' * 80}{Colors.RESET}")
            
            # Log success
            self.logger.info(f"Successfully processed {input_path.name}: {len(segments)} segments")
            
        except Exception as e:
            print(f"\n{Colors.BRIGHT_RED}❌ ERROR: {e}{Colors.RESET}")
            self.logger.error(f"Failed to process {input_path.name}: {e}")
            
    def run(self):
        """Main CLI application loop"""
        self.print_banner()
        
        while True:
            options = [
                ("🎬 Process Media File", "process"),
                ("▶️ Download YouTube Video", "youtube"),
                ("⚙️ Settings", "settings"),
                ("🗑️ Clear Cache", "clear"),
                ("📊 View Statistics", "stats"),
                ("🔍 Search Cache", "search"),
                ("💾 Database Vacuum", "vacuum"),
                ("ℹ️ About", "about"),
                ("🚪 Exit", "exit")
            ]
            
            choice = self.print_menu("Main Menu", options)
            
            if choice == '0' or choice == 'q':
                print(f"\n{Colors.BRIGHT_GREEN}👋 Goodbye!{Colors.RESET}")
                break
            elif choice == 'process':
                file_path = self.select_file()
                if file_path:
                    self.process_file(file_path)
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == 'youtube':
                file_path = self.download_youtube()
                if file_path:
                    self.process_file(file_path)
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == 'settings':
                self.configure_settings()
            elif choice == 'clear':
                confirm = input(f"{Colors.BRIGHT_YELLOW}⚠️ Clear all cache? (y/n): {Colors.RESET}").lower()
                if confirm == 'y':
                    self.cache.clear_all()
                    print(f"{Colors.BRIGHT_GREEN}✓ Cache cleared{Colors.RESET}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == 'stats':
                stats = self.cache.get_stats()
                print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}📊 Cache Statistics{Colors.RESET}")
                print(f"  {Colors.BRIGHT_GREEN}Cached entries:{Colors.RESET} {stats['count']}")
                print(f"  {Colors.BRIGHT_GREEN}Total size:{Colors.RESET} {stats['size'] / (1024*1024):.2f} MB")
                print(f"  {Colors.BRIGHT_GREEN}Audio duration:{Colors.RESET} {stats['duration'] / 3600:.1f} hours")
                print(f"  {Colors.BRIGHT_GREEN}Unique models:{Colors.RESET} {stats['models_count']}")
                print(f"  {Colors.BRIGHT_GREEN}Max access count:{Colors.RESET} {stats['max_access']}")
                
                if stats['model_stats']:
                    print(f"\n  {Colors.BRIGHT_CYAN}Model breakdown:{Colors.RESET}")
                    for ms in stats['model_stats']:
                        print(f"    • {ms['model']}: {ms['count']} entries (avg access: {ms['avg_access']:.1f})")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == 'search':
                query = input(f"{Colors.BRIGHT_CYAN}🔍 Search query: {Colors.RESET}").strip()
                if query:
                    results = self.cache.search(query)
                    print(f"\n{Colors.BRIGHT_GREEN}Found {len(results)} results:{Colors.RESET}")
                    for r in results:
                        print(f"  • {r['file_name']} ({r['model']}, {r['language']}) - Accessed {r['access']} times")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == 'vacuum':
                print(f"{Colors.BRIGHT_BLUE}Optimizing database...{Colors.RESET}")
                self.cache.vacuum()
                print(f"{Colors.BRIGHT_GREEN}✓ Database optimized{Colors.RESET}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            elif choice == 'about':
                about_text = f"""
{Colors.BRIGHT_CYAN}═══════════════════════════════════════════════════════════════{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_YELLOW}           NotY Caption Generator AI v7.1{Colors.RESET}
{Colors.BRIGHT_CYAN}═══════════════════════════════════════════════════════════════{Colors.RESET}

{Colors.BRIGHT_GREEN}📝 Description:{Colors.RESET}
  Professional AI-powered subtitle generation using OpenAI Whisper

{Colors.BRIGHT_GREEN}✨ Features:{Colors.RESET}
  • Multiple Whisper models (tiny to large)
  • 20+ languages with accuracy tiers
  • Vocal separation (2/4/5 stems)
  • YouTube download support
  • Smart subtitle formatting
  • SQLite caching for speed
  • Multiple output formats (SRT/VTT/ASS)

{Colors.BRIGHT_GREEN}👨‍💻 Developer:{Colors.RESET} NotY215
{Colors.BRIGHT_GREEN}📧 Contact:{Colors.RESET} https://t.me/Noty_215
{Colors.BRIGHT_GREEN}📺 YouTube:{Colors.RESET} https://www.youtube.com/@NotY215
{Colors.BRIGHT_GREEN}📜 License:{Colors.RESET} LGPL-3.0

{Colors.BRIGHT_CYAN}═══════════════════════════════════════════════════════════════{Colors.RESET}
                """
                print(about_text)
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")


# ============================================================================
# SECTION 3: GUI Mode Classes (1000-2000+ lines)
# ============================================================================

if GUI_AVAILABLE:
    
    class SmoothScrollArea(QScrollArea):
        """Smooth scrolling scroll area with inertia and wheel acceleration"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWidgetResizable(True)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.setFrameShape(QFrame.NoFrame)
            
            # Smooth scrolling animation
            self.scroll_animation = QVariantAnimation()
            self.scroll_animation.setDuration(400)
            self.scroll_animation.setEasingCurve(QEasingCurve.OutCubic)
            self.scroll_animation.valueChanged.connect(self._do_scroll)
            
            # Momentum variables
            self._velocity = 0
            self._last_wheel_time = 0
            self._last_wheel_pos = 0
            self._momentum_timer = QTimer()
            self._momentum_timer.setSingleShot(True)
            self._momentum_timer.timeout.connect(self._apply_momentum)
            
        def _do_scroll(self, value):
            self.verticalScrollBar().setValue(int(value))
            
        def _apply_momentum(self):
            """Apply scrolling momentum"""
            if abs(self._velocity) > 1:
                current = self.verticalScrollBar().value()
                target = current + self._velocity
                target = max(0, min(target, self.verticalScrollBar().maximum()))
                
                self.scroll_animation.setStartValue(current)
                self.scroll_animation.setEndValue(target)
                self.scroll_animation.start()
                
                self._velocity *= 0.95  # Decay
                self._momentum_timer.start(16)  # ~60fps
            else:
                self._velocity = 0
                
        def wheelEvent(self, event):
            current_time = time.time() * 1000
            delta = event.angleDelta().y()
            
            # Calculate velocity for momentum
            if self._last_wheel_time > 0:
                time_diff = current_time - self._last_wheel_time
                if time_diff > 0:
                    self._velocity = delta / time_diff * 10
                    
            self._last_wheel_time = current_time
            
            # Smooth scroll
            current = self.verticalScrollBar().value()
            scroll_amount = -delta / 3
            target = max(0, min(current + scroll_amount, self.verticalScrollBar().maximum()))
            
            self.scroll_animation.setStartValue(current)
            self.scroll_animation.setEndValue(target)
            self.scroll_animation.start()
            
            # Start momentum timer
            self._momentum_timer.start(100)
            
            event.accept()
            
        def scroll_to_bottom(self):
            """Smooth scroll to bottom"""
            target = self.verticalScrollBar().maximum()
            current = self.verticalScrollBar().value()
            self.scroll_animation.setStartValue(current)
            self.scroll_animation.setEndValue(target)
            self.scroll_animation.start()
            
        def scroll_to_top(self):
            """Smooth scroll to top"""
            target = 0
            current = self.verticalScrollBar().value()
            self.scroll_animation.setStartValue(current)
            self.scroll_animation.setEndValue(target)
            self.scroll_animation.start()
            
        def scroll_to_widget(self, widget: QWidget):
            """Smooth scroll to make widget visible"""
            pos = widget.mapTo(self, widget.pos())
            target = pos.y() - self.height() // 3
            target = max(0, min(target, self.verticalScrollBar().maximum()))
            current = self.verticalScrollBar().value()
            self.scroll_animation.setStartValue(current)
            self.scroll_animation.setEndValue(target)
            self.scroll_animation.start()
    
    
    class AnimatedButton(QPushButton):
        """Professional animated button with GPU-accelerated effects"""
        
        def __init__(self, text, color_start="#FF6B35", color_end="#F7931E", parent=None):
            super().__init__(text, parent)
            self.color_start = color_start
            self.color_end = color_end
            self._opacity = 1.0
            self._scale = 1.0
            self._ripple_radius = 0
            self._ripple_center = QPoint(0, 0)
            self._ripple_anim = None
            
            # Create animations
            self.opacity_anim = QVariantAnimation()
            self.opacity_anim.setDuration(200)
            self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
            self.opacity_anim.valueChanged.connect(self._update_opacity)
            
            self.scale_anim = QVariantAnimation()
            self.scale_anim.setDuration(150)
            self.scale_anim.setEasingCurve(QEasingCurve.OutElastic)
            self.scale_anim.valueChanged.connect(self._update_scale)
            
            self.setCursor(Qt.PointingHandCursor)
            self.setMinimumHeight(40)
            self._setup_style()
            
        def _setup_style(self):
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {self.color_start}, stop:1 {self.color_end});
                    border: none;
                    border-radius: 12px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px 20px;
                }}
                QPushButton:disabled {{
                    background: #444;
                    color: #888;
                }}
            """)
            
            # Add shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 4)
            self.setGraphicsEffect(shadow)
            
        def _update_opacity(self, value):
            self._opacity = value
            if self.graphicsEffect():
                shadow = self.graphicsEffect()
                shadow.setBlurRadius(20 + (1 - value) * 10)
                shadow.setOffset(0, 4 + (1 - value) * 4)
                
        def _update_scale(self, value):
            self._scale = value
            # Scale animation via geometry
            base_rect = self.geometry()
            new_width = int(base_rect.width() * (0.95 + value * 0.05))
            new_height = int(base_rect.height() * (0.95 + value * 0.05))
            new_x = base_rect.x() + (base_rect.width() - new_width) // 2
            new_y = base_rect.y() + (base_rect.height() - new_height) // 2
            self.setGeometry(new_x, new_y, new_width, new_height)
            
        def enterEvent(self, event):
            self.opacity_anim.setStartValue(1.0)
            self.opacity_anim.setEndValue(0.85)
            self.opacity_anim.start()
            
            self.scale_anim.setStartValue(0)
            self.scale_anim.setEndValue(1)
            self.scale_anim.start()
            super().enterEvent(event)
            
        def leaveEvent(self, event):
            self.opacity_anim.setStartValue(0.85)
            self.opacity_anim.setEndValue(1.0)
            self.opacity_anim.start()
            
            self.scale_anim.setStartValue(1)
            self.scale_anim.setEndValue(0)
            self.scale_anim.start()
            super().leaveEvent(event)
            
        def mousePressEvent(self, event):
            self._ripple_center = event.pos()
            self._ripple_radius = 0
            if self._ripple_anim:
                self._ripple_anim.stop()
            self._ripple_anim = QVariantAnimation()
            self._ripple_anim.setDuration(300)
            self._ripple_anim.setStartValue(0)
            self._ripple_anim.setEndValue(max(self.width(), self.height()))
            self._ripple_anim.valueChanged.connect(self._update_ripple)
            self._ripple_anim.start()
            super().mousePressEvent(event)
            
        def _update_ripple(self, value):
            self._ripple_radius = value
            self.update()
            
        def paintEvent(self, event):
            super().paintEvent(event)
            if self._ripple_radius > 0 and self._ripple_radius < max(self.width(), self.height()):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(QColor(255, 255, 255, 80))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(self._ripple_center, int(self._ripple_radius), int(self._ripple_radius))
    
    
    class AnimatedGradientWidget(QWidget):
        """Widget with smooth animated gradient background without setAngle"""
        
        def __init__(self, colors=None, parent=None):
            super().__init__(parent)
            self.colors = colors or ['#1a1a2e', '#16213e', '#0f3460', '#1a1a2e']
            self._offset = 0
            self._direction = 0
            
            # Animate gradient offset
            self.offset_anim = QVariantAnimation()
            self.offset_anim.setDuration(8000)
            self.offset_anim.setStartValue(0.0)
            self.offset_anim.setEndValue(1.0)
            self.offset_anim.setLoopCount(-1)
            self.offset_anim.valueChanged.connect(self._update_offset)
            self.offset_anim.start()
            
            # Animate gradient direction using QTimer (mousemove effect alternative)
            self.direction_timer = QTimer()
            self.direction_timer.timeout.connect(self._update_direction)
            self.direction_timer.start(50)
            
        def _update_offset(self, value):
            self._offset = value
            self.update()
            
        def _update_direction(self):
            # Simulate mouse-following gradient
            if hasattr(self, 'parent') and self.parent():
                cursor = QCursor.pos()
                local = self.mapFromGlobal(cursor)
                if self.rect().contains(local):
                    self._direction = local.x() / self.width() if self.width() > 0 else 0
                    self.update()
                    
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create gradient with start/end points instead of setAngle
            width = self.width()
            height = self.height()
            
            # Calculate gradient points based on direction
            x1 = int(width * self._direction)
            y1 = 0
            x2 = int(width * (1 - self._direction))
            y2 = height
            
            gradient = QLinearGradient(x1, y1, x2, y2)
            
            for i, color in enumerate(self.colors):
                pos = (i / (len(self.colors) - 1) + self._offset) % 1.0
                gradient.setColorAt(pos, QColor(color))
                
            painter.fillRect(self.rect(), QBrush(gradient))
            
    
    class ModernCard(QFrame):
        """Modern card with smooth hover animation and glass morphism effect"""
        
        def __init__(self, parent=None, color="#252535", glass=False):
            super().__init__(parent)
            self.color = color
            self.glass = glass
            self.setObjectName("ModernCard")
            self._hover_progress = 0
            
            # Hover animation
            self.hover_anim = QVariantAnimation()
            self.hover_anim.setDuration(250)
            self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)
            self.hover_anim.valueChanged.connect(self._update_hover)
            
            self._setup_style()
            
        def _setup_style(self):
            if self.glass:
                bg_color = f"rgba({int(self.color[1:3], 16)}, {int(self.color[3:5], 16)}, {int(self.color[5:7], 16)}, 0.7)"
                self.setStyleSheet(f"""
                    #ModernCard {{
                        background-color: {bg_color};
                        border-radius: 16px;
                        border: 1px solid rgba(255,255,255,0.15);
                    }}
                """)
            else:
                self.setStyleSheet(f"""
                    #ModernCard {{
                        background-color: {self.color};
                        border-radius: 16px;
                        border: 1px solid rgba(255,255,255,0.08);
                    }}
                """)
            self._update_shadow(0)
            
        def _update_shadow(self, value):
            shadow = QGraphicsDropShadowEffect()
            blur = 15 + value * 15
            offset = 3 + value * 5
            shadow.setBlurRadius(blur)
            shadow.setColor(QColor(0, 0, 0, 80 + int(value * 50)))
            shadow.setOffset(0, offset)
            self.setGraphicsEffect(shadow)
            
        def _update_hover(self, value):
            self._hover_progress = value
            self._update_shadow(value)
            
        def enterEvent(self, event):
            self.hover_anim.setStartValue(0)
            self.hover_anim.setEndValue(1)
            self.hover_anim.start()
            super().enterEvent(event)
            
        def leaveEvent(self, event):
            self.hover_anim.setStartValue(1)
            self.hover_anim.setEndValue(0)
            self.hover_anim.start()
            super().leaveEvent(event)
    
    
    class MediaPlayerWidget(QWidget):
        """Enhanced media player with full controls and waveform visualization"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.media_player = QMediaPlayer()
            self.current_file = None
            self.waveform_data = []
            self.waveform_visible = False
            
            self._setup_ui()
            self._connect_signals()
            
        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)
            
            # Waveform container
            self.waveform_container = QWidget()
            self.waveform_container.setFixedHeight(60)
            self.waveform_container.setVisible(False)
            self.waveform_container.setStyleSheet("""
                QWidget {
                    background-color: #1a1a2e;
                    border-radius: 8px;
                }
            """)
            layout.addWidget(self.waveform_container)
            
            # Time slider
            self.time_slider = QSlider(Qt.Horizontal)
            self.time_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #1a1a2e;
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
            layout.addWidget(self.time_slider)
            
            # Control buttons
            controls = QHBoxLayout()
            controls.setSpacing(10)
            
            self.play_btn = AnimatedButton("▶ Play", "#2ecc71", "#27ae60")
            self.play_btn.setFixedWidth(90)
            self.play_btn.clicked.connect(self.toggle_playback)
            self.play_btn.setEnabled(False)
            controls.addWidget(self.play_btn)
            
            self.stop_btn = AnimatedButton("⏹ Stop", "#e74c3c", "#c0392b")
            self.stop_btn.setFixedWidth(90)
            self.stop_btn.clicked.connect(self.stop_playback)
            self.stop_btn.setEnabled(False)
            controls.addWidget(self.stop_btn)
            
            self.time_label = QLabel("00:00:00 / 00:00:00")
            self.time_label.setStyleSheet("""
                QLabel {
                    color: #FF6B35;
                    font-family: monospace;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            controls.addWidget(self.time_label)
            controls.addStretch()
            
            # Volume control
            volume_label = QLabel("🔊")
            volume_label.setStyleSheet("color: #FF6B35;")
            controls.addWidget(volume_label)
            
            self.volume_slider = QSlider(Qt.Horizontal)
            self.volume_slider.setRange(0, 100)
            self.volume_slider.setValue(70)
            self.volume_slider.setFixedWidth(80)
            self.volume_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 3px;
                    background: #2d2d3d;
                    border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #FF6B35;
                    width: 10px;
                    height: 10px;
                    margin: -3px 0;
                    border-radius: 5px;
                }
            """)
            self.volume_slider.valueChanged.connect(self.set_volume)
            controls.addWidget(self.volume_slider)
            
            layout.addLayout(controls)
            
        def _connect_signals(self):
            self.media_player.positionChanged.connect(self.update_position)
            self.media_player.durationChanged.connect(self.update_duration)
            self.media_player.stateChanged.connect(self.update_playback_state)
            self.media_player.error.connect(self.handle_error)
            
        def set_volume(self, value):
            self.media_player.setVolume(value)
            
        def load_media(self, file_path: str):
            """Load media file and generate waveform"""
            self.current_file = file_path
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            
            # Generate waveform visualization
            self._generate_waveform(file_path)
            
        def _generate_waveform(self, file_path: str):
            """Generate waveform data for visualization"""
            try:
                import numpy as np
                import soundfile as sf
                
                data, sr = sf.read(file_path)
                if len(data.shape) > 1:
                    data = data.mean(axis=1)
                    
                # Downsample for waveform
                target_points = 1000
                step = max(1, len(data) // target_points)
                waveform = data[::step]
                
                # Normalize
                if len(waveform) > 0:
                    max_val = np.max(np.abs(waveform))
                    if max_val > 0:
                        waveform = waveform / max_val
                        
                self.waveform_data = waveform.tolist()
                self.waveform_visible = True
                self.waveform_container.setVisible(True)
                self.waveform_container.update()
                
                # Custom paint for waveform
                class WaveformWidget(QWidget):
                    def __init__(self, parent, data):
                        super().__init__(parent)
                        self.data = data
                        
                    def paintEvent(self, event):
                        painter = QPainter(self)
                        painter.setRenderHint(QPainter.Antialiasing)
                        
                        if not self.data:
                            return
                            
                        width = self.width()
                        height = self.height()
                        center_y = height // 2
                        
                        bar_width = max(1, width / len(self.data))
                        pen = QPen(QColor(255, 107, 53))
                        pen.setWidth(max(1, int(bar_width)))
                        painter.setPen(pen)
                        
                        for i, val in enumerate(self.data):
                            x = i * bar_width
                            bar_height = int(abs(val) * height)
                            y1 = center_y - bar_height // 2
                            y2 = center_y + bar_height // 2
                            painter.drawLine(int(x), y1, int(x), y2)
                            
                # Replace container with waveform widget
                old_widget = self.waveform_container.layout() if self.waveform_container.layout() else None
                if old_widget:
                    old_widget.deleteLater()
                    
                waveform_widget = WaveformWidget(self.waveform_container, self.waveform_data)
                layout = QVBoxLayout(self.waveform_container)
                layout.addWidget(waveform_widget)
                layout.setContentsMargins(0, 0, 0, 0)
                
            except Exception as e:
                print(f"Waveform generation failed: {e}")
                
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
            
        def update_duration(self, duration):
            self.time_slider.setRange(0, duration)
            
        def update_playback_state(self, state):
            if state == QMediaPlayer.StoppedState:
                self.play_btn.setText("▶ Play")
                
        def handle_error(self, error):
            if error != QMediaPlayer.NoError:
                print(f"Media player error: {error}")
                
        def is_playing(self) -> bool:
            return self.media_player.state() == QMediaPlayer.PlayingState
            
        def get_position(self) -> float:
            return self.media_player.position() / 1000.0
            
        def get_current_time(self) -> float:
            return self.media_player.position() / 1000.0
            
        def stop(self):
            self.media_player.stop()
            
        def unload(self):
            """Unload current media"""
            self.stop_playback()
            self.media_player.setMedia(QMediaContent())
            self.current_file = None
            self.play_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self.time_label.setText("00:00:00 / 00:00:00")
            self.time_slider.setValue(0)
            self.waveform_container.setVisible(False)
            self.waveform_data = []
            self.waveform_visible = False
            
        def get_current_file(self):
            return self.current_file
    
    
    class TranscriptionWorker(QThread):
        """Enhanced worker thread for transcription with progress tracking"""
        
        progress = pyqtSignal(int, str)
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)
        
        def __init__(self, input_file, settings):
            super().__init__()
            self.input_file = input_file
            self.settings = settings
            self._is_running = True
            self.logger = Logger()
            
        def stop(self):
            self._is_running = False
            
        def run(self):
            try:
                import whisper
                
                self.progress.emit(5, "🎯 Initializing Whisper engine...")
                model_name = self.settings.get('model', 'base')
                
                self.progress.emit(10, f"📥 Loading {model_name.upper()} model...")
                self.logger.info(f"Loading model: {model_name}")
                
                model = whisper.load_model(model_name, download_root=str(MODELS_DIR))
                
                self.progress.emit(25, "🎵 Preparing audio stream...")
                options = {
                    'language': self.settings.get('language', 'en'),
                    'task': 'translate' if self.settings.get('translate', False) else 'transcribe',
                    'verbose': False,
                    'fp16': False,
                    'word_timestamps': True,
                    'initial_prompt': "The following is a transcription of spoken audio in natural language."
                }
                
                self.progress.emit(40, "🎤 AI is transcribing (this may take several minutes)...")
                result = model.transcribe(self.input_file, **options)
                
                self.progress.emit(75, "📝 Processing and optimizing segments...")
                segments = []
                for seg in result['segments']:
                    if not self._is_running:
                        return
                    segments.append({
                        'start': seg['start'],
                        'end': seg['end'],
                        'text': seg['text'].strip(),
                        'confidence': seg.get('confidence', 0)
                    })
                
                self.progress.emit(85, "🎨 Generating formatted subtitles...")
                subtitles = self._generate_subtitles(segments)
                
                self.progress.emit(100, "✅ Transcription complete!")
                self.finished.emit({'subtitles': subtitles, 'segments': segments})
                self.logger.info(f"Transcription complete: {len(segments)} segments")
                
            except Exception as e:
                self.logger.error(f"Transcription failed: {e}")
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
        """Main application window with complete functionality"""
        
        def __init__(self):
            super().__init__()
            
            # Initialize components
            self.config = ConfigManager()
            self.cache = CacheManager()
            self.logger = Logger()
            
            # State variables
            self.current_file = None
            self.current_subtitles = []
            self.current_segments = []
            self.worker = None
            self.media_loaded = False
            self.dark_mode = True
            
            # Setup window
            self.setWindowTitle("NotY Caption Generator AI v7.1")
            
            # Get saved window size or use defaults
            window_width = self.config.get('ui.window_width', 1300)
            window_height = self.config.get('ui.window_height', 850)
            self.setMinimumSize(1100, 750)
            self.resize(window_width, window_height)
            
            # Center window on screen
            screen = QApplication.primaryScreen().geometry()
            self.move(screen.center() - self.rect().center())
            
            # Apply modern style
            self._apply_modern_style()
            
            # Setup UI
            self._setup_ui()
            self._setup_animations()
            self._load_settings()
            
            # Setup tray icon
            self._setup_tray()
            
            self.logger.info("Application started")
            
        def _apply_modern_style(self):
            """Apply modern Fusion style with custom colors"""
            QApplication.setStyle(QStyleFactory.create('Fusion'))
            
            # Create custom dark palette
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(26, 26, 46))
            palette.setColor(QPalette.WindowText, QColor(221, 221, 221))
            palette.setColor(QPalette.Base, QColor(30, 30, 46))
            palette.setColor(QPalette.AlternateBase, QColor(35, 35, 51))
            palette.setColor(QPalette.ToolTipBase, QColor(255, 107, 53))
            palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(221, 221, 221))
            palette.setColor(QPalette.Button, QColor(45, 45, 61))
            palette.setColor(QPalette.ButtonText, QColor(221, 221, 221))
            palette.setColor(QPalette.BrightText, QColor(255, 107, 53))
            palette.setColor(QPalette.Highlight, QColor(255, 107, 53))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
            
            QApplication.setPalette(palette)
            
            # Global stylesheet
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1a2e;
                }
                QScrollBar:vertical {
                    background: #2d2d3d;
                    width: 10px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical {
                    background: #FF6B35;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #F7931E;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0px;
                }
                QToolTip {
                    background-color: #1a1a2e;
                    color: #FF6B35;
                    border: 1px solid #FF6B35;
                    border-radius: 8px;
                    padding: 5px;
                }
                QMenuBar {
                    background-color: #1a1a2e;
                    color: #ddd;
                    border-bottom: 1px solid #2d2d3d;
                }
                QMenuBar::item:selected {
                    background-color: #FF6B35;
                    color: white;
                }
                QMenu {
                    background-color: #2d2d3d;
                    color: #ddd;
                    border: 1px solid #3d3d4d;
                }
                QMenu::item:selected {
                    background-color: #FF6B35;
                    color: white;
                }
            """)
            
        def _setup_tray(self):
            """Setup system tray icon"""
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(QIcon())
            self.tray_icon.setToolTip("NotY Caption Generator AI")
            
            tray_menu = QMenu()
            show_action = QAction("Show", self)
            show_action.triggered.connect(self.show_normal)
            tray_menu.addAction(show_action)
            
            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
        def show_normal(self):
            """Show window normally"""
            self.showNormal()
            self.raise_()
            self.activateWindow()
            
        def _setup_ui(self):
            """Setup complete UI"""
            central = AnimatedGradientWidget(['#1a1a2e', '#16213e', '#0f3460', '#1a1a2e'])
            self.setCentralWidget(central)
            
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_layout.setSpacing(15)
            
            # Menu bar
            self._create_menu_bar()
            
            # Header
            header = self._create_header()
            main_layout.addWidget(header)
            
            # Main splitter (Resizable panels)
            splitter = QSplitter(Qt.Horizontal)
            splitter.setHandleWidth(4)
            splitter.setStyleSheet("""
                QSplitter::handle {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF6B35, stop:1 #F7931E);
                    border-radius: 2px;
                }
            """)
            
            # Left panel - Controls (Scrollable)
            left_panel = self._create_control_panel()
            splitter.addWidget(left_panel)
            
            # Right panel - Caption Editor
            right_panel = self._create_caption_panel()
            splitter.addWidget(right_panel)
            
            # Restore splitter sizes
            splitter_sizes = self.config.get('ui.splitter_sizes', [450, 850])
            splitter.setSizes(splitter_sizes)
            
            main_layout.addWidget(splitter, 1)
            
            # Progress section
            progress_section = self._create_progress_section()
            main_layout.addWidget(progress_section)
            
            # Status bar
            self.statusBar().setStyleSheet("""
                QStatusBar {
                    background-color: #1a1a2e;
                    color: #FF6B35;
                    border-top: 1px solid #2d2d3d;
                    padding: 3px;
                }
            """)
            self.statusBar().showMessage("🎯 Ready - Import media to begin")
            
        def _create_menu_bar(self):
            """Create application menu bar"""
            menubar = self.menuBar()
            
            # File menu
            file_menu = menubar.addMenu("File")
            
            import_action = QAction("Import Media...", self)
            import_action.triggered.connect(self.import_media)
            import_action.setShortcut("Ctrl+O")
            file_menu.addAction(import_action)
            
            youtube_action = QAction("Download from YouTube...", self)
            youtube_action.triggered.connect(self.import_youtube)
            youtube_action.setShortcut("Ctrl+Y")
            file_menu.addAction(youtube_action)
            
            file_menu.addSeparator()
            
            export_srt_action = QAction("Export SRT...", self)
            export_srt_action.triggered.connect(lambda: self.export_subtitles('srt'))
            export_srt_action.setShortcut("Ctrl+E")
            file_menu.addAction(export_srt_action)
            
            export_ass_action = QAction("Export ASS...", self)
            export_ass_action.triggered.connect(lambda: self.export_subtitles('ass'))
            file_menu.addAction(export_ass_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            exit_action.setShortcut("Ctrl+Q")
            file_menu.addAction(exit_action)
            
            # Edit menu
            edit_menu = menubar.addMenu("Edit")
            
            clear_action = QAction("Clear Captions", self)
            clear_action.triggered.connect(self.clear_captions)
            edit_menu.addAction(clear_action)
            
            copy_action = QAction("Copy Captions", self)
            copy_action.triggered.connect(self.copy_captions)
            copy_action.setShortcut("Ctrl+C")
            edit_menu.addAction(copy_action)
            
            # View menu
            view_menu = menubar.addMenu("View")
            
            toggle_waveform_action = QAction("Show Waveform", self)
            toggle_waveform_action.setCheckable(True)
            toggle_waveform_action.triggered.connect(self.toggle_waveform)
            view_menu.addAction(toggle_waveform_action)
            
            # Tools menu
            tools_menu = menubar.addMenu("Tools")
            
            settings_action = QAction("Settings...", self)
            settings_action.triggered.connect(self.show_settings)
            tools_menu.addAction(settings_action)
            
            clear_cache_action = QAction("Clear Cache", self)
            clear_cache_action.triggered.connect(self.clear_cache)
            tools_menu.addAction(clear_cache_action)
            
            # Help menu
            help_menu = menubar.addMenu("Help")
            
            about_action = QAction("About", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
            
        def _create_header(self):
            """Create animated header"""
            header = QWidget()
            header.setFixedHeight(90)
            header.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:0.3 #F7931E, 
                        stop:0.7 #FF3366, stop:1 #FF6B35);
                    border-radius: 15px;
                }
            """)
            
            layout = QHBoxLayout(header)
            layout.setContentsMargins(25, 0, 25, 0)
            
            # Logo and title
            title_container = QWidget()
            title_layout = QVBoxLayout(title_container)
            title_layout.setSpacing(5)
            
            title = QLabel("🎬 NotY Caption Generator AI")
            title.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    letter-spacing: 1px;
                }
            """)
            title_layout.addWidget(title)
            
            subtitle = QLabel("Professional AI-Powered Subtitle Generation | Powered by OpenAI Whisper")
            subtitle.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 11px;")
            title_layout.addWidget(subtitle)
            
            layout.addWidget(title_container)
            layout.addStretch()
            
            # Stats badge
            self.stats_badge = QLabel("✨ READY")
            self.stats_badge.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    background: rgba(0,0,0,0.3);
                    padding: 8px 18px;
                    border-radius: 25px;
                }
            """)
            layout.addWidget(self.stats_badge)
            
            return header
            
        def _create_control_panel(self):
            """Create scrollable control panel"""
            scroll = SmoothScrollArea()
            scroll.setStyleSheet("""
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
            """)
            
            content = QWidget()
            content.setStyleSheet("background-color: transparent;")
            layout = QVBoxLayout(content)
            layout.setSpacing(15)
            
            # Media info card
            self.media_card = ModernCard(color="#252535")
            media_layout = QVBoxLayout(self.media_card)
            media_layout.setContentsMargins(20, 20, 20, 20)
            media_layout.setSpacing(12)
            
            self.media_icon = QLabel("🎬")
            self.media_icon.setStyleSheet("font-size: 56px;")
            self.media_icon.setAlignment(Qt.AlignCenter)
            media_layout.addWidget(self.media_icon)
            
            self.media_label = QLabel("No Media Loaded")
            self.media_label.setStyleSheet("color: #aaa; font-size: 12px; font-weight: bold;")
            self.media_label.setAlignment(Qt.AlignCenter)
            self.media_label.setWordWrap(True)
            media_layout.addWidget(self.media_label)
            
            # Cancel/Unload button
            self.cancel_btn = AnimatedButton("✖ Cancel / Unload", "#e74c3c", "#c0392b")
            self.cancel_btn.clicked.connect(self.unload_media)
            self.cancel_btn.setVisible(False)
            media_layout.addWidget(self.cancel_btn)
            
            layout.addWidget(self.media_card)
            
            # Import buttons container
            import_container = QWidget()
            import_layout = QVBoxLayout(import_container)
            import_layout.setSpacing(10)
            
            self.import_btn = AnimatedButton("📁 Import Media File", "#3498db", "#2980b9")
            self.import_btn.clicked.connect(self.import_media)
            import_layout.addWidget(self.import_btn)
            
            self.youtube_btn = AnimatedButton("▶️ Download from YouTube", "#e74c3c", "#c0392b")
            self.youtube_btn.clicked.connect(self.import_youtube)
            import_layout.addWidget(self.youtube_btn)
            
            layout.addWidget(import_container)
            
            # Settings sections
            sections = [
                ("🎤 Whisper Model", self._create_model_section()),
                ("🌐 Language & Translation", self._create_language_section()),
                ("🎵 Vocal Separation", self._create_vocal_section()),
                ("📝 Subtitle Formatting", self._create_break_section()),
            ]
            
            for title, widget in sections:
                section = ModernCard(color="#252535")
                section_layout = QVBoxLayout(section)
                section_layout.setContentsMargins(18, 14, 18, 14)
                section_layout.setSpacing(8)
                
                title_label = QLabel(title)
                title_label.setStyleSheet("color: #FF6B35; font-weight: bold; font-size: 12px; letter-spacing: 0.5px;")
                section_layout.addWidget(title_label)
                section_layout.addWidget(widget)
                
                layout.addWidget(section)
            
            # Generate button
            self.generate_btn = AnimatedButton("✨ GENERATE CAPTIONS", "#FF6B35", "#F7931E")
            self.generate_btn.setMinimumHeight(55)
            self.generate_btn.clicked.connect(self.generate_captions)
            self.generate_btn.setEnabled(False)
            layout.addWidget(self.generate_btn)
            
            # Export buttons
            export_container = QWidget()
            export_layout = QHBoxLayout(export_container)
            export_layout.setSpacing(10)
            export_layout.setContentsMargins(0, 0, 0, 0)
            
            self.export_srt_btn = AnimatedButton("📄 Export SRT", "#4ECDC4", "#45B7D1")
            self.export_srt_btn.clicked.connect(lambda: self.export_subtitles('srt'))
            self.export_srt_btn.setEnabled(False)
            export_layout.addWidget(self.export_srt_btn)
            
            self.export_ass_btn = AnimatedButton("🎨 Export ASS", "#9B59B6", "#8E44AD")
            self.export_ass_btn.clicked.connect(lambda: self.export_subtitles('ass'))
            self.export_ass_btn.setEnabled(False)
            export_layout.addWidget(self.export_ass_btn)
            
            layout.addWidget(export_container)
            
            layout.addStretch()
            scroll.setWidget(content)
            return scroll
            
        def _create_model_section(self):
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.model_combo = QComboBox()
            models = [
                ("⚡ TINY", "Fastest, lowest quality"),
                ("🎯 BASE", "Balanced speed/quality"),
                ("📈 SMALL", "Better accuracy"),
                ("🚀 MEDIUM", "High quality"),
                ("💎 LARGE", "Best quality, slower")
            ]
            for name, desc in models:
                self.model_combo.addItem(f"{name} - {desc}")
            self.model_combo.setCurrentIndex(1)
            self.model_combo.setStyleSheet("""
                QComboBox {
                    background: #1a1a2e;
                    border: 1px solid #3d3d4d;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-size: 12px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 6px solid transparent;
                    border-right: 6px solid transparent;
                    border-top: 6px solid #FF6B35;
                    margin-right: 10px;
                }
                QComboBox QAbstractItemView {
                    background: #1a1a2e;
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
            layout.setSpacing(10)
            
            self.lang_combo = QComboBox()
            languages = [
                ("🇺🇸 English - High Accuracy", "en"),
                ("🇪🇸 Spanish - High Accuracy", "es"),
                ("🇮🇹 Italian - High Accuracy", "it"),
                ("🇵🇹 Portuguese - High Accuracy", "pt"),
                ("🇩🇪 German - High Accuracy", "de"),
                ("🇯🇵 Japanese - High Accuracy", "ja"),
                ("🇫🇷 French - High Accuracy", "fr"),
                ("🇷🇺 Russian - Medium Accuracy", "ru"),
                ("🇮🇳 Hindi - Medium Accuracy", "hi"),
                ("🇮🇳 Tamil - Medium Accuracy", "ta"),
                ("🇮🇳 Bengali - Medium Accuracy", "bn"),
            ]
            for name, code in languages:
                self.lang_combo.addItem(name, code)
            self.lang_combo.setStyleSheet("""
                QComboBox {
                    background: #1a1a2e;
                    border: 1px solid #3d3d4d;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-size: 12px;
                }
                QComboBox::drop-down {
                    border: none;
                }
            """)
            layout.addWidget(self.lang_combo)
            
            # Translate checkbox - only shown for non-English languages
            self.translate_check = QCheckBox("🔄 Translate to English (Auto-translate)")
            self.translate_check.setStyleSheet("""
                QCheckBox {
                    color: #ccc;
                    spacing: 10px;
                    font-size: 11px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 5px;
                    border: 2px solid #FF6B35;
                    background: #1a1a2e;
                }
                QCheckBox::indicator:checked {
                    background-color: #FF6B35;
                }
                QCheckBox::indicator:hover {
                    border-color: #F7931E;
                }
            """)
            layout.addWidget(self.translate_check)
            
            # Connect language change to update translate visibility
            self.lang_combo.currentIndexChanged.connect(self._update_translate_visibility)
            self._update_translate_visibility()
            
            return widget
            
        def _update_translate_visibility(self):
            """Hide translate checkbox for English language"""
            current_lang = self.lang_combo.currentData()
            if current_lang == 'en':
                self.translate_check.setVisible(False)
                self.translate_check.setChecked(False)
            else:
                self.translate_check.setVisible(True)
                
        def _create_vocal_section(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.vocal_combo = QComboBox()
            vocal_options = [
                ("None - Use original audio", "none"),
                ("2stems - Vocals + Accompaniment", "2stems"),
                ("4stems - Vocals + Drums + Bass + Other", "4stems"),
                ("5stems - Full separation", "5stems")
            ]
            for name, value in vocal_options:
                self.vocal_combo.addItem(name, value)
            self.vocal_combo.setStyleSheet("""
                QComboBox {
                    background: #1a1a2e;
                    border: 1px solid #3d3d4d;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-size: 12px;
                }
            """)
            layout.addWidget(self.vocal_combo)
            
            return widget
            
        def _create_break_section(self):
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)
            
            self.break_combo = QComboBox()
            self.break_combo.addItems(['🎯 Auto (Smart sentences)', '📝 Words (Count based)', '📏 Letters (Character based)'])
            self.break_combo.setStyleSheet("""
                QComboBox {
                    background: #1a1a2e;
                    border: 1px solid #3d3d4d;
                    border-radius: 10px;
                    padding: 10px;
                    color: white;
                    font-size: 12px;
                }
            """)
            layout.addWidget(self.break_combo)
            
            # Limits container
            limits_container = QWidget()
            limits_layout = QHBoxLayout(limits_container)
            limits_layout.setContentsMargins(0, 0, 0, 0)
            limits_layout.setSpacing(15)
            
            # Word limit
            word_container = QWidget()
            word_layout = QHBoxLayout(word_container)
            word_layout.setContentsMargins(0, 0, 0, 0)
            word_layout.setSpacing(5)
            word_layout.addWidget(QLabel("Words:"))
            self.word_limit = QSpinBox()
            self.word_limit.setRange(1, 30)
            self.word_limit.setValue(10)
            self.word_limit.setEnabled(False)
            self.word_limit.setStyleSheet("""
                QSpinBox {
                    background: #1a1a2e;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 6px;
                    color: white;
                    min-width: 65px;
                }
            """)
            word_layout.addWidget(self.word_limit)
            limits_layout.addWidget(word_container)
            
            # Char limit
            char_container = QWidget()
            char_layout = QHBoxLayout(char_container)
            char_layout.setContentsMargins(0, 0, 0, 0)
            char_layout.setSpacing(5)
            char_layout.addWidget(QLabel("Chars:"))
            self.char_limit = QSpinBox()
            self.char_limit.setRange(10, 80)
            self.char_limit.setValue(40)
            self.char_limit.setEnabled(False)
            self.char_limit.setStyleSheet("""
                QSpinBox {
                    background: #1a1a2e;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    padding: 6px;
                    color: white;
                    min-width: 65px;
                }
            """)
            char_layout.addWidget(self.char_limit)
            limits_layout.addWidget(char_container)
            
            limits_layout.addStretch()
            layout.addWidget(limits_container)
            
            self.break_combo.currentIndexChanged.connect(self._on_break_changed)
            
            return widget
            
        def _create_caption_panel(self):
            """Create caption editor panel with media player"""
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setSpacing(15)
            
            # Media player card
            player_card = ModernCard(color="#252535")
            player_layout = QVBoxLayout(player_card)
            player_layout.setContentsMargins(15, 15, 15, 15)
            player_layout.setSpacing(10)
            
            self.media_player = MediaPlayerWidget()
            player_layout.addWidget(self.media_player)
            layout.addWidget(player_card)
            
            # Caption editor card
            editor_card = ModernCard(color="#252535")
            editor_layout = QVBoxLayout(editor_card)
            editor_layout.setContentsMargins(15, 15, 15, 15)
            editor_layout.setSpacing(10)
            
            # Editor header
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
                    font-size: 11px;
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
                    font-size: 11px;
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
                    line-height: 1.6;
                }
                QTextEdit:focus {
                    border: 2px solid #FF6B35;
                }
            """)
            self.caption_editor.setPlaceholderText(
                "✨ Generated captions will appear here...\n\n"
                "• Click 'Edit Mode' to modify captions\n"
                "• Edit timestamps and text as needed\n"
                "• Click 'Save Changes' to keep your edits\n"
                "• Export as SRT or ASS when done"
            )
            editor_layout.addWidget(self.caption_editor)
            
            layout.addWidget(editor_card)
            
            return panel
            
        def _create_progress_section(self):
            """Create progress section"""
            card = ModernCard(color="#252535")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(15, 10, 15, 10)
            layout.setSpacing(8)
            
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 8px;
                    background: #1a1a2e;
                    height: 8px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF6B35, stop:0.5 #F7931E, stop:1 #FF3366);
                    border-radius: 8px;
                }
            """)
            layout.addWidget(self.progress_bar)
            
            self.progress_label = QLabel("")
            self.progress_label.setStyleSheet("color: #FF6B35; font-size: 11px; font-weight: bold;")
            self.progress_label.setVisible(False)
            layout.addWidget(self.progress_label)
            
            return card
            
        def _setup_animations(self):
            """Setup window animations"""
            self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
            self.fade_animation.setDuration(500)
            self.fade_animation.setStartValue(0)
            self.fade_animation.setEndValue(1)
            self.fade_animation.start()
            
        def _load_settings(self):
            """Load saved settings"""
            # Model setting
            model_index = self.config.get('transcription.default_model', 'base')
            model_map = {'tiny': 0, 'base': 1, 'small': 2, 'medium': 3, 'large': 4}
            self.model_combo.setCurrentIndex(model_map.get(model_index, 1))
            
            # Language setting
            language = self.config.get('transcription.default_language', 'en')
            for i in range(self.lang_combo.count()):
                if self.lang_combo.itemData(i) == language:
                    self.lang_combo.setCurrentIndex(i)
                    break
                    
            # Translate setting
            translate = self.config.get('transcription.auto_translate', False)
            self.translate_check.setChecked(translate)
            
            # Vocal separation
            vocal = self.config.get('transcription.vocal_separation', 'none')
            vocal_map = {'none': 0, '2stems': 1, '4stems': 2, '5stems': 3}
            self.vocal_combo.setCurrentIndex(vocal_map.get(vocal, 0))
            
            # Break type
            break_type = self.config.get('transcription.break_type', 'auto')
            break_map = {'auto': 0, 'words': 1, 'letters': 2}
            self.break_combo.setCurrentIndex(break_map.get(break_type, 0))
            
            # Word/char limits
            self.word_limit.setValue(self.config.get('transcription.word_limit', 10))
            self.char_limit.setValue(self.config.get('transcription.char_limit', 40))
            
        def _save_settings(self):
            """Save current settings"""
            model_map = {0: 'tiny', 1: 'base', 2: 'small', 3: 'medium', 4: 'large'}
            self.config.set('transcription.default_model', model_map.get(self.model_combo.currentIndex(), 'base'))
            self.config.set('transcription.default_language', self.lang_combo.currentData())
            self.config.set('transcription.auto_translate', self.translate_check.isChecked())
            
            vocal_map = {0: 'none', 1: '2stems', 2: '4stems', 3: '5stems'}
            self.config.set('transcription.vocal_separation', vocal_map.get(self.vocal_combo.currentIndex(), 'none'))
            
            break_map = {0: 'auto', 1: 'words', 2: 'letters'}
            self.config.set('transcription.break_type', break_map.get(self.break_combo.currentIndex(), 'auto'))
            self.config.set('transcription.word_limit', self.word_limit.value())
            self.config.set('transcription.char_limit', self.char_limit.value())
            
            # Save window geometry
            self.config.set('ui.window_width', self.width())
            self.config.set('ui.window_height', self.height())
            
            splitter = self.findChild(QSplitter)
            if splitter:
                self.config.set('ui.splitter_sizes', splitter.sizes())
                
        def _on_break_changed(self, index):
            """Handle break type change"""
            self.word_limit.setEnabled(index == 1)
            self.char_limit.setEnabled(index == 2)
            
        def import_media(self):
            """Import media file dialog"""
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Media", "",
                "Media Files (*.mp4 *.avi *.mkv *.mov *.mp3 *.wav *.flac *.m4a *.mpg *.mpeg *.webm)"
            )
            if file_path:
                self.load_media(file_path)
                
        def import_youtube(self):
            """Download YouTube video"""
            url, ok = QInputDialog.getText(self, "YouTube URL", 
                "Enter YouTube URL:\n\nExamples:\n• https://youtu.be/...\n• https://www.youtube.com/watch?v=...")
            if ok and url:
                self.stats_badge.setText("📥 DOWNLOADING")
                self.statusBar().showMessage("Downloading from YouTube...")
                
                try:
                    import yt_dlp
                    
                    temp_dir = Path(tempfile.gettempdir()) / 'NotYCaptionGenAI'
                    temp_dir.mkdir(exist_ok=True)
                    
                    # Find available filename
                    base_name = "youtube_audio"
                    counter = 1
                    while (temp_dir / f"{base_name}_{counter}.mp3").exists():
                        counter += 1
                    output_path = temp_dir / f"{base_name}_{counter}.mp3"
                    
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': str(output_path.with_suffix('')),
                        'quiet': True,
                        'no_warnings': True,
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.extract_info(url, download=True)
                        
                    if output_path.exists():
                        self.load_media(str(output_path))
                        self.stats_badge.setText("✅ DOWNLOADED")
                        self.statusBar().showMessage("Download complete!")
                    else:
                        raise Exception("Output file not found")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Download Error", f"Failed to download:\n\n{str(e)}")
                    self.stats_badge.setText("❌ FAILED")
                    self.statusBar().showMessage("Download failed")
                    
        def load_media(self, file_path: str):
            """Load media file into the application"""
            self.current_file = file_path
            self.media_loaded = True
            
            # Update UI
            self.media_label.setText(f"📹 {Path(file_path).name}")
            self.generate_btn.setEnabled(True)
            self.media_player.load_media(file_path)
            self.cancel_btn.setVisible(True)
            
            self.stats_badge.setText("🎬 MEDIA LOADED")
            self.statusBar().showMessage(f"Loaded: {Path(file_path).name}")
            
            # Show success message
            QMessageBox.information(self, "Media Loaded", 
                f"✅ Successfully loaded:\n\n{Path(file_path).name}\n\n"
                f"Click 'Generate Captions' to start transcription.")
                
        def unload_media(self):
            """Unload current media and reset UI"""
            reply = QMessageBox.question(self, "Unload Media", 
                "Are you sure you want to unload the current media?\n\nAny unsaved captions will be lost.",
                QMessageBox.Yes | QMessageBox.No)
                
            if reply == QMessageBox.Yes:
                self.current_file = None
                self.media_loaded = False
                self.current_subtitles = []
                self.current_segments = []
                self.caption_editor.clear()
                
                # Reset UI
                self.media_label.setText("No Media Loaded")
                self.generate_btn.setEnabled(False)
                self.export_srt_btn.setEnabled(False)
                self.export_ass_btn.setEnabled(False)
                self.media_player.unload()
                self.cancel_btn.setVisible(False)
                
                self.stats_badge.setText("✨ READY")
                self.statusBar().showMessage("Media unloaded - Ready for new import")
                
        def generate_captions(self):
            """Start caption generation"""
            if not self.current_file:
                return
                
            # Get model name from combo box
            model_text = self.model_combo.currentText()
            if 'TINY' in model_text:
                model = 'tiny'
            elif 'BASE' in model_text:
                model = 'base'
            elif 'SMALL' in model_text:
                model = 'small'
            elif 'MEDIUM' in model_text:
                model = 'medium'
            else:
                model = 'large'
                
            # Get settings
            settings = {
                'model': model,
                'language': self.lang_combo.currentData(),
                'translate': self.translate_check.isChecked() and self.lang_combo.currentData() != 'en',
                'vocal_separation': self.vocal_combo.currentData(),
                'break_type': ['auto', 'words', 'letters'][self.break_combo.currentIndex()],
                'word_limit': self.word_limit.value(),
                'char_limit': self.char_limit.value()
            }
            
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_label.setVisible(True)
            self.progress_bar.setValue(0)
            self.generate_btn.setEnabled(False)
            self.stats_badge.setText("🔄 PROCESSING")
            
            # Start worker thread
            self.worker = TranscriptionWorker(self.current_file, settings)
            self.worker.progress.connect(self.update_progress)
            self.worker.finished.connect(self.on_transcription_finished)
            self.worker.error.connect(self.on_transcription_error)
            self.worker.start()
            
        def update_progress(self, value, message):
            """Update progress display"""
            self.progress_bar.setValue(value)
            self.progress_label.setText(message)
            self.statusBar().showMessage(message)
            
            # Hide progress
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            self.generate_btn.setEnabled(True)
            self.export_srt_btn.setEnabled(True)
            self.export_ass_btn.setEnabled(True)
            
            self.stats_badge.setText(f"✅ {len(self.current_subtitles)} CAPTIONS")
            self.statusBar().showMessage(f"Successfully generated {len(self.current_subtitles)} captions!")
            
            # Save settings
            self._save_settings()
            
            # Calculate total duration
            total_duration = 0
            if self.current_segments:
                total_duration = self.current_segments[-1]['end']
            
            QMessageBox.information(self, "Generation Complete", 
                f"✨ Successfully generated {len(self.current_subtitles)} captions!\n\n"
                f"📊 Statistics:\n"
                f"  • Segments: {len(self.current_segments)}\n"
                f"  • Duration: {int(total_duration // 60)}m {int(total_duration % 60)}s\n"
                f"  • Style: {self.break_combo.currentText()}\n\n"
                f"You can now edit captions and export them.")
                
        def on_transcription_error(self, error):
            """Handle transcription error"""
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
            self.generate_btn.setEnabled(True)
            
            self.stats_badge.setText("❌ ERROR")
            self.statusBar().showMessage("Transcription failed")
            
            QMessageBox.critical(self, "Transcription Error", 
                f"❌ Failed to generate captions:\n\n{error}\n\n"
                f"Please check:\n"
                f"• Media file is valid and accessible\n"
                f"• Whisper model is downloaded\n"
                f"• Internet connection (for first run)\n"
                f"• Sufficient disk space (models need 1-5GB)\n"
                f"• FFmpeg is installed and accessible")
                
        def export_subtitles(self, format_type: str):
            """Export subtitles to file"""
            if not self.current_subtitles:
                QMessageBox.warning(self, "No Captions", 
                    "No captions to export. Please generate captions first.")
                return
                
            default_name = f"subtitles_{Path(self.current_file).stem}.{format_type}"
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"Export {format_type.upper()} File",
                default_name,
                f"{format_type.upper()} Files (*.{format_type})"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(self.current_subtitles))
                        
                    self.statusBar().showMessage(f"Exported to {Path(file_path).name}")
                    self.stats_badge.setText("📤 EXPORTED")
                    
                    # Show success with file info
                    file_size = Path(file_path).stat().st_size
                    size_kb = file_size / 1024
                    
                    QMessageBox.information(self, "Export Complete", 
                        f"✅ Successfully exported to:\n\n{file_path}\n\n"
                        f"📄 Format: {format_type.upper()}\n"
                        f"📊 Segments: {len(self.current_subtitles)}\n"
                        f"💾 File size: {size_kb:.1f} KB")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", 
                        f"Failed to export file:\n\n{str(e)}")
                    
        def toggle_edit_mode(self):
            """Toggle caption edit mode"""
            self.caption_editor.setReadOnly(not self.edit_mode_btn.isChecked())
            self.save_edit_btn.setEnabled(self.edit_mode_btn.isChecked())
            
            if self.edit_mode_btn.isChecked():
                self.statusBar().showMessage("✏️ Edit mode enabled - You can now edit timestamps and text")
                self.stats_badge.setText("✏️ EDIT MODE")
                # Change cursor to editing cursor
                self.caption_editor.setCursor(QCursor(Qt.IBeamCursor))
                # Highlight the editable area
                self.caption_editor.setStyleSheet("""
                    QTextEdit {
                        background: #1a1a2e;
                        border: 2px solid #FF6B35;
                        border-radius: 12px;
                        padding: 15px;
                        color: #e0e0e0;
                        font-family: 'Consolas', 'Monaco', monospace;
                        line-height: 1.6;
                    }
                """)
            else:
                self.statusBar().showMessage("📖 View mode - Click 'Edit Mode' to make changes")
                self.stats_badge.setText("📖 VIEW MODE")
                self.caption_editor.setCursor(QCursor(Qt.ArrowCursor))
                self.caption_editor.setStyleSheet("""
                    QTextEdit {
                        background: #1a1a2e;
                        border: 1px solid #2d2d3d;
                        border-radius: 12px;
                        padding: 15px;
                        color: #e0e0e0;
                        font-family: 'Consolas', 'Monaco', monospace;
                        line-height: 1.6;
                    }
                    QTextEdit:focus {
                        border: 2px solid #FF6B35;
                    }
                """)
                
        def save_caption_edits(self):
            """Save edited captions with validation"""
            text = self.caption_editor.toPlainText()
            blocks = text.strip().split('\n\n')
            
            # Validate SRT format
            valid_blocks = []
            invalid_blocks = []
            
            for i, block in enumerate(blocks, 1):
                lines = block.strip().split('\n')
                if len(lines) >= 3 and '-->' in lines[1]:
                    # Check timecode format
                    timecode = lines[1]
                    if '-->' in timecode:
                        try:
                            start, end = timecode.split(' --> ')
                            # Validate time format
                            if ',' in start and ',' in end:
                                valid_blocks.append(block + '\n')
                            else:
                                invalid_blocks.append(i)
                        except:
                            invalid_blocks.append(i)
                    else:
                        invalid_blocks.append(i)
                else:
                    invalid_blocks.append(i)
                    
            if valid_blocks:
                self.current_subtitles = valid_blocks
                self.save_edit_btn.setEnabled(False)
                self.edit_mode_btn.setChecked(False)
                self.caption_editor.setReadOnly(True)
                
                # Reset edit mode styling
                self.caption_editor.setStyleSheet("""
                    QTextEdit {
                        background: #1a1a2e;
                        border: 1px solid #2d2d3d;
                        border-radius: 12px;
                        padding: 15px;
                        color: #e0e0e0;
                        font-family: 'Consolas', 'Monaco', monospace;
                        line-height: 1.6;
                    }
                    QTextEdit:focus {
                        border: 2px solid #FF6B35;
                    }
                """)
                
                self.statusBar().showMessage(f"✅ Saved {len(valid_blocks)} captions!")
                self.stats_badge.setText("💾 SAVED")
                
                QMessageBox.information(self, "Changes Saved", 
                    f"✅ Successfully saved {len(valid_blocks)} captions!\n\n"
                    f"Your edits have been applied and can now be exported.")
            else:
                QMessageBox.warning(self, "Invalid Format", 
                    "❌ Could not parse edited captions.\n\n"
                    "Please ensure the SRT format is correct:\n\n"
                    "1\n"
                    "00:00:00,000 --> 00:00:05,000\n"
                    "Your caption text here\n\n"
                    f"Invalid blocks detected: {invalid_blocks}")
                    
        def clear_captions(self):
            """Clear all captions from editor"""
            if self.current_subtitles:
                reply = QMessageBox.question(self, "Clear Captions", 
                    "Are you sure you want to clear all captions?\n\nThis action cannot be undone.",
                    QMessageBox.Yes | QMessageBox.No)
                    
                if reply == QMessageBox.Yes:
                    self.current_subtitles = []
                    self.current_segments = []
                    self.caption_editor.clear()
                    self.export_srt_btn.setEnabled(False)
                    self.export_ass_btn.setEnabled(False)
                    self.statusBar().showMessage("Captions cleared")
                    self.stats_badge.setText("🗑️ CLEARED")
                    
        def copy_captions(self):
            """Copy captions to clipboard"""
            text = self.caption_editor.toPlainText()
            if text:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                self.statusBar().showMessage("Captions copied to clipboard")
                self.stats_badge.setText("📋 COPIED")
            else:
                QMessageBox.warning(self, "Nothing to Copy", 
                    "No captions to copy. Please generate captions first.")
                
        def toggle_waveform(self, visible):
            """Toggle waveform visualization"""
            if hasattr(self, 'media_player'):
                if visible:
                    self.media_player.waveform_container.setVisible(True)
                    self.statusBar().showMessage("Waveform visualization enabled")
                else:
                    self.media_player.waveform_container.setVisible(False)
                    self.statusBar().showMessage("Waveform visualization disabled")
                    
        def show_settings(self):
            """Show settings dialog"""
            dialog = QDialog(self)
            dialog.setWindowTitle("Settings")
            dialog.setMinimumWidth(500)
            dialog.setMinimumHeight(400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1a1a2e;
                }
                QLabel {
                    color: #ddd;
                }
                QGroupBox {
                    color: #FF6B35;
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Create tabs
            tabs = QTabWidget()
            tabs.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #3d3d4d;
                    border-radius: 8px;
                    background: #252535;
                }
                QTabBar::tab {
                    background: #2d2d3d;
                    padding: 8px 16px;
                    margin-right: 4px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background: #FF6B35;
                    color: white;
                }
                QTabBar::tab:hover:!selected {
                    background: #3d3d4d;
                }
            """)
            
            # General settings tab
            general_tab = QWidget()
            general_layout = QVBoxLayout(general_tab)
            
            # Theme selection
            theme_group = QGroupBox("Appearance")
            theme_layout = QVBoxLayout(theme_group)
            
            self.theme_combo = QComboBox()
            self.theme_combo.addItems(["Dark", "Light", "System"])
            self.theme_combo.setCurrentText("Dark")
            self.theme_combo.setStyleSheet("""
                QComboBox {
                    background: #1a1a2e;
                    border: 1px solid #3d3d4d;
                    border-radius: 6px;
                    padding: 6px;
                    color: white;
                }
            """)
            theme_layout.addWidget(QLabel("Theme:"))
            theme_layout.addWidget(self.theme_combo)
            theme_group.setLayout(theme_layout)
            general_layout.addWidget(theme_group)
            
            # Performance settings
            perf_group = QGroupBox("Performance")
            perf_layout = QGridLayout(perf_group)
            
            perf_layout.addWidget(QLabel("CPU Threads:"), 0, 0)
            self.threads_spin = QSpinBox()
            self.threads_spin.setRange(1, 16)
            self.threads_spin.setValue(4)
            self.threads_spin.setStyleSheet("""
                QSpinBox {
                    background: #1a1a2e;
                    border: 1px solid #3d3d4d;
                    border-radius: 6px;
                    padding: 4px;
                    color: white;
                }
            """)
            perf_layout.addWidget(self.threads_spin, 0, 1)
            
            self.gpu_check = QCheckBox("Use GPU acceleration (experimental)")
            self.gpu_check.setStyleSheet("""
                QCheckBox {
                    color: #ccc;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 4px;
                    border: 2px solid #FF6B35;
                    background: #1a1a2e;
                }
                QCheckBox::indicator:checked {
                    background-color: #FF6B35;
                }
            """)
            perf_layout.addWidget(self.gpu_check, 1, 0, 1, 2)
            
            self.cache_check = QCheckBox("Enable caching")
            self.cache_check.setChecked(True)
            perf_layout.addWidget(self.cache_check, 2, 0, 1, 2)
            
            general_layout.addWidget(perf_group)
            general_layout.addStretch()
            
            # Cache settings tab
            cache_tab = QWidget()
            cache_layout = QVBoxLayout(cache_tab)
            
            cache_group = QGroupBox("Cache Management")
            cache_group_layout = QVBoxLayout(cache_group)
            
            cache_layout.addWidget(QLabel("Cache Statistics:"))
            stats = self.cache.get_stats()
            stats_label = QLabel(f"""
                • Total entries: {stats['count']}
                • Cache size: {stats['size'] / (1024*1024):.2f} MB
                • Audio duration: {stats['duration'] / 3600:.1f} hours
            """)
            stats_label.setStyleSheet("color: #aaa; font-family: monospace;")
            cache_group_layout.addWidget(stats_label)
            
            clear_cache_btn = AnimatedButton("Clear All Cache", "#e74c3c", "#c0392b")
            clear_cache_btn.clicked.connect(self.clear_cache)
            cache_group_layout.addWidget(clear_cache_btn)
            
            vacuum_btn = AnimatedButton("Optimize Database", "#3498db", "#2980b9")
            vacuum_btn.clicked.connect(self.vacuum_database)
            cache_group_layout.addWidget(vacuum_btn)
            
            cache_group.setLayout(cache_group_layout)
            cache_layout.addWidget(cache_group)
            cache_layout.addStretch()
            
            # About tab
            about_tab = QWidget()
            about_layout = QVBoxLayout(about_tab)
            
            about_text = QLabel("""
                <h2 style="color: #FF6B35;">NotY Caption Generator AI</h2>
                <p><b>Version:</b> 7.1</p>
                <p><b>Developer:</b> NotY215</p>
                <p><b>License:</b> LGPL-3.0</p>
                <br>
                <p><b>Features:</b></p>
                <ul>
                    <li>AI-powered transcription using OpenAI Whisper</li>
                    <li>Support for 20+ languages</li>
                    <li>Vocal separation with Spleeter</li>
                    <li>YouTube video download</li>
                    <li>Multiple subtitle formats (SRT, ASS, VTT)</li>
                    <li>Real-time playback with highlighting</li>
                    <li>Smart caching for faster processing</li>
                </ul>
                <br>
                <p><b>Contact:</b> <a href="https://t.me/Noty_215" style="color: #FF6B35;">Telegram</a></p>
                <p><b>YouTube:</b> <a href="https://www.youtube.com/@NotY215" style="color: #FF6B35;">@NotY215</a></p>
            """)
            about_text.setWordWrap(True)
            about_text.setOpenExternalLinks(True)
            about_text.setStyleSheet("color: #ddd;")
            about_layout.addWidget(about_text)
            about_layout.addStretch()
            
            # Add tabs
            tabs.addTab(general_tab, "General")
            tabs.addTab(cache_tab, "Cache")
            tabs.addTab(about_tab, "About")
            
            layout.addWidget(tabs)
            
            # Dialog buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            buttons.setStyleSheet("""
                QPushButton {
                    background: #FF6B35;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 20px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #F7931E;
                }
            """)
            layout.addWidget(buttons)
            
            if dialog.exec_() == QDialog.Accepted:
                # Apply settings
                if self.theme_combo.currentText() != "Dark":
                    QMessageBox.information(self, "Restart Required", 
                        "Theme changes will take effect after restarting the application.")
                    
        def clear_cache(self):
            """Clear all cached transcriptions"""
            reply = QMessageBox.question(self, "Clear Cache", 
                "Are you sure you want to clear all cached transcriptions?\n\n"
                "This will remove all saved transcriptions and free up disk space.\n"
                "This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No)
                
            if reply == QMessageBox.Yes:
                self.cache.clear_all()
                self.statusBar().showMessage("Cache cleared successfully")
                self.stats_badge.setText("🗑️ CACHE CLEARED")
                QMessageBox.information(self, "Cache Cleared", 
                    "All cached transcriptions have been removed.")
                
        def vacuum_database(self):
            """Optimize database"""
            try:
                self.cache.vacuum()
                self.statusBar().showMessage("Database optimized")
                self.stats_badge.setText("💾 OPTIMIZED")
                QMessageBox.information(self, "Optimization Complete", 
                    "Database has been optimized for better performance.")
            except Exception as e:
                QMessageBox.critical(self, "Optimization Failed", 
                    f"Failed to optimize database:\n\n{str(e)}")
                
        def show_about(self):
            """Show about dialog"""
            about_text = f"""
                <h2 style="color: #FF6B35;">🎬 NotY Caption Generator AI</h2>
                <p><b>Version:</b> 7.1</p>
                <p><b>Developer:</b> NotY215</p>
                <p><b>License:</b> LGPL-3.0</p>
                <br>
                <p><b>Description:</b></p>
                <p>Professional AI-powered subtitle generation using OpenAI Whisper.</p>
                <br>
                <p><b>Features:</b></p>
                <ul>
                    <li>Multiple Whisper models (tiny to large)</li>
                    <li>20+ languages with accuracy tiers</li>
                    <li>Vocal separation with Spleeter</li>
                    <li>YouTube download support</li>
                    <li>Smart subtitle formatting</li>
                    <li>SQLite caching for speed</li>
                    <li>Real-time playback with highlighting</li>
                    <li>Multiple output formats (SRT/ASS/VTT)</li>
                </ul>
                <br>
                <p><b>Contact:</b> <a href="https://t.me/Noty_215" style="color: #FF6B35;">Telegram</a></p>
                <p><b>YouTube:</b> <a href="https://www.youtube.com/@NotY215" style="color: #FF6B35;">@NotY215</a></p>
                <p><b>Source:</b> <a href="#" style="color: #FF6B35;">GitHub</a></p>
            """
            
            QMessageBox.about(self, "About NotY Caption Generator AI", about_text)
            
        def highlight_current_caption(self, current_time: float):
            """Highlight the caption corresponding to current playback time"""
            if not self.current_subtitles:
                return
                
            for i, caption in enumerate(self.current_subtitles):
                lines = caption.split('\n')
                if len(lines) >= 2 and '-->' in lines[1]:
                    try:
                        start_str, end_str = lines[1].split(' --> ')
                        start = self._parse_srt_time(start_str)
                        end = self._parse_srt_time(end_str)
                        
                        if start <= current_time <= end:
                            # Find caption position in text
                            cursor = self.caption_editor.textCursor()
                            text = self.caption_editor.toPlainText()
                            
                            # Find the caption block
                            pos = text.find(caption)
                            if pos >= 0:
                                # Select the caption
                                cursor.setPosition(pos)
                                cursor.movePosition(QTextCursor.NextCharacter, 
                                                    QTextCursor.KeepAnchor, len(caption))
                                self.caption_editor.setTextCursor(cursor)
                                
                                # Scroll to make it visible
                                self.caption_editor.ensureCursorVisible()
                                
                                # Change background color temporarily
                                self.caption_editor.setExtraSelections([])
                                selection = QTextEdit.ExtraSelection()
                                selection.format.setBackground(QColor(255, 107, 53, 50))
                                selection.cursor = cursor
                                self.caption_editor.setExtraSelections([selection])
                            break
                    except Exception as e:
                        continue
                        
        def _parse_srt_time(self, time_str: str) -> float:
            """Parse SRT time format to seconds"""
            try:
                time_str = time_str.replace(',', '.')
                parts = time_str.split(':')
                if len(parts) == 3:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(parts[2])
                    return hours * 3600 + minutes * 60 + seconds
            except:
                pass
            return 0
            
        def resizeEvent(self, event):
            """Handle window resize - save geometry"""
            super().resizeEvent(event)
            # Update splitter proportions
            splitter = self.findChild(QSplitter)
            if splitter and splitter.width() > 0:
                # Save splitter sizes to config
                self.config.set('ui.splitter_sizes', splitter.sizes())
                
        def closeEvent(self, event):
            """Handle application close with cleanup"""
            # Check if transcription is running
            if self.worker and self.worker.isRunning():
                reply = QMessageBox.question(self, "Stop Processing", 
                    "Transcription is in progress. Are you sure you want to exit?\n\n"
                    "This will stop the current transcription job.",
                    QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.worker.stop()
                    self.worker.wait()
                else:
                    event.ignore()
                    return
                    
            # Stop media player
            if hasattr(self, 'media_player'):
                self.media_player.stop()
                
            # Save window geometry
            self.config.set('ui.window_width', self.width())
            self.config.set('ui.window_height', self.height())
            
            # Save settings
            self._save_settings()
            
            # Clean up temporary files
            try:
                temp_dir = Path(tempfile.gettempdir()) / 'NotYCaptionGenAI'
                if temp_dir.exists():
                    # Only clean files older than 1 hour
                    current_time = time.time()
                    for file in temp_dir.iterdir():
                        if file.is_file() and (current_time - file.stat().st_mtime) > 3600:
                            file.unlink()
            except Exception as e:
                pass
                
            self.logger.info("Application closed")
            event.accept()
            
        def keyPressEvent(self, event):
            """Handle keyboard shortcuts"""
            if event.key() == Qt.Key_Escape:
                if self.worker and self.worker.isRunning():
                    self.worker.stop()
                    self.statusBar().showMessage("Transcription stopped")
                else:
                    self.close()
            elif event.modifiers() == Qt.ControlModifier:
                if event.key() == Qt.Key_S:
                    if self.current_subtitles:
                        self.export_subtitles('srt')
                elif event.key() == Qt.Key_E:
                    self.edit_mode_btn.toggle()
                elif event.key() == Qt.Key_Delete:
                    self.clear_captions()
            else:
                super().keyPressEvent(event)
                
        def dragEnterEvent(self, event):
            """Handle drag enter for file drop"""
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
                self.statusBar().showMessage("Drop file to import")
                
        def dropEvent(self, event):
            """Handle file drop"""
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path and Path(file_path).exists():
                    self.load_media(file_path)
                    
        def wheelEvent(self, event):
            """Handle mouse wheel for zooming (Ctrl+wheel)"""
            if event.modifiers() == Qt.ControlModifier:
                # Zoom in/out of caption editor
                font = self.caption_editor.font()
                delta = event.angleDelta().y()
                new_size = font.pointSize() + (1 if delta > 0 else -1)
                if 8 <= new_size <= 20:
                    font.setPointSize(new_size)
                    self.caption_editor.setFont(font)
                    self.statusBar().showMessage(f"Font size: {new_size}")
                event.accept()
            else:
                super().wheelEvent(event)


# ============================================================================
# SECTION 4: Main Entry Point
# ============================================================================

def main():
    """Main entry point - automatically selects GUI or CLI"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="NotY Caption Generator AI v7.1")
    parser.add_argument("--cli", action="store_true", help="Force CLI mode")
    parser.add_argument("--input", "-i", type=str, help="Input file path (CLI mode)")
    parser.add_argument("--output", "-o", type=str, help="Output file path (CLI mode)")
    parser.add_argument("--model", "-m", type=str, default="base", help="Whisper model (tiny/base/small/medium/large)")
    parser.add_argument("--language", "-l", type=str, default="en", help="Language code")
    parser.add_argument("--translate", action="store_true", help="Translate to English")
    args = parser.parse_args()
    
    # Force CLI mode if requested
    if args.cli:
        cli = NotyCaptionCLI()
        if args.input:
            # Direct processing mode
            input_path = Path(args.input)
            if input_path.exists():
                cli.settings['model'] = args.model
                cli.settings['language'] = args.language
                cli.settings['task'] = 'translate' if args.translate else 'transcribe'
                cli.process_file(input_path)
            else:
                print(f"{Colors.BRIGHT_RED}Error: Input file not found: {args.input}{Colors.RESET}")
                sys.exit(1)
        else:
            cli.run()
    elif GUI_AVAILABLE:
        # GUI mode
        app = QApplication(sys.argv)
        app.setApplicationName("NotY Caption Generator AI")
        app.setOrganizationName("NotY215")
        
        # Set application icon
        app.setWindowIcon(QIcon())
        
        # Enable high DPI scaling
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        window = NotYCaptionWindow()
        window.show()
        
        sys.exit(app.exec_())
    else:
        # Fallback to CLI
        cli = NotyCaptionCLI()
        cli.run()


if __name__ == "__main__":
    main()