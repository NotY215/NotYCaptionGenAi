#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NotY Caption Generator AI v7.1
All-in-one file - No external src folder dependencies
Professional Vocal Separation with Spleeter & TensorFlow
Copyright (c) 2026 NotY215
"""

import os
import sys
import atexit
import signal
import time
import tempfile
import shutil
import argparse
import platform
import subprocess
import re
import json
import hashlib
import sqlite3
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# ============================================================================
# CRITICAL: Path handling for packaged app
# ============================================================================
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    
    packages_path = os.path.join(application_path, '_pythonPackages_')
    if os.path.exists(packages_path) and packages_path not in sys.path:
        sys.path.insert(0, packages_path)
    
    os.environ['PATH'] = application_path + os.pathsep + os.environ.get('PATH', '')
    os.environ['TORCH_USE_RTLD_GLOBAL'] = '1'
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    os.environ['OMP_NUM_THREADS'] = '4'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

# ============================================================================
# Application Metadata
# ============================================================================
APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "7.1"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"
APP_LICENSE = "LGPL-3.0"
APP_TELEGRAM = "https://t.me/Noty_215"
APP_YOUTUBE = "https://www.youtube.com/@NotY215"
APP_DATA_FOLDER = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'NotYCaptionGenAI')
APP_LOGS_FOLDER = os.path.join(APP_DATA_FOLDER, 'logs')
APP_MODELS_FOLDER = os.path.join(APP_DATA_FOLDER, 'models')

# Create AppData folders
os.makedirs(APP_DATA_FOLDER, exist_ok=True)
os.makedirs(APP_LOGS_FOLDER, exist_ok=True)
os.makedirs(APP_MODELS_FOLDER, exist_ok=True)

# ============================================================================
# Logging Setup
# ============================================================================
log_filename = os.path.join(APP_LOGS_FOLDER, f'app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            self._style._fmt = '%(asctime)s [i] %(message)s'
        elif record.levelno == logging.WARNING:
            self._style._fmt = '%(asctime)s [!] %(message)s'
        elif record.levelno == logging.ERROR:
            self._style._fmt = '%(asctime)s [✗] %(message)s'
        else:
            self._style._fmt = '%(asctime)s [•] %(message)s'
        return super().format(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(CustomFormatter())
logger.addHandler(file_handler)

# ============================================================================
# Colors for Console Output
# ============================================================================
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if platform.system() == "Windows":
    try:
        import colorama
        colorama.init()
    except:
        pass

# ============================================================================
# Progress Bar
# ============================================================================
class ProgressBar:
    def __init__(self, total: int, description: str = "Processing", width: int = 50):
        self.total = total
        self.description = description
        self.width = width
        self.current = 0
        self.lock = threading.Lock()
        
    def update(self, increment: int = 1, message: str = ""):
        with self.lock:
            self.current = min(self.current + increment, self.total)
            percent = self.current / self.total
            filled = int(self.width * percent)
            bar = '█' * filled + '░' * (self.width - filled)
            if message:
                print(f"\r{Colors.CYAN}[{bar}] {percent*100:.0f}% - {self.description} - {message}{Colors.RESET}", end="", flush=True)
            else:
                print(f"\r{Colors.CYAN}[{bar}] {percent*100:.0f}% - {self.description}{Colors.RESET}", end="", flush=True)
            if self.current >= self.total:
                print()
                
    def set_total(self, total: int):
        self.total = total
        
    def reset(self):
        self.current = 0

# ============================================================================
# Language Tiers with Accuracy Information
# ============================================================================
LANGUAGE_TIERS = {
    "high": {
        "name": "High Accuracy (90-95%)",
        "description": "Best for clean audio, professional content",
        "languages": [
            ("English", "en", "English - Best for US/UK content"),
            ("Spanish", "es", "Spanish - European and Latin American"),
            ("Italian", "it", "Italian - Standard Italian"),
            ("Portuguese", "pt", "Portuguese - European and Brazilian"),
            ("German", "de", "German - Standard German"),
            ("Japanese", "ja", "Japanese - Standard Japanese"),
            ("French", "fr", "French - European and Canadian"),
            ("Catalan", "ca", "Catalan - Catalonia region"),
        ]
    },
    "medium": {
        "name": "Medium Accuracy (70-85%)",
        "description": "Good for clear audio with some background noise",
        "languages": [
            ("Swedish", "sv", "Swedish - Standard Swedish"),
            ("Russian", "ru", "Russian - Standard Russian"),
            ("Polish", "pl", "Polish - Standard Polish"),
            ("Dutch", "nl", "Dutch - Netherlands and Belgian"),
        ]
    },
    "low": {
        "name": "Lower Accuracy (50-70%)",
        "description": "May have errors, best for short clips",
        "languages": [
            ("Hindi", "hi", "Hindi - Devanagari script"),
            ("Tamil", "ta", "Tamil - Dravidian language"),
            ("Telugu", "te", "Telugu - South Indian language"),
            ("Punjabi", "pa", "Punjabi - Gurmukhi script"),
            ("Bengali", "bn", "Bengali - Eastern Indo-Aryan"),
            ("Urdu", "ur", "Urdu - Nastaliq script"),
            ("Marathi", "mr", "Marathi - Western India"),
            ("Gujarati", "gu", "Gujarati - Western India"),
            ("Kannada", "kn", "Kannada - South Indian"),
            ("Malayalam", "ml", "Malayalam - Kerala region"),
        ]
    }
}

# ============================================================================
# Whisper Models
# ============================================================================
WHISPER_MODELS = [
    ("tiny", "75 MB", "Fastest, lowest accuracy, good for testing", "0.5x realtime"),
    ("base", "150 MB", "Fast, moderate accuracy, good for short files", "1.0x realtime"),
    ("small", "500 MB", "Balanced speed/accuracy, recommended", "2.0x realtime"),
    ("medium", "1.5 GB", "High accuracy, slower, good for important content", "4.0x realtime"),
    ("large", "2.9 GB", "Best accuracy, slowest, for professional use", "8.0x realtime")
]

# ============================================================================
# Modes
# ============================================================================
MODES = [
    ("Normal Mode", "normal", "Transcribe in selected language without translation"),
    ("Translate Mode", "translate", "Transcribe and translate to English")
]

# ============================================================================
# Line Break Types
# ============================================================================
LINE_TYPES = [
    ("Auto (Recommended)", "auto", "Smart sentence detection with natural breaks", "1-50 chars"),
    ("Words", "words", "Break by word count", "1-30 words"),
    ("Letters", "letters", "Break by character limit", "10-80 chars")
]

# ============================================================================
# Vocal Separation Options
# ============================================================================
VOCAL_OPTIONS = [
    ("No vocal separation", "none", "Fastest, use original audio", "0-1x speed"),
    ("2 Stems (Fast)", "2stems", "Vocals + Accompaniment, good quality", "1-2x slower"),
    ("4 Stems (Better)", "4stems", "Vocals + Drums + Bass + Other, better separation", "2-3x slower"),
    ("5 Stems (Best)", "5stems", "Vocals + Drums + Bass + Piano + Other, best quality", "3-4x slower")
]

# ============================================================================
# Supported File Extensions
# ============================================================================
SUPPORTED_EXTENSIONS = {
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm', '.flv', '.wmv'],
    'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma'],
    'all': ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm', '.flv', '.wmv',
            '.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma']
}

# ============================================================================
# Data Classes
# ============================================================================
@dataclass
class SubtitleEntry:
    index: int
    start: float
    end: float
    text: str
    
    def to_srt(self) -> str:
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        return f"{self.index}\n{format_time(self.start)} --> {format_time(self.end)}\n{self.text}\n\n"

@dataclass
class UserSelection:
    platform: str = ""
    source: str = ""
    vocal_separation: str = ""
    vocal_separation_name: str = ""
    model: str = ""
    model_name: str = ""
    mode: str = ""
    mode_name: str = ""
    language_code: str = ""
    language_name: str = ""
    line_type: str = ""
    line_type_name: str = ""
    limit: int = 5
    file_path: str = ""
    video_title: str = ""
    checkpoint: str = ""

# ============================================================================
# Whisper Import with Error Handling
# ============================================================================
WHISPER_AVAILABLE = False
SPLEETER_AVAILABLE = False
TENSORFLOW_AVAILABLE = False
whisper = None
Separator = None

try:
    import whisper
    WHISPER_AVAILABLE = True
    logger.info("Whisper loaded successfully")
    print(f"{Colors.GREEN}[✓] Whisper loaded successfully{Colors.RESET}")
except ImportError as e:
    logger.error(f"Whisper import failed: {e}")
    print(f"{Colors.YELLOW}[!] Whisper not found: {e}{Colors.RESET}")

try:
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    tf.autograph.set_verbosity(0)
    TENSORFLOW_AVAILABLE = True
    logger.info("TensorFlow loaded successfully")
    print(f"{Colors.GREEN}[✓] TensorFlow loaded successfully{Colors.RESET}")
    
    from spleeter.separator import Separator
    SPLEETER_AVAILABLE = True
    logger.info("Spleeter loaded successfully")
    print(f"{Colors.GREEN}[✓] Spleeter loaded successfully{Colors.RESET}")
except ImportError as e:
    logger.warning(f"Spleeter/TensorFlow not available: {e}")
    print(f"{Colors.YELLOW}[!] Spleeter/TensorFlow not available. Vocal separation will use FFmpeg.{Colors.RESET}")

# ============================================================================
# Cache Manager
# ============================================================================
class CacheManager:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.conn = None
        self.cursor = None
        self.init_database()
        
    def init_database(self):
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = self.cache_dir / "cache.db"
            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS transcriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT UNIQUE,
                    model_name TEXT,
                    language TEXT,
                    mode TEXT,
                    vocal_separation TEXT,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init failed: {e}")
            
    def get_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def cache_transcription(self, file_hash: str, model_name: str, language: str, 
                           mode: str, vocal_separation: str, result: dict):
        if not self.conn or not self.cursor:
            return
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO transcriptions (file_hash, model_name, language, mode, vocal_separation, result) VALUES (?, ?, ?, ?, ?, ?)",
                (file_hash, model_name, language, mode, vocal_separation, json.dumps(result))
            )
            self.conn.commit()
            logger.info(f"Cached transcription for {file_hash[:8]}")
        except Exception as e:
            logger.error(f"Cache write failed: {e}")
            
    def get_cached_transcription(self, file_hash: str, model_name: str, language: str,
                                 mode: str, vocal_separation: str) -> Optional[dict]:
        if not self.conn or not self.cursor:
            return None
        try:
            self.cursor.execute(
                "SELECT result FROM transcriptions WHERE file_hash = ? AND model_name = ? AND language = ? AND mode = ? AND vocal_separation = ?",
                (file_hash, model_name, language, mode, vocal_separation)
            )
            row = self.cursor.fetchone()
            if row:
                logger.info(f"Cache hit for {file_hash[:8]}")
                return json.loads(row[0])
        except Exception as e:
            logger.error(f"Cache read failed: {e}")
        return None

# ============================================================================
# Audio Processor
# ============================================================================
class AudioProcessor:
    def __init__(self, ffmpeg_exe: Optional[Path] = None, ffprobe_exe: Optional[Path] = None):
        self.ffmpeg_exe = ffmpeg_exe
        self.ffprobe_exe = ffprobe_exe
        
    def check_ffmpeg(self) -> bool:
        if self.ffmpeg_exe and self.ffmpeg_exe.exists():
            return True
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return True
        except:
            return False
            
    def get_audio_duration(self, audio_path: Path) -> float:
        ffprobe_cmd = str(self.ffprobe_exe) if self.ffprobe_exe and self.ffprobe_exe.exists() else 'ffprobe'
        cmd = [ffprobe_cmd, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return 0.0
        
    def extract_audio(self, video_path: Path, progress_callback: Optional[Callable] = None) -> Optional[Path]:
        if not self.check_ffmpeg():
            logger.error("FFmpeg not found")
            return None
        temp_dir = Path(tempfile.gettempdir())
        audio_path = temp_dir / f"{video_path.stem}_temp_audio.wav"
        ffmpeg_cmd = str(self.ffmpeg_exe) if self.ffmpeg_exe and self.ffmpeg_exe.exists() else 'ffmpeg'
        cmd = [ffmpeg_cmd, '-i', str(video_path), '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-y', str(audio_path)]
        try:
            if progress_callback:
                progress_callback(10, "Extracting audio...")
            subprocess.run(cmd, capture_output=True, timeout=120)
            if audio_path.exists() and audio_path.stat().st_size > 0:
                logger.info(f"Audio extracted: {audio_path}")
                if progress_callback:
                    progress_callback(20, "Audio extracted")
                return audio_path
        except Exception as e:
            logger.error(f"Audio extraction failed: {e}")
        return None

# ============================================================================
# Vocal Separator with Spleeter and TensorFlow
# ============================================================================
class VocalSeparator:
    def __init__(self, ffmpeg_exe: Optional[Path] = None, pretrained_models_dir: Optional[Path] = None):
        self.ffmpeg_exe = ffmpeg_exe
        self.pretrained_models_dir = pretrained_models_dir
        self.separator = None
        self.current_model = "2stems"
        
    def is_available(self) -> bool:
        return SPLEETER_AVAILABLE or (self.ffmpeg_exe is not None and self.ffmpeg_exe.exists())
    
    def separate_vocals_spleeter(self, audio_path: Path, model: str = "2stems", progress_callback: Optional[Callable] = None) -> Optional[Path]:
        if not SPLEETER_AVAILABLE:
            return None
            
        if progress_callback:
            progress_callback(25, f"Separating vocals with Spleeter ({model})...")
        logger.info(f"Separating vocals with Spleeter ({model})...")
        print(f"{Colors.CYAN}[→] Separating vocals with Spleeter ({model})...{Colors.RESET}")
        
        temp_dir = Path(tempfile.gettempdir())
        output_dir = temp_dir / f"spleeter_output_{int(time.time())}"
        
        try:
            if self.pretrained_models_dir and self.pretrained_models_dir.exists():
                os.environ['SPLEETER_PRETRAINED_PATH'] = str(self.pretrained_models_dir)
                logger.info(f"Using local models from: {self.pretrained_models_dir}")
            
            if self.separator is None or self.current_model != model:
                logger.info(f"Loading Spleeter model...")
                print(f"{Colors.CYAN}[i] Loading Spleeter model...{Colors.RESET}")
                model_map = {
                    "2stems": "spleeter:2stems",
                    "4stems": "spleeter:4stems", 
                    "5stems": "spleeter:5stems"
                }
                self.separator = Separator(model_map.get(model, "spleeter:2stems"))
                self.current_model = model
            
            self.separator.separate_to_file(
                str(audio_path), str(output_dir),
                filename_format="{filename}_{instrument}.{codec}"
            )
            
            vocal_file = None
            for file in output_dir.rglob("*vocals.wav"):
                vocal_file = file
                break
            
            if vocal_file and vocal_file.exists():
                final_vocals = temp_dir / f"{audio_path.stem}_vocals.wav"
                shutil.copy2(vocal_file, final_vocals)
                shutil.rmtree(output_dir, ignore_errors=True)
                logger.info("Spleeter vocal separation complete")
                if progress_callback:
                    progress_callback(40, "Vocal separation complete")
                print(f"{Colors.GREEN}[✓] Spleeter vocal separation complete{Colors.RESET}")
                return final_vocals
            else:
                logger.warning("Could not find vocal track")
                return None
                
        except Exception as e:
            logger.error(f"Spleeter error: {e}")
            print(f"{Colors.YELLOW}[!] Spleeter error: {e}{Colors.RESET}")
            return None
            
    def separate_vocals_ffmpeg(self, audio_path: Path, progress_callback: Optional[Callable] = None) -> Optional[Path]:
        if not self.ffmpeg_exe or not self.ffmpeg_exe.exists():
            return None
            
        if progress_callback:
            progress_callback(25, "Isolating vocals with FFmpeg...")
        logger.info("Isolating vocals with FFmpeg...")
        print(f"{Colors.CYAN}[→] Isolating vocals with FFmpeg...{Colors.RESET}")
        
        temp_dir = Path(tempfile.gettempdir())
        vocal_path = temp_dir / f"{audio_path.stem}_vocals.wav"
        ffmpeg_cmd = str(self.ffmpeg_exe)
        
        cmd = [
            ffmpeg_cmd, '-i', str(audio_path),
            '-af', 'highpass=f=100, lowpass=f=10000, volume=2.0, acompressor=threshold=0.1:ratio=2:attack=5:release=50',
            '-y', str(vocal_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=180)
            if vocal_path.exists() and vocal_path.stat().st_size > 0:
                logger.info("FFmpeg vocal isolation complete")
                if progress_callback:
                    progress_callback(40, "Vocal isolation complete")
                print(f"{Colors.GREEN}[✓] FFmpeg vocal isolation complete{Colors.RESET}")
                return vocal_path
        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            print(f"{Colors.YELLOW}[!] FFmpeg error: {e}{Colors.RESET}")
        return None
        
    def separate(self, audio_path: Path, model: str = "2stems", progress_callback: Optional[Callable] = None) -> Optional[Path]:
        if SPLEETER_AVAILABLE and model != "none":
            result = self.separate_vocals_spleeter(audio_path, model, progress_callback)
            if result:
                return result
        return self.separate_vocals_ffmpeg(audio_path, progress_callback)

# ============================================================================
# Transcriber
# ============================================================================
class Transcriber:
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.model = None
        self.current_model_name = None
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def is_available(self) -> bool:
        return WHISPER_AVAILABLE and whisper is not None
        
    def load_model(self, model_name: str, progress_callback: Optional[Callable] = None) -> bool:
        if not self.is_available():
            logger.error("Whisper not available")
            return False
        try:
            if progress_callback:
                progress_callback(50, f"Loading {model_name} model...")
            logger.info(f"Loading {model_name} model...")
            print(f"{Colors.CYAN}[→] Loading {model_name} model...{Colors.RESET}")
            load_start = time.time()
            self.model = whisper.load_model(model_name, download_root=str(self.models_dir))
            self.current_model_name = model_name
            load_time = time.time() - load_start
            logger.info(f"Model loaded in {load_time:.1f}s")
            if progress_callback:
                progress_callback(60, f"Model loaded in {load_time:.1f}s")
            print(f"{Colors.GREEN}[✓] Model loaded in {load_time:.1f}s{Colors.RESET}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            print(f"{Colors.RED}[✗] Failed to load model: {e}{Colors.RESET}")
            return False
            
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        words = text.split()
        cleaned = []
        prev = None
        count = 0
        for w in words:
            if w == prev:
                count += 1
                if count < 2:
                    cleaned.append(w)
            else:
                count = 0
                cleaned.append(w)
                prev = w
        text = ' '.join(cleaned)
        patterns = [r'(\S+)\s+\1\s+\1', r'\b(?:सुबासे|गुम्राम|अपने)\s+\1']
        for p in patterns:
            text = re.sub(p, '', text)
        return re.sub(r'\s+', ' ', text).strip()
        
    def transcribe(self, audio_path: Path, language: str, mode: str, progress_callback: Optional[Callable] = None) -> Dict:
        if not self.model:
            logger.error("No model loaded")
            return {"segments": []}
        
        task = "translate" if mode == "translate" else "transcribe"
        lang = None if language == "auto" else language
        
        if progress_callback:
            progress_callback(70, f"Transcribing with {task} mode...")
        logger.info(f"Transcribing with {task} mode...")
        print(f"{Colors.CYAN}[i] Transcribing with {task} mode...{Colors.RESET}")
        
        try:
            result = self.model.transcribe(
                str(audio_path), language=lang, task=task, verbose=False,
                word_timestamps=True, fp16=False, no_speech_threshold=0.6,
                compression_ratio_threshold=2.4, logprob_threshold=-1.0
            )
            
            if "segments" in result:
                for seg in result["segments"]:
                    if "text" in seg:
                        seg["text"] = self.clean_text(seg["text"])
            
            logger.info(f"Transcription completed")
            if progress_callback:
                progress_callback(85, "Transcription complete")
            return result
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            print(f"{Colors.RED}[✗] Transcription failed: {e}{Colors.RESET}")
            return {"segments": []}

# ============================================================================
# Subtitle Generator
# ============================================================================
class SubtitleGenerator:
    def split_by_words(self, text: str, words_per_line: int) -> List[str]:
        words = text.split()
        return [' '.join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)]
    
    def split_by_letters(self, text: str, letters_per_line: int) -> List[str]:
        if len(text) <= letters_per_line:
            return [text]
        lines = []
        current = ""
        for word in text.split():
            if len(current) + len(word) + (1 if current else 0) <= letters_per_line:
                current += (" " + word) if current else word
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
    
    def split_smart(self, text: str, max_chars: int = 42) -> List[str]:
        if len(text) <= max_chars:
            return [text]
        for punct in ['. ', '! ', '? ', '; ', ': ', ', ']:
            if punct in text:
                parts = [p.strip() + punct.strip() for p in text.split(punct) if p.strip()]
                lines = []
                current = ""
                for part in parts:
                    if len(current) + len(part) <= max_chars:
                        current += part
                    else:
                        if current:
                            lines.append(current.strip())
                        current = part
                if current:
                    lines.append(current.strip())
                if len(lines) > 1:
                    return lines
        return self.split_by_words(text, max(1, max_chars // 10))
    
    def generate_subtitles(self, segments: List[Dict], line_type: str, limit: int, progress_callback: Optional[Callable] = None) -> List[SubtitleEntry]:
        subtitles = []
        idx = 1
        
        if progress_callback:
            progress_callback(90, "Generating subtitles...")
        
        for seg in segments:
            text = seg.get("text", "").strip()
            if not text or len(text) < 2:
                continue
            
            start = seg.get("start", 0)
            end = seg.get("end", start + 1)
            duration = end - start
            
            if line_type == "words":
                lines = self.split_by_words(text, max(1, limit))
            elif line_type == "letters":
                lines = self.split_by_letters(text, max(10, limit))
            else:
                lines = self.split_smart(text)
            
            if len(lines) == 1:
                subtitles.append(SubtitleEntry(idx, start, end, lines[0]))
                idx += 1
            else:
                line_duration = duration / len(lines)
                for i, line in enumerate(lines):
                    line_start = start + (i * line_duration)
                    line_end = line_start + line_duration
                    subtitles.append(SubtitleEntry(idx, line_start, line_end, line))
                    idx += 1
        
        if progress_callback:
            progress_callback(95, f"Generated {len(subtitles)} subtitles")
        
        return subtitles
    
    def save_srt(self, output_path: Path, subtitles: List[SubtitleEntry]):
        with open(output_path, 'w', encoding='utf-8') as f:
            for sub in subtitles:
                f.write(sub.to_srt())

# ============================================================================
# Menu System with Checkpoint-Based Back Navigation
# ============================================================================
class MenuItem:
    def __init__(self, key: str, title: str, description: str = "", action=None, submenu=None):
        self.key = key
        self.title = title
        self.description = description
        self.action = action
        self.submenu = submenu

class Menu:
    def __init__(self, name: str = "main", parent=None, checkpoint_id: str = None):
        self.name = name
        self.parent = parent
        self.items: List[MenuItem] = []
        self.checkpoint_id = checkpoint_id or name
        
    def add(self, key: str, title: str, description: str = "", action=None, submenu=None):
        self.items.append(MenuItem(key, title, description, action, submenu))
        return self
    
    def clear_screen(self):
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def show(self):
        while True:
            self.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}")
            print("+" + "=" * 60 + "+")
            print("|" + f"{APP_NAME} v{APP_VERSION}".center(60) + "|")
            print("|" + f"Copyright (c) {APP_YEAR} {APP_AUTHOR}".center(60) + "|")
            print("|" + f"License: {APP_LICENSE}".center(60) + "|")
            print("|" + "Powered by OpenAI Whisper + Spleeter".center(60) + "|")
            print("+" + "=" * 60 + "+")
            print(f"{Colors.RESET}")
            
            if self.parent:
                print(f"\n{Colors.CYAN}📍 Path: {self.get_path()}{Colors.RESET}\n")
            
            print(f"{Colors.CYAN}{Colors.BOLD}{self.name.upper()}{Colors.RESET}\n")
            
            for i, item in enumerate(self.items, 1):
                print(f"  {Colors.GREEN}{i}{Colors.RESET}) {Colors.WHITE}{item.title}{Colors.RESET}")
                if item.description:
                    print(f"     {Colors.CYAN}└─ {item.description}{Colors.RESET}")
            
            if self.parent:
                print(f"\n  {Colors.YELLOW}0{Colors.RESET}) {Colors.YELLOW}Back to previous menu{Colors.RESET}")
            else:
                print(f"\n  {Colors.RED}0{Colors.RESET}) {Colors.RED}Exit{Colors.RESET}")
            
            print()
            choice = input(f"{Colors.CYAN}Choose option (0-{len(self.items)}): {Colors.RESET}").strip()
            
            if choice == "0":
                if self.parent:
                    return "back"
                else:
                    return "exit"
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.items):
                    item = self.items[idx]
                    if item.submenu:
                        result = item.submenu.show()
                        if result == "exit":
                            return "exit"
                    elif item.action:
                        item.action()
                else:
                    print(f"{Colors.RED}[✗] Invalid option. Choose 0-{len(self.items)}{Colors.RESET}")
                    input("Press Enter to continue...")
            except ValueError:
                print(f"{Colors.RED}[✗] Invalid input. Please enter a number.{Colors.RESET}")
                input("Press Enter to continue...")
    
    def get_path(self) -> str:
        path = []
        current = self
        while current:
            path.insert(0, current.name)
            current = current.parent
        return " > ".join(path)

# ============================================================================
# NotYCaptionGenerator - Main Application Class
# ============================================================================
class NotYCaptionGenerator:
    def __init__(self, media_path: Optional[str] = None):
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        logger.info(f"Log file: {log_filename}")
        
        # Initialize paths
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
            
        self.models_dir = self.base_dir / "models"
        self.ffmpeg_dir = self.base_dir / "ffmpeg"
        self.cache_dir = self.base_dir / "cache"
        self.pretrained_models_dir = self.base_dir / "pretrained_models"
        
        # Check AppData models (priority)
        appdata_models = Path(APP_MODELS_FOLDER)
        if appdata_models.exists() and any(appdata_models.iterdir()):
            self.models_dir = appdata_models
            logger.info(f"Using models from AppData: {appdata_models}")
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg setup
        if platform.system() == "Windows":
            self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg.exe"
            self.ffprobe_exe = self.ffmpeg_dir / "ffprobe.exe"
        else:
            self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg"
            self.ffprobe_exe = self.ffmpeg_dir / "ffprobe"
        
        if self.ffmpeg_dir.exists():
            os.environ['PATH'] = str(self.ffmpeg_dir) + os.pathsep + os.environ.get('PATH', '')
        
        # Initialize components
        self.cache_manager = CacheManager(self.cache_dir)
        self.audio_processor = AudioProcessor(self.ffmpeg_exe, self.ffprobe_exe)
        self.vocal_separator = VocalSeparator(self.ffmpeg_exe, self.pretrained_models_dir)
        self.transcriber = Transcriber(self.models_dir)
        self.subtitle_generator = SubtitleGenerator()
        
        self.media_path_arg = media_path
        self.selection = UserSelection()
        self.checkpoint_stack = []
        
        atexit.register(self.cleanup)
        logger.info("Application initialized successfully")
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            temp_dir = Path(tempfile.gettempdir())
            patterns = ["*_temp_audio.wav", "*_vocals.wav", "youtube_audio_*", "spleeter_*", "chunk_*", "spleeter_output_*"]
            for pattern in patterns:
                for file in temp_dir.glob(pattern):
                    try:
                        if file.is_file():
                            file.unlink()
                            logger.debug(f"Removed temp file: {file}")
                    except:
                        pass
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def update_progress(self, percent: int, message: str):
        """Update progress display"""
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r{Colors.CYAN}[{bar}] {percent}% - {message}{Colors.RESET}", end="", flush=True)
        if percent >= 100:
            print()
    
    def print_selection_summary(self):
        """Print a summary of all user selections"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}SELECTION SUMMARY{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"  {Colors.GREEN}Platform:{Colors.RESET} {self.selection.platform}")
        print(f"  {Colors.GREEN}Source:{Colors.RESET} {self.selection.source}")
        print(f"  {Colors.GREEN}Vocal Separation:{Colors.RESET} {self.selection.vocal_separation_name}")
        print(f"  {Colors.GREEN}Whisper Model:{Colors.RESET} {self.selection.model_name.upper()}")
        print(f"  {Colors.GREEN}Mode:{Colors.RESET} {self.selection.mode_name}")
        print(f"  {Colors.GREEN}Language:{Colors.RESET} {self.selection.language_name}")
        print(f"  {Colors.GREEN}Line Break:{Colors.RESET} {self.selection.line_type_name}")
        if self.selection.line_type != "auto":
            print(f"  {Colors.GREEN}Limit:{Colors.RESET} {self.selection.limit}")
        print(f"  {Colors.GREEN}File:{Colors.RESET} {self.selection.file_path}")
        if self.selection.video_title:
            print(f"  {Colors.GREEN}Video Title:{Colors.RESET} {self.selection.video_title[:60]}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    def save_checkpoint(self, checkpoint_name: str):
        """Save current checkpoint for back navigation"""
        self.selection.checkpoint = checkpoint_name
        self.checkpoint_stack.append(checkpoint_name)
        logger.debug(f"Checkpoint saved: {checkpoint_name}")
    
    def go_back_to_checkpoint(self, target_checkpoint: str) -> bool:
        """Navigate back to a specific checkpoint"""
        while self.checkpoint_stack and self.checkpoint_stack[-1] != target_checkpoint:
            self.checkpoint_stack.pop()
        if self.checkpoint_stack:
            self.selection.checkpoint = self.checkpoint_stack[-1]
            return True
        return False
    
    def select_vocal_separation(self) -> bool:
        """Vocal separation selection menu"""
        self.save_checkpoint("vocal_separation")
        while True:
            self.menu.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}VOCAL SEPARATION{Colors.RESET}\n")
            print(f"{Colors.YELLOW}Note: Spleeter with TensorFlow provides better quality{Colors.RESET}\n")
            for i, (name, key, desc, speed) in enumerate(VOCAL_OPTIONS, 1):
                print(f"  {Colors.GREEN}{i}{Colors.RESET}) {Colors.WHITE}{name}{Colors.RESET}")
                print(f"     {Colors.CYAN}└─ {desc}{Colors.RESET}")
                print(f"     {Colors.CYAN}   Speed: {speed}{Colors.RESET}")
            print(f"\n  {Colors.YELLOW}0{Colors.RESET}) {Colors.YELLOW}Back{Colors.RESET}")
            
            choice = input(f"\n{Colors.CYAN}Choose option (0-{len(VOCAL_OPTIONS)}): {Colors.RESET}").strip()
            if choice == "0":
                return False
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(VOCAL_OPTIONS):
                    self.selection.vocal_separation = VOCAL_OPTIONS[idx][1]
                    self.selection.vocal_separation_name = VOCAL_OPTIONS[idx][0]
                    logger.info(f"Selected vocal separation: {self.selection.vocal_separation_name}")
                    return True
                else:
                    print(f"{Colors.RED}[✗] Invalid option{Colors.RESET}")
                    input("Press Enter...")
            except ValueError:
                print(f"{Colors.RED}[✗] Invalid input{Colors.RESET}")
                input("Press Enter...")
    
    def select_model(self) -> bool:
        """Whisper model selection menu"""
        self.save_checkpoint("model")
        while True:
            self.menu.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}WHISPER MODEL{Colors.RESET}\n")
            print(f"{Colors.YELLOW}Note: Larger models = better accuracy but slower{Colors.RESET}\n")
            for i, (name, size, desc, speed) in enumerate(WHISPER_MODELS, 1):
                print(f"  {Colors.GREEN}{i}{Colors.RESET}) {Colors.WHITE}{name.upper()}{Colors.RESET}")
                print(f"     {Colors.CYAN}└─ Size: {size}{Colors.RESET}")
                print(f"     {Colors.CYAN}   {desc}{Colors.RESET}")
                print(f"     {Colors.CYAN}   Speed: {speed}{Colors.RESET}")
            print(f"\n  {Colors.YELLOW}0{Colors.RESET}) {Colors.YELLOW}Back{Colors.RESET}")
            
            choice = input(f"\n{Colors.CYAN}Choose option (0-{len(WHISPER_MODELS)}): {Colors.RESET}").strip()
            if choice == "0":
                return False
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(WHISPER_MODELS):
                    self.selection.model = WHISPER_MODELS[idx][0]
                    self.selection.model_name = WHISPER_MODELS[idx][0]
                    logger.info(f"Selected model: {self.selection.model}")
                    return True
                else:
                    print(f"{Colors.RED}[✗] Invalid option{Colors.RESET}")
                    input("Press Enter...")
            except ValueError:
                print(f"{Colors.RED}[✗] Invalid input{Colors.RESET}")
                input("Press Enter...")
    
    def select_mode(self) -> bool:
        """Mode selection menu"""
        self.save_checkpoint("mode")
        while True:
            self.menu.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}MODE SELECTION{Colors.RESET}\n")
            for i, (name, key, desc) in enumerate(MODES, 1):
                print(f"  {Colors.GREEN}{i}{Colors.RESET}) {Colors.WHITE}{name}{Colors.RESET}")
                print(f"     {Colors.CYAN}└─ {desc}{Colors.RESET}")
            print(f"\n  {Colors.YELLOW}0{Colors.RESET}) {Colors.YELLOW}Back{Colors.RESET}")
            
            choice = input(f"\n{Colors.CYAN}Choose option (0-{len(MODES)}): {Colors.RESET}").strip()
            if choice == "0":
                return False
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(MODES):
                    self.selection.mode = MODES[idx][1]
                    self.selection.mode_name = MODES[idx][0]
                    logger.info(f"Selected mode: {self.selection.mode_name}")
                    return True
                else:
                    print(f"{Colors.RED}[✗] Invalid option{Colors.RESET}")
                    input("Press Enter...")
            except ValueError:
                print(f"{Colors.RED}[✗] Invalid input{Colors.RESET}")
                input("Press Enter...")
    
    def select_language(self) -> bool:
        """Language selection with tiers"""
        self.save_checkpoint("language")
        while True:
            self.menu.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}LANGUAGE SELECTION{Colors.RESET}\n")
            print(f"  {Colors.GREEN}1{Colors.RESET}) {Colors.WHITE}High Accuracy (90-95%){Colors.RESET}")
            print(f"     {Colors.CYAN}└─ Best for clean audio, professional content{Colors.RESET}")
            print(f"  {Colors.GREEN}2{Colors.RESET}) {Colors.WHITE}Medium Accuracy (70-85%){Colors.RESET}")
            print(f"     {Colors.CYAN}└─ Good for clear audio with some background noise{Colors.RESET}")
            print(f"  {Colors.GREEN}3{Colors.RESET}) {Colors.WHITE}Lower Accuracy (50-70%){Colors.RESET}")
            print(f"     {Colors.CYAN}└─ May have errors, best for short clips{Colors.RESET}")
            print(f"\n  {Colors.YELLOW}0{Colors.RESET}) {Colors.YELLOW}Back{Colors.RESET}")
            
            tier_choice = input(f"\n{Colors.CYAN}Choose tier (0-3): {Colors.RESET}").strip()
            if tier_choice == "0":
                return False
            elif tier_choice == "1":
                tier = "high"
            elif tier_choice == "2":
                tier = "medium"
            elif tier_choice == "3":
                tier = "low"
            else:
                print(f"{Colors.RED}[✗] Invalid choice{Colors.RESET}")
                input("Press Enter...")
                continue
            
            languages = LANGUAGE_TIERS[tier]["languages"]
            while True:
                self.menu.clear_screen()
                print(f"{Colors.CYAN}{Colors.BOLD}SELECT LANGUAGE{Colors.RESET}")
                print(f"{Colors.GREEN}Tier: {LANGUAGE_TIERS[tier]['name']}{Colors.RESET}")
                print(f"{Colors.CYAN}Description: {LANGUAGE_TIERS[tier]['description']}{Colors.RESET}\n")
                
                for i, (name, code, desc) in enumerate(languages, 1):
                    print(f"  {Colors.GREEN}{i}{Colors.RESET}) {Colors.WHITE}{name}{Colors.RESET}")
                    print(f"     {Colors.CYAN}└─ {desc}{Colors.RESET}")
                print(f"\n  {Colors.YELLOW}0{Colors.RESET}) {Colors.YELLOW}Back to tiers{Colors.RESET}")
                
                lang_choice = input(f"\n{Colors.CYAN}Choose language (0-{len(languages)}): {Colors.RESET}").strip()
                if lang_choice == "0":
                    break
                try:
                    idx = int(lang_choice) - 1
                    if 0 <= idx < len(languages):
                        self.selection.language_code = languages[idx][1]
                        self.selection.language_name = languages[idx][0]
                        logger.info(f"Selected language: {self.selection.language_name}")
                        return True
                    else:
                        print(f"{Colors.RED}[✗] Invalid option{Colors.RESET}")
                        input("Press Enter...")
                except ValueError:
                    print(f"{Colors.RED}[✗] Invalid input{Colors.RESET}")
                    input("Press Enter...")
    
    def select_line_break(self) -> bool:
        """Line break type selection"""
        self.save_checkpoint("line_break")
        while True:
            self.menu.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}LINE BREAK TYPE{Colors.RESET}\n")
            for i, (name, key, desc, range_text) in enumerate(LINE_TYPES, 1):
                print(f"  {Colors.GREEN}{i}{Colors.RESET}) {Colors.WHITE}{name}{Colors.RESET}")
                print(f"     {Colors.CYAN}└─ {desc}{Colors.RESET}")
                print(f"     {Colors.CYAN}   Range: {range_text}{Colors.RESET}")
            print(f"\n  {Colors.YELLOW}0{Colors.RESET}) {Colors.YELLOW}Back{Colors.RESET}")
            
            choice = input(f"\n{Colors.CYAN}Choose option (0-{len(LINE_TYPES)}): {Colors.RESET}").strip()
            if choice == "0":
                return False
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(LINE_TYPES):
                    self.selection.line_type = LINE_TYPES[idx][1]
                    self.selection.line_type_name = LINE_TYPES[idx][0]
                    
                    if self.selection.line_type == "words":
                        while True:
                            try:
                                val = input(f"{Colors.CYAN}Words per line (1-30): {Colors.RESET}").strip()
                                if val:
                                    limit = int(val)
                                    if 1 <= limit <= 30:
                                        self.selection.limit = limit
                                        break
                                    else:
                                        print(f"{Colors.RED}[✗] Please enter a number between 1 and 30{Colors.RESET}")
                                else:
                                    self.selection.limit = 5
                                    break
                            except ValueError:
                                print(f"{Colors.RED}[✗] Invalid input{Colors.RESET}")
                    elif self.selection.line_type == "letters":
                        while True:
                            try:
                                val = input(f"{Colors.CYAN}Letters per line (10-80): {Colors.RESET}").strip()
                                if val:
                                    limit = int(val)
                                    if 10 <= limit <= 80:
                                        self.selection.limit = limit
                                        break
                                    else:
                                        print(f"{Colors.RED}[✗] Please enter a number between 10 and 80{Colors.RESET}")
                                else:
                                    self.selection.limit = 42
                                    break
                            except ValueError:
                                print(f"{Colors.RED}[✗] Invalid input{Colors.RESET}")
                    else:
                        self.selection.limit = 0
                    
                    logger.info(f"Selected line break: {self.selection.line_type_name}, limit: {self.selection.limit}")
                    return True
                else:
                    print(f"{Colors.RED}[✗] Invalid option{Colors.RESET}")
                    input("Press Enter...")
            except ValueError:
                print(f"{Colors.RED}[✗] Invalid input{Colors.RESET}")
                input("Press Enter...")
    
    def download_youtube_audio(self, url: str) -> Tuple[Optional[Path], Optional[str]]:
        """Download audio from YouTube"""
        try:
            import yt_dlp
        except ImportError:
            logger.error("yt-dlp not available")
            print(f"{Colors.RED}[✗] yt-dlp not available{Colors.RESET}")
            return None, None
            
        logger.info(f"Downloading YouTube audio from: {url}")
        print(f"{Colors.CYAN}[i] Downloading audio from YouTube...{Colors.RESET}")
        
        temp_dir = Path(tempfile.gettempdir())
        output_template = str(temp_dir / "youtube_audio_%(id)s.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '16000',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', '')
                video_title_clean = re.sub(r'[<>:"/\\|?*]', '', str(video_title))[:50]
                logger.info(f"Downloaded: {video_title_clean}")
                
                for f in temp_dir.glob("youtube_audio_*"):
                    if f.suffix in ['.wav', '.mp3', '.m4a']:
                        if f.suffix != '.wav':
                            wav_path = f.with_suffix('.wav')
                            ffmpeg_cmd = ['ffmpeg', '-i', str(f), '-acodec', 'pcm_s16le', 
                                         '-ar', '16000', '-ac', '1', '-y', str(wav_path)]
                            subprocess.run(ffmpeg_cmd, capture_output=True)
                            f.unlink()
                            f = wav_path
                        return f, video_title_clean
        except Exception as e:
            logger.error(f"YouTube download failed: {e}")
            print(f"{Colors.RED}[✗] Download failed: {e}{Colors.RESET}")
        return None, None
    
    def process_file(self) -> bool:
        """Process the selected file and generate captions"""
        try:
            media_path = Path(self.selection.file_path)
            audio_path = media_path
            
            # Extract audio if needed
            if media_path.suffix.lower() in ['.mp4', '.avi', '.mkv', '.mov', '.mpg', '.mpeg', '.webm', '.flv', '.wmv']:
                logger.info(f"Extracting audio from video: {media_path}")
                audio_path = self.audio_processor.extract_audio(media_path, self.update_progress)
                if not audio_path:
                    logger.error("Could not extract audio")
                    print(f"{Colors.RED}[✗] Could not extract audio{Colors.RESET}")
                    return False
            
            # Vocal separation
            if self.selection.vocal_separation != "none":
                logger.info(f"Applying vocal separation: {self.selection.vocal_separation}")
                vocals_path = self.vocal_separator.separate(audio_path, self.selection.vocal_separation, self.update_progress)
                if vocals_path and vocals_path.exists():
                    audio_path = vocals_path
                    print(f"{Colors.GREEN}[✓] Using isolated vocals{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}[!] Vocal separation failed, using original audio{Colors.RESET}")
            
            # Load model
            if not self.transcriber.load_model(self.selection.model, self.update_progress):
                return False
            
            # Check cache
            file_hash = self.cache_manager.get_file_hash(media_path)
            cached_result = self.cache_manager.get_cached_transcription(
                file_hash, self.selection.model, self.selection.language_code, 
                self.selection.mode, self.selection.vocal_separation
            )
            
            if cached_result:
                logger.info("Using cached transcription")
                print(f"{Colors.GREEN}[✓] Using cached transcription{Colors.RESET}")
                result = cached_result
            else:
                # Transcribe
                result = self.transcriber.transcribe(audio_path, self.selection.language_code, self.selection.mode, self.update_progress)
                # Cache result
                self.cache_manager.cache_transcription(
                    file_hash, self.selection.model, self.selection.language_code,
                    self.selection.mode, self.selection.vocal_separation, result
                )
            
            # Generate subtitles
            segments = result.get("segments", [])
            if not segments:
                logger.error("No segments found in transcription result")
                print(f"{Colors.RED}[✗] No segments found in transcription result{Colors.RESET}")
                return False
            
            subtitles = self.subtitle_generator.generate_subtitles(segments, self.selection.line_type, self.selection.limit, self.update_progress)
            
            # Determine output path
            if self.selection.platform == "YouTube" and self.selection.video_title:
                suffix = f"{self.selection.language_code}" if self.selection.mode == "normal" else f"{self.selection.language_code}_translated"
                output_path = Path.cwd() / f"{self.selection.video_title}_{suffix}.srt"
            else:
                suffix = f"{self.selection.language_code}" if self.selection.mode == "normal" else f"{self.selection.language_code}_translated"
                output_path = media_path.parent / f"{media_path.stem}_{suffix}.srt"
            
            # Save subtitles
            self.subtitle_generator.save_srt(output_path, subtitles)
            
            self.update_progress(100, "Complete!")
            logger.info(f"Captions saved to: {output_path}")
            print(f"\n{Colors.GREEN}[✓] Saved to: {output_path}{Colors.RESET}")
            print(f"{Colors.CYAN}[i] Generated {len(subtitles)} subtitle entries{Colors.RESET}")
            
            # Cleanup
            if audio_path != media_path and audio_path and audio_path.exists():
                try:
                    audio_path.unlink()
                except:
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            print(f"{Colors.RED}[✗] Error: {e}{Colors.RESET}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """Main application loop"""
        # Check requirements
        if not self.audio_processor.check_ffmpeg():
            logger.warning("FFmpeg not found")
            print(f"{Colors.YELLOW}[!] FFmpeg not found. Some features may not work.{Colors.RESET}")
        if not WHISPER_AVAILABLE:
            logger.error("Whisper not available")
            print(f"{Colors.RED}[✗] Whisper not available!{Colors.RESET}")
            print(f"{Colors.CYAN}[i] Please ensure packages are installed in _pythonPackages_ folder{Colors.RESET}")
            input("\nPress Enter to exit...")
            return
        
        # Display status
        print(f"{Colors.GREEN}[✓] Whisper: Available{Colors.RESET}")
        if SPLEETER_AVAILABLE:
            print(f"{Colors.GREEN}[✓] Spleeter: Available (with TensorFlow){Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!] Spleeter: Not available (using FFmpeg fallback){Colors.RESET}")
        
        # Check for Send To file
        if self.media_path_arg:
            media_path = Path(self.media_path_arg)
            if media_path.exists() and media_path.suffix.lower() in SUPPORTED_EXTENSIONS['all']:
                logger.info(f"File received from Send To: {media_path}")
                self.selection.platform = "Local File"
                self.selection.source = "Send To"
                self.selection.file_path = str(media_path)
                
                # Show selection menu and process directly
                self.menu = None  # No menu needed for Send To
                if self.select_vocal_separation() and self.select_model() and self.select_mode() and self.select_language() and self.select_line_break():
                    self.print_selection_summary()
                    confirm = input(f"{Colors.CYAN}Generate captions? (y/n): {Colors.RESET}").lower()
                    if confirm in ['y', 'yes']:
                        print()
                        success = self.process_file()
                        if not success:
                            print(f"{Colors.RED}[✗] Failed to generate captions{Colors.RESET}")
                    else:
                        print(f"{Colors.YELLOW}[!] Cancelled by user{Colors.RESET}")
                return
        
        # Create main menu
        main_menu = Menu("Main Menu")
        
        # YouTube menu
        youtube_menu = Menu("YouTube Download", main_menu)
        
        def youtube_action():
            self.menu = youtube_menu
            while True:
                self.menu.clear_screen()
                print(f"{Colors.CYAN}{Colors.BOLD}YOUTUBE DOWNLOAD{Colors.RESET}\n")
                print(f"{Colors.YELLOW}Supported: YouTube.com, youtu.be, and other YouTube URLs{Colors.RESET}\n")
                url = input(f"{Colors.CYAN}Enter YouTube URL: {Colors.RESET}").strip()
                if not url:
                    return
                
                print(f"{Colors.CYAN}[i] Processing URL...{Colors.RESET}")
                media_path, video_title = self.download_youtube_audio(url)
                if not media_path:
                    print(f"{Colors.RED}[✗] Failed to download{Colors.RESET}")
                    input("Press Enter to try again...")
                    continue
                
                self.selection.platform = "YouTube"
                self.selection.source = url
                self.selection.file_path = str(media_path)
                self.selection.video_title = video_title
                
                if self.select_vocal_separation() and self.select_model() and self.select_mode() and self.select_language() and self.select_line_break():
                    self.print_selection_summary()
                    confirm = input(f"{Colors.CYAN}Generate captions? (y/n): {Colors.RESET}").lower()
                    if confirm in ['y', 'yes']:
                        print()
                        success = self.process_file()
                        if not success:
                            print(f"{Colors.RED}[✗] Failed to generate captions{Colors.RESET}")
                            retry = input(f"{Colors.CYAN}Try again? (y/n): {Colors.RESET}").lower()
                            if retry in ['y', 'yes']:
                                continue
                    else:
                        print(f"{Colors.YELLOW}[!] Cancelled by user{Colors.RESET}")
                return
        
        youtube_menu.add("1", "Download from URL", "Paste YouTube URL to download and transcribe", action=youtube_action)
        
        # Local file menu
        local_menu = Menu("Local File", main_menu)
        
        def local_file_action():
            self.menu = local_menu
            from tkinter import filedialog, Tk
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(
                title="Select Video/Audio File",
                filetypes=[
                    ("All Supported Files", "*.mp4;*.avi;*.mkv;*.mov;*.mp3;*.wav;*.m4a;*.flac"),
                    ("Video Files", "*.mp4;*.avi;*.mkv;*.mov;*.m4v;*.mpg;*.mpeg;*.webm"),
                    ("Audio Files", "*.mp3;*.wav;*.m4a;*.flac;*.ogg;*.aac"),
                    ("All Files", "*.*")
                ]
            )
            root.destroy()
            
            if not file_path:
                return
            
            media_path = Path(file_path)
            if not media_path.exists():
                print(f"{Colors.RED}[✗] File not found{Colors.RESET}")
                input("Press Enter...")
                return
            
            if media_path.suffix.lower() not in SUPPORTED_EXTENSIONS['all']:
                print(f"{Colors.RED}[✗] Unsupported file format{Colors.RESET}")
                print(f"{Colors.CYAN}[i] Supported formats: {', '.join(SUPPORTED_EXTENSIONS['all'])}{Colors.RESET}")
                input("Press Enter...")
                return
            
            self.selection.platform = "Local File"
            self.selection.source = "File Dialog"
            self.selection.file_path = str(media_path)
            
            if self.select_vocal_separation() and self.select_model() and self.select_mode() and self.select_language() and self.select_line_break():
                self.print_selection_summary()
                confirm = input(f"{Colors.CYAN}Generate captions? (y/n): {Colors.RESET}").lower()
                if confirm in ['y', 'yes']:
                    print()
                    success = self.process_file()
                    if not success:
                        print(f"{Colors.RED}[✗] Failed to generate captions{Colors.RESET}")
                        retry = input(f"{Colors.CYAN}Try again? (y/n): {Colors.RESET}").lower()
                        if retry in ['y', 'yes']:
                            local_file_action()
                else:
                    print(f"{Colors.YELLOW}[!] Cancelled by user{Colors.RESET}")
        
        local_menu.add("1", "Select File", "Browse and select video/audio file", action=local_file_action)
        
        # About function
        def about_action():
            self.menu.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}")
            print("+" + "=" * 60 + "+")
            print("|" + f"{APP_NAME} v{APP_VERSION}".center(60) + "|")
            print("|" + f"Author: {APP_AUTHOR}".center(60) + "|")
            print("|" + f"License: {APP_LICENSE}".center(60) + "|")
            print("+" + "=" * 60 + "+")
            print(f"{Colors.RESET}")
            print(f"\n{Colors.CYAN}Description:{Colors.RESET}")
            print("  Professional AI-powered subtitle generator using OpenAI Whisper")
            print(f"\n{Colors.CYAN}Features:{Colors.RESET}")
            print("  • YouTube video download and captioning")
            print("  • Local video/audio file processing")
            print("  • Vocal separation with Spleeter & TensorFlow")
            print("  • 20+ languages with accuracy tiers")
            print("  • Smart subtitle formatting (Auto/Words/Letters)")
            print("  • Caching for faster reprocessing")
            print(f"\n{Colors.CYAN}Components:{Colors.RESET}")
            print(f"  • Whisper: {'Available' if WHISPER_AVAILABLE else 'Not Available'}")
            print(f"  • Spleeter: {'Available' if SPLEETER_AVAILABLE else 'Not Available'}")
            print(f"  • TensorFlow: {'Available' if TENSORFLOW_AVAILABLE else 'Not Available'}")
            print(f"  • FFmpeg: {'Available' if self.audio_processor.check_ffmpeg() else 'Not Available'}")
            print(f"\n{Colors.CYAN}Support:{Colors.RESET}")
            print(f"  Telegram: {APP_TELEGRAM}")
            print(f"  YouTube: {APP_YOUTUBE}")
            print(f"  Logs: {APP_LOGS_FOLDER}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
        # Build main menu
        main_menu.add("1", "🌐 YouTube Mode", "Download video from YouTube and generate captions", submenu=youtube_menu)
        main_menu.add("2", "📁 Local File Mode", "Process existing video/audio file from your computer", submenu=local_menu)
        main_menu.add("3", "ℹ️ About", "Show application information and component status", action=about_action)
        
        # Run menu
        result = main_menu.show()
        
        # Cleanup
        print(f"\n{Colors.GREEN}[✓] Thanks for using {APP_NAME}!{Colors.RESET}")
        logger.info("Application shutting down")
        self.cleanup()
        time.sleep(2)

# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'{APP_NAME} - {APP_AUTHOR}')
    parser.add_argument('file', nargs='?', help='Video/Audio file to process (supports Send To)')
    args = parser.parse_args()
    
    app = NotYCaptionGenerator(args.file)
    app.run()