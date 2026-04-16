#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NotY Caption Generator AI v6.1
Using OpenAI Whisper (PyTorch) with YouTube Support & Smart Lyrics Matching
Professional Vocal Separation with Spleeter
Copyright (c) 2026 NotY215
"""

# CRITICAL: These imports must be at the top for frozen apps
import os
import sys
import atexit
import glob

# Fix for PyInstaller packaged app
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.environ['PATH'] = application_path + os.pathsep + os.environ.get('PATH', '')
    if application_path not in sys.path:
        sys.path.insert(0, application_path)
    os.environ['TORCH_USE_RTLD_GLOBAL'] = '1'
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    os.environ['OMP_NUM_THREADS'] = '4'
    torch_path = os.path.join(application_path, 'torch')
    if os.path.exists(torch_path):
        sys.path.insert(0, torch_path)

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

# Mock torch.cuda before importing torch
class _MockCuda:
    def __init__(self):
        self.is_available = lambda: False
        self.device_count = lambda: 0
        self.current_device = lambda: -1
        self.is_initialized = lambda: False
        self.is_bf16_supported = lambda: False
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

class _MockCudaStream:
    def __init__(self):
        pass

class _MockTorchCuda:
    def __init__(self):
        self.is_available = lambda: False
        self.device_count = lambda: 0
        self.current_device = lambda: -1
        self.is_initialized = lambda: False
        self.is_bf16_supported = lambda: False
        self.Stream = _MockCudaStream
        self.Event = lambda *args, **kwargs: None
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

# Import torch with fallback
try:
    import torch
    if not hasattr(torch, 'cuda') or torch.cuda.is_available() is None:
        torch.cuda = _MockTorchCuda()
    elif torch.cuda.is_available():
        # Set to CPU only for compatibility
        torch.cuda.is_available = lambda: False
except ImportError:
    class _MockTorch:
        cuda = _MockTorchCuda()
        class nn:
            Module = object
        class optim:
            Adam = None
        class utils:
            data = None
        def __getattr__(self, name):
            return None
    torch = _MockTorch()
    sys.modules['torch'] = torch

# Now import other dependencies
import webbrowser
import time
import platform
import argparse
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any, Union
from datetime import timedelta
import re
import json
import urllib.request
import urllib.parse
import tempfile
import shutil
import hashlib
import sqlite3
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# Try to import whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError as e:
    WHISPER_AVAILABLE = False
    whisper = None

# Try to import yt-dlp
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    yt_dlp = None

# Try to import spleeter for vocal separation
SPLEETER_AVAILABLE = False
try:
    from spleeter.separator import Separator
    from spleeter.audio.adapter import AudioAdapter
    SPLEETER_AVAILABLE = True
except ImportError as e:
    pass

# Try to import tensorflow with fallback
try:
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'

if platform.system() == "Windows":
    try:
        import colorama
        colorama.init()
    except:
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')

def cleanup_temp_files():
    """Clean up temporary audio files only - NOT cache"""
    try:
        temp_dir = Path(tempfile.gettempdir())
        patterns = ["*_temp_audio.wav", "*_vocals.wav", "*_accompaniment.wav", 
                   "youtube_audio_*", "spleeter_*", "*_temp_audio.mp3"]
        for pattern in patterns:
            for file in temp_dir.glob(pattern):
                try:
                    if file.is_file():
                        file.unlink()
                except:
                    pass
    except:
        pass

def select_file_dialog():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_types = [
            ("All Supported Files", "*.mp4;*.avi;*.mkv;*.mov;*.m4v;*.mpg;*.mpeg;*.webm;*.mp3;*.wav;*.m4a;*.flac"),
            ("Video Files", "*.mp4;*.avi;*.mkv;*.mov;*.m4v;*.mpg;*.mpeg;*.webm"),
            ("Audio Files", "*.mp3;*.wav;*.m4a;*.flac"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(title="Select Video/Audio File", filetypes=file_types)
        root.destroy()
        return file_path
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Could not open file dialog: {e}{Colors.RESET}")
        return None

def save_file_dialog(default_name: str) -> str:
    """Show save dialog for YouTube mode only"""
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = filedialog.asksaveasfilename(
            title="Save Subtitle File",
            defaultextension=".srt",
            filetypes=[("SubRip Subtitle", "*.srt"), ("All Files", "*.*")],
            initialfile=default_name
        )
        root.destroy()
        return file_path
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Could not open save dialog: {e}{Colors.RESET}")
        return None

def show_message_box(title: str, message: str, icon: str = 'info'):
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        if icon == 'info':
            messagebox.showinfo(title, message)
        elif icon == 'warning':
            messagebox.showwarning(title, message)
        elif icon == 'error':
            messagebox.showerror(title, message)
        root.destroy()
    except:
        pass

def print_header(title: str = None):
    if title is None:
        title = f"{APP_NAME} v{APP_VERSION}"
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("+" + "=" * 58 + "+")
    print("|" + title.center(58) + "|")
    print("|" + f"Copyright (c) {APP_YEAR} {APP_AUTHOR}".center(58) + "|")
    print("|" + f"License: {APP_LICENSE}".center(58) + "|")
    print("|" + "Powered by OpenAI Whisper + Spleeter".center(58) + "|")
    print("+" + "=" * 58 + "+")
    print(f"{Colors.RESET}")

# Application metadata
APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "6.1"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"
APP_LICENSE = "LGPL-3.0"
APP_TELEGRAM = "https://t.me/Noty_215"
APP_YOUTUBE = "https://www.youtube.com/@NotY215"

# Language codes
class Language(Enum):
    ENGLISH = ("en", "English")
    HINDI = ("hi", "Hindi")
    JAPANESE = ("ja", "Japanese")
    SPANISH = ("es", "Spanish")
    KOREAN = ("ko", "Korean")
    CHINESE = ("zh", "Chinese (Mandarin)")
    RUSSIAN = ("ru", "Russian")
    AUTO = ("auto", "Auto Detect")

# Whisper models
WHISPER_MODELS = {
    "tiny": {"size": "75 MB", "desc": "Fastest", "speed": 0.5},
    "base": {"size": "150 MB", "desc": "Balanced", "speed": 1.0},
    "small": {"size": "500 MB", "desc": "Good", "speed": 2.0},
    "medium": {"size": "1.5 GB", "desc": "Accurate", "speed": 4.0},
    "large": {"size": "2.9 GB", "desc": "Best", "speed": 8.0}
}

# Spleeter models for vocal separation
SPLEETER_MODELS = {
    "2stems": "Vocals + Accompaniment (Fastest)",
    "4stems": "Vocals + Drums + Bass + Other (Better)",
    "5stems": "Vocals + Drums + Bass + Piano + Other (Best)"
}

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm'],
    'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'],
    'all': ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm', 
            '.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']
}

@dataclass
class SubtitleEntry:
    index: int
    start: timedelta
    end: timedelta
    text: str
    
    def to_srt(self) -> str:
        start_str = f"{self.start.total_seconds():02d}:{int(self.start.total_seconds() % 60):02d}:{int(self.start.total_seconds() * 1000 % 1000):03d}"
        end_str = f"{self.end.total_seconds():02d}:{int(self.end.total_seconds() % 60):02d}:{int(self.end.total_seconds() * 1000 % 1000):03d}"
        # Proper SRT time format: HH:MM:SS,mmm
        start_hours = int(self.start.total_seconds() // 3600)
        start_minutes = int((self.start.total_seconds() % 3600) // 60)
        start_seconds = int(self.start.total_seconds() % 60)
        start_millis = int((self.start.total_seconds() % 1) * 1000)
        
        end_hours = int(self.end.total_seconds() // 3600)
        end_minutes = int((self.end.total_seconds() % 3600) // 60)
        end_seconds = int(self.end.total_seconds() % 60)
        end_millis = int((self.end.total_seconds() % 1) * 1000)
        
        return f"{self.index}\n{start_hours:02d}:{start_minutes:02d}:{start_seconds:02d},{start_millis:03d} --> {end_hours:02d}:{end_minutes:02d}:{end_seconds:02d},{end_millis:03d}\n{self.text}\n"

@dataclass
class ProcessingStats:
    start_time: float = 0
    end_time: float = 0
    audio_duration: float = 0
    transcription_time: float = 0
    separation_time: float = 0
    total_segments: int = 0
    model_used: str = ""
    vocal_separation_used: bool = False
    
    @property
    def total_time(self) -> float:
        return self.end_time - self.start_time
    
    def display(self):
        print(f"\n{Colors.CYAN}{'='*50}")
        print("PROCESSING STATISTICS")
        print(f"{'='*50}{Colors.RESET}")
        print(f"  Model: {self.model_used}")
        print(f"  Vocal Separation: {'Yes' if self.vocal_separation_used else 'No'}")
        print(f"  Audio Duration: {self.audio_duration:.2f} seconds")
        print(f"  Transcription Time: {self.transcription_time:.2f} seconds")
        if self.separation_time > 0:
            print(f"  Separation Time: {self.separation_time:.2f} seconds")
        print(f"  Total Segments: {self.total_segments}")
        print(f"  Total Processing Time: {self.total_time:.2f} seconds")
        if self.audio_duration > 0 and self.total_time > 0:
            ratio = self.audio_duration / self.total_time
            print(f"  Speed: {ratio:.2f}x realtime")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")

class NotYCaptionGenerator:
    def __init__(self, media_path: str = None):
        atexit.register(cleanup_temp_files)
        
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
            
        self.models_dir = self.base_dir / "models"
        self.ffmpeg_dir = self.base_dir / "ffmpeg"
        self.cache_dir = self.base_dir / "cache"
        self.pretrained_models_dir = self.base_dir / "pretrained_models"
        
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if platform.system() == "Windows":
            self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg.exe"
            self.ffprobe_exe = self.ffmpeg_dir / "ffprobe.exe"
        else:
            self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg"
            self.ffprobe_exe = self.ffmpeg_dir / "ffprobe"
        
        if self.ffmpeg_dir.exists():
            os.environ['PATH'] = str(self.ffmpeg_dir) + os.pathsep + os.environ.get('PATH', '')
        
        self.init_database()
        
        self.languages = [
            (Language.ENGLISH.value[1], Language.ENGLISH.value[0]),
            (Language.HINDI.value[1], Language.HINDI.value[0]),
            (Language.JAPANESE.value[1], Language.JAPANESE.value[0]),
            (Language.SPANISH.value[1], Language.SPANISH.value[0]),
            (Language.KOREAN.value[1], Language.KOREAN.value[0]),
            (Language.CHINESE.value[1], Language.CHINESE.value[0]),
            (Language.RUSSIAN.value[1], Language.RUSSIAN.value[0]),
            (Language.AUTO.value[1], Language.AUTO.value[0])
        ]
        
        self.models = [
            ("tiny", WHISPER_MODELS["tiny"]["size"], WHISPER_MODELS["tiny"]["desc"]),
            ("base", WHISPER_MODELS["base"]["size"], WHISPER_MODELS["base"]["desc"]),
            ("small", WHISPER_MODELS["small"]["size"], WHISPER_MODELS["small"]["desc"]),
            ("medium", WHISPER_MODELS["medium"]["size"], WHISPER_MODELS["medium"]["desc"]),
            ("large", WHISPER_MODELS["large"]["size"], WHISPER_MODELS["large"]["desc"])
        ]
        
        self.modes = [
            ("Normal Mode", "normal", "Standard transcription in selected language"),
            ("Translate Mode", "translate", "Translate to English while transcribing")
        ]
        
        self.line_types = [
            ("Words", "words", "Break by word count (1-30 words)"),
            ("Letters", "letters", "Break by character limit (1-50 chars)"),
            ("Auto", "auto", "Smart sentence detection with natural breaks")
        ]
        
        self.vocal_quality_options = [
            ("No vocal separation", "none", "Fastest - use original audio"),
            ("2 Stems (Fast)", "2stems", "Vocals + Accompaniment - Good quality"),
            ("4 Stems (Better)", "4stems", "Vocals + Drums + Bass + Other - Better quality"),
            ("5 Stems (Best)", "5stems", "Vocals + Drums + Bass + Piano + Other - Best quality")
        ]
        
        self.use_vocal_separation = False
        self.spleeter_model = "2stems"
        self.separator = None
        
        self.selected_model = None
        self.selected_language = None
        self.selected_mode = None
        self.selected_line_type = None
        self.selected_vocal_quality = None
        self.media_path_arg = media_path
        self.model = None
        self.is_sendto = media_path is not None
        
        # Menu state for back button
        self.menu_stack = []
        self.current_menu = "main"
        self.temp_data = {}
        
        # Processing stats
        self.stats = ProcessingStats()
        
        # Check for local Spleeter models
        self.has_local_spleeter_models = self.check_spleeter_models()
        
    def check_spleeter_models(self) -> bool:
        """Check if Spleeter pretrained models exist locally"""
        if self.pretrained_models_dir.exists():
            for model in ['2stems', '4stems', '5stems']:
                model_dir = self.pretrained_models_dir / model
                if model_dir.exists() and any(model_dir.iterdir()):
                    return True
        return False
        
    def get_spleeter_model_path(self) -> Optional[Path]:
        """Get the path to Spleeter pretrained models"""
        if self.pretrained_models_dir.exists() and any(self.pretrained_models_dir.iterdir()):
            return self.pretrained_models_dir
        return None
        
    def init_database(self):
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
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lyrics_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_name TEXT UNIQUE,
                lyrics TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def get_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def cache_transcription(self, file_hash: str, model_name: str, language: str, mode: str, vocal_separation: str, result: dict):
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO transcriptions (file_hash, model_name, language, mode, vocal_separation, result) VALUES (?, ?, ?, ?, ?, ?)",
                (file_hash, model_name, language, mode, vocal_separation, json.dumps(result))
            )
            self.conn.commit()
        except Exception as e:
            pass
            
    def get_cached_transcription(self, file_hash: str, model_name: str, language: str, mode: str, vocal_separation: str) -> Optional[dict]:
        try:
            self.cursor.execute(
                "SELECT result FROM transcriptions WHERE file_hash = ? AND model_name = ? AND language = ? AND mode = ? AND vocal_separation = ?",
                (file_hash, model_name, language, mode, vocal_separation)
            )
            row = self.cursor.fetchone()
            if row:
                return json.loads(row[0])
        except:
            pass
        return None
        
    def save_setting(self, key: str, value: str):
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            self.conn.commit()
        except:
            pass
            
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        try:
            self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = self.cursor.fetchone()
            if row:
                return row[0]
        except:
            pass
        return default
        
    def clear_screen(self):
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
    def print_success(self, message: str):
        print(f"{Colors.GREEN}[✓] {message}{Colors.RESET}")
        
    def print_error(self, message: str):
        print(f"{Colors.RED}[✗] {message}{Colors.RESET}")
        
    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}[!] {message}{Colors.RESET}")
        
    def print_info(self, message: str):
        print(f"{Colors.CYAN}[i] {message}{Colors.RESET}")
        
    def print_progress(self, message: str, percent: int = None):
        if percent is not None:
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r{Colors.CYAN}[{bar}] {percent}% - {message}{Colors.RESET}", end="", flush=True)
            if percent == 100:
                print()
        else:
            print(f"{Colors.CYAN}[→] {message}{Colors.RESET}")
        
    def print_box(self, lines: List[str]):
        width = max(len(line) for line in lines) + 4
        print(f"{Colors.GREEN}")
        print("┌" + "─" * (width - 2) + "┐")
        for line in lines:
            print(f"│ {line.ljust(width - 4)} │")
        print("└" + "─" * (width - 2) + "┘")
        print(f"{Colors.RESET}")
        
    def print_table(self, headers: List[str], rows: List[List[str]]):
        if not rows:
            return
            
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        total_width = sum(col_widths) + len(headers) * 3 + 1
        
        print(f"{Colors.CYAN}")
        print("┌" + "─" * (total_width - 2) + "┐")
        
        header_line = "│ "
        for i, header in enumerate(headers):
            header_line += header.ljust(col_widths[i]) + " │ "
        print(header_line[:-2])
        
        print("├" + "─" * (total_width - 2) + "┤")
        
        for row in rows:
            row_line = "│ "
            for i, cell in enumerate(row):
                row_line += str(cell).ljust(col_widths[i]) + " │ "
            print(row_line[:-2])
        
        print("└" + "─" * (total_width - 2) + "┘")
        print(f"{Colors.RESET}")
        
    def get_input(self, prompt: str, default: str = None) -> str:
        try:
            if default:
                print(f"{Colors.CYAN}{prompt} [{default}]: {Colors.RESET}", end="", flush=True)
                value = sys.stdin.readline().strip()
                return value if value else default
            else:
                print(f"{Colors.CYAN}{prompt}{Colors.RESET}", end="", flush=True)
                return sys.stdin.readline().strip()
        except Exception as e:
            self.print_error(f"Input error: {e}")
            return ""
            
    def get_number_input(self, prompt: str, min_val: int, max_val: int) -> int:
        while True:
            value = self.get_input(prompt)
            if value == "":
                continue
            try:
                num = int(value)
                if min_val <= num <= max_val:
                    return num
                self.print_error(f"Please enter a number between {min_val} and {max_val}")
            except ValueError:
                self.print_error("Invalid input! Please enter a number.")
                
    def confirm(self, prompt: str) -> bool:
        while True:
            response = self.get_input(f"{prompt} (y/n): ").lower()
            if response in ['y', 'yes', 'ye', 'yep', 'ok']:
                return True
            elif response in ['n', 'no', 'nope', 'cancel']:
                return False
            self.print_error("Please enter y or n")
            
    def show_menu(self, title: str, options: List[str], menu_id: str = None) -> int:
        """Show menu and return selected index. Returns -1 for back/exit."""
        if menu_id:
            if self.current_menu != menu_id:
                self.menu_stack.append(self.current_menu)
                self.current_menu = menu_id
        
        while True:
            print(f"\n{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
            print(f"{Colors.CYAN}┌{'─' * 50}┐{Colors.RESET}")
            for i, option in enumerate(options, 1):
                print(f"{Colors.CYAN}│{Colors.RESET} {i:2}) {option:<45} {Colors.CYAN}│{Colors.RESET}")
            print(f"{Colors.CYAN}│{Colors.RESET}  0) Back{' ' * 45}{Colors.CYAN}│{Colors.RESET}")
            print(f"{Colors.CYAN}└{'─' * 50}┘{Colors.RESET}")
            
            choice = self.get_number_input(f"Choose option (0-{len(options)}): ", 0, len(options))
            if choice == 0:
                if self.menu_stack:
                    self.current_menu = self.menu_stack.pop()
                return -1
            return choice - 1
            
    def get_youtube_url(self) -> Optional[str]:
        print(f"\n{Colors.CYAN}Paste YouTube URL:{Colors.RESET}")
        print(f"   Examples:")
        print(f"   - https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print(f"   - https://youtu.be/dQw4w9WgXcQ")
        print(f"   - https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120")
        url = self.get_input("\n> ").strip()
        if not url:
            self.print_error("URL cannot be empty!")
            return None
        return url
        
    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([\w-]+)',
            r'(?:youtu\.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)',
            r'(?:youtube\.com\/v\/)([\w-]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
        
    def download_youtube_audio(self, url: str) -> Tuple[Optional[Path], Optional[str]]:
        if not YTDLP_AVAILABLE:
            self.print_error("yt-dlp not available. Please install: pip install yt-dlp")
            return None, None
            
        self.print_info("Downloading audio from YouTube...")
        
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
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', '')
                video_duration = info.get('duration', 0)
                video_uploader = info.get('uploader', '')
                
                video_title_clean = re.sub(r'[<>:"/\\|?*]', '', video_title)[:50]
                self.print_info(f"Video: {video_title}")
                self.print_info(f"Channel: {video_uploader}")
                if video_duration:
                    minutes = video_duration // 60
                    seconds = video_duration % 60
                    self.print_info(f"Duration: {minutes}:{seconds:02d}")
                
                for f in temp_dir.glob("youtube_audio_*"):
                    if f.suffix in ['.wav', '.mp3', '.m4a']:
                        if f.suffix != '.wav':
                            wav_path = f.with_suffix('.wav')
                            if self.check_ffmpeg():
                                ffmpeg_cmd = [str(self.ffmpeg_exe) if self.ffmpeg_exe.exists() else 'ffmpeg',
                                              '-i', str(f), '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-y', str(wav_path)]
                                subprocess.run(ffmpeg_cmd, capture_output=True)
                                f.unlink()
                                f = wav_path
                        self.print_success("Download complete!")
                        return f, video_title_clean
        except Exception as e:
            self.print_error(f"Download failed: {e}")
        return None, None
        
    def check_ffmpeg(self) -> bool:
        if self.ffmpeg_exe.exists():
            return True
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            pass
        return False
        
    def get_audio_duration(self, audio_path: Path) -> float:
        if not self.check_ffmpeg():
            return 0
            
        ffprobe_cmd = str(self.ffprobe_exe) if self.ffprobe_exe.exists() else 'ffprobe'
        cmd = [
            ffprobe_cmd, '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return 0
            
    def extract_audio(self, video_path: Path) -> Path:
        if not self.check_ffmpeg():
            self.print_error("FFmpeg not found!")
            return None
            
        temp_dir = Path(tempfile.gettempdir())
        audio_path = temp_dir / f"{video_path.stem}_temp_audio.wav"
        
        self.print_progress("Extracting audio...", 10)
        
        ffmpeg_cmd = str(self.ffmpeg_exe) if self.ffmpeg_exe.exists() else 'ffmpeg'
        
        cmd = [
            ffmpeg_cmd, '-i', str(video_path),
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',
            str(audio_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=120)
            if audio_path.exists() and audio_path.stat().st_size > 0:
                duration = self.get_audio_duration(audio_path)
                self.stats.audio_duration = duration
                self.print_progress(f"Audio extracted ({duration:.1f}s)", 20)
                return audio_path
        except subprocess.TimeoutExpired:
            self.print_error("Audio extraction timed out")
        except Exception as e:
            self.print_error(f"Audio extraction failed: {e}")
        return None
        
    def separate_vocals_spleeter(self, audio_path: Path) -> Optional[Path]:
        """Separate vocals using Spleeter - High quality vocal isolation"""
        if not SPLEETER_AVAILABLE:
            self.print_warning("Spleeter not available. Install: pip install spleeter")
            return None
            
        sep_start = time.time()
        self.print_progress(f"Separating vocals with Spleeter ({self.spleeter_model})...", 30)
        
        temp_dir = Path(tempfile.gettempdir())
        output_dir = temp_dir / f"spleeter_output_{int(time.time())}"
        
        try:
            # Set Spleeter model path environment variable if local models exist
            model_path = self.get_spleeter_model_path()
            if model_path:
                os.environ['SPLEETER_PRETRAINED_PATH'] = str(model_path)
                self.print_info(f"Using local Spleeter models from: {model_path}")
            else:
                self.print_info("Downloading Spleeter model (first time only)...")
            
            # Initialize Spleeter separator
            if self.separator is None:
                self.print_info(f"Loading Spleeter model: {self.spleeter_model}")
                self.separator = Separator(f'spleeter:{self.spleeter_model}')
            
            # Perform separation
            self.print_info("Separating audio tracks (this may take a while)...")
            self.separator.separate_to_file(
                str(audio_path),
                str(output_dir),
                filename_format="{filename}_{instrument}.{codec}",
                codec='wav'
            )
            
            # Find the vocal file
            vocal_file = None
            for file in output_dir.rglob("*vocals.wav"):
                vocal_file = file
                break
            
            if vocal_file and vocal_file.exists():
                # Copy to temp directory
                final_vocals = temp_dir / f"{audio_path.stem}_vocals.wav"
                shutil.copy2(vocal_file, final_vocals)
                
                # Cleanup
                shutil.rmtree(output_dir, ignore_errors=True)
                
                self.stats.separation_time = time.time() - sep_start
                self.print_progress("Vocal separation complete", 40)
                return final_vocals
            else:
                self.print_warning("Could not find vocal track in output")
                return None
                
        except Exception as e:
            self.print_warning(f"Spleeter error: {e}")
            return None
            
    def separate_vocals_ffmpeg(self, audio_path: Path) -> Optional[Path]:
        """Fallback vocal separation using FFmpeg"""
        self.print_progress("Isolating vocals with FFmpeg...", 35)
        
        temp_dir = Path(tempfile.gettempdir())
        vocal_path = temp_dir / f"{audio_path.stem}_vocals.wav"
        
        ffmpeg_cmd = str(self.ffmpeg_exe) if self.ffmpeg_exe.exists() else 'ffmpeg'
        
        # Use highpass and lowpass filters to isolate vocal range (80Hz - 12kHz)
        cmd = [
            ffmpeg_cmd, '-i', str(audio_path),
            '-af', 'highpass=f=80, lowpass=f=12000, volume=2.0',
            '-y',
            str(vocal_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=180)
            if vocal_path.exists() and vocal_path.stat().st_size > 0:
                self.print_progress("Vocal isolation complete", 40)
                return vocal_path
        except Exception as e:
            self.print_warning(f"FFmpeg vocal isolation failed: {e}")
        
        return None
        
    def load_model(self, model_name: str):
        if not WHISPER_AVAILABLE:
            self.print_error("Whisper not available!")
            return False
            
        try:
            self.print_progress(f"Loading {model_name} model...", 60)
            load_start = time.time()
            self.model = whisper.load_model(model_name, download_root=str(self.models_dir))
            load_time = time.time() - load_start
            self.print_success(f"Model loaded in {load_time:.1f}s")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False
            
    def format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def limit_letters_per_line(self, text: str, max_letters: int) -> str:
        if max_letters <= 0 or len(text) <= max_letters:
            return text
        lines = []
        current_line = ""
        current_length = 0
        for word in text.split():
            word_len = len(word)
            if current_length + word_len + (1 if current_line else 0) > max_letters:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                    current_length = word_len
                else:
                    lines.append(word)
                    current_line = ""
                    current_length = 0
            else:
                if current_line:
                    current_line += " " + word
                    current_length += word_len + 1
                else:
                    current_line = word
                    current_length = word_len
        if current_line:
            lines.append(current_line)
        return '\n'.join(lines)
        
    def smart_split_subtitle(self, text: str, max_chars: int = 42) -> List[str]:
        """Smart subtitle splitting for better readability"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_len = len(word)
            if current_length + word_len + (1 if current_line else 0) <= max_chars:
                current_line.append(word)
                current_length += word_len + (1 if current_line else 0)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_len
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
        
    def auto_break_sentences(self, segments) -> List[SubtitleEntry]:
        """Smart sentence breaking with natural language processing"""
        subtitles = []
        index = 1
        min_gap = 0.3
        max_duration = 3.0
        
        i = 0
        while i < len(segments):
            segment = segments[i]
            text = segment["text"].strip()
            if not text:
                i += 1
                continue
                
            start_time = segment["start"]
            end_time = segment["end"]
            duration = end_time - start_time
            
            natural_breaks = ['.', '!', '?', ';', ':', ',', '。', '！', '？', '；', '：', '，']
            has_natural_break = any(text.rstrip().endswith(p) for p in natural_breaks)
            
            if has_natural_break or duration <= max_duration:
                if len(text) > 42:
                    lines = self.smart_split_subtitle(text)
                    line_duration = duration / len(lines)
                    for idx, line in enumerate(lines):
                        line_start = start_time + (idx * line_duration)
                        line_end = line_start + line_duration
                        subtitles.append(SubtitleEntry(
                            index=index,
                            start=timedelta(seconds=line_start),
                            end=timedelta(seconds=line_end),
                            text=line
                        ))
                        index += 1
                else:
                    subtitles.append(SubtitleEntry(
                        index=index,
                        start=timedelta(seconds=start_time),
                        end=timedelta(seconds=end_time),
                        text=text
                    ))
                    index += 1
                i += 1
            else:
                merged_text = text
                merged_end = end_time
                j = i + 1
                
                while j < len(segments):
                    next_text = segments[j]["text"].strip()
                    if not next_text:
                        j += 1
                        continue
                    
                    next_end = segments[j]["end"]
                    
                    if (next_end - start_time) > max_duration * 1.5:
                        break
                    
                    merged_text += " " + next_text
                    merged_end = next_end
                    
                    if any(merged_text.rstrip().endswith(p) for p in ['.', '!', '?', '。', '！', '？']):
                        j += 1
                        break
                    
                    j += 1
                
                if len(merged_text) > 42:
                    lines = self.smart_split_subtitle(merged_text)
                    total_duration = merged_end - start_time
                    line_duration = total_duration / len(lines)
                    for idx, line in enumerate(lines):
                        line_start = start_time + (idx * line_duration)
                        line_end = line_start + line_duration
                        subtitles.append(SubtitleEntry(
                            index=index,
                            start=timedelta(seconds=line_start),
                            end=timedelta(seconds=line_end),
                            text=line
                        ))
                        index += 1
                else:
                    subtitles.append(SubtitleEntry(
                        index=index,
                        start=timedelta(seconds=start_time),
                        end=timedelta(seconds=merged_end),
                        text=merged_text
                    ))
                    index += 1
                
                i = j
                
        return subtitles
        
    def generate_captions(self, media_path: Path, model_name: str, mode: str, line_type: str, 
                          number_per_line: int, language_code: str, vocal_separation: str = "none",
                          is_youtube: bool = False, video_title: str = None) -> bool:
        try:
            self.stats = ProcessingStats()
            self.stats.start_time = time.time()
            self.stats.model_used = model_name
            self.stats.vocal_separation_used = (vocal_separation != "none")
            
            if not WHISPER_AVAILABLE:
                self.print_error("Whisper not available!")
                return False
                
            file_hash = self.get_file_hash(media_path)
            cached_result = self.get_cached_transcription(file_hash, model_name, language_code, mode, vocal_separation)
            
            if cached_result:
                self.print_success("Using cached transcription")
                result = cached_result
            else:
                audio_path = media_path
                if media_path.suffix.lower() in ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm']:
                    audio_path = self.extract_audio(media_path)
                    if not audio_path:
                        self.print_error("Could not extract audio")
                        return False
                
                if vocal_separation != "none":
                    self.print_info(f"Using {vocal_separation} vocal separation...")
                    
                    if SPLEETER_AVAILABLE and vocal_separation in ['2stems', '4stems', '5stems']:
                        self.spleeter_model = vocal_separation
                        vocals_path = self.separate_vocals_spleeter(audio_path)
                    else:
                        vocals_path = self.separate_vocals_ffmpeg(audio_path)
                    
                    if vocals_path and vocals_path.exists():
                        audio_path = vocals_path
                        self.print_success("Using isolated vocals for better transcription")
                    else:
                        self.print_warning("Vocal separation failed, using original audio")
                
                if self.model is None or self.stats.model_used != model_name:
                    if not self.load_model(model_name):
                        return False
                        
                self.print_progress("Transcribing with word-level timestamps...", 70)
                
                language = language_code if language_code != "auto" else None
                task = "translate" if mode == "translate" else "transcribe"
                
                transcribe_start = time.time()
                result = self.model.transcribe(
                    str(audio_path),
                    language=language,
                    task=task,
                    verbose=False,
                    word_timestamps=True,
                    fp16=False
                )
                self.stats.transcription_time = time.time() - transcribe_start
                
                self.cache_transcription(file_hash, model_name, language_code, mode, vocal_separation, result)
                
                if audio_path != media_path and audio_path and audio_path.exists():
                    try:
                        audio_path.unlink()
                    except:
                        pass
            
            self.print_progress("Processing transcription...", 80)
            
            # Determine output path
            lang_names = {"en": "english", "hi": "hindi", "ja": "japanese", "es": "spanish",
                         "ko": "korean", "zh": "chinese", "ru": "russian", "auto": "auto"}
            lang_name = lang_names.get(language_code, language_code)
            
            if is_youtube and video_title:
                suffix = f"{lang_name}" if mode == "normal" else f"{lang_name}_{mode}"
                if vocal_separation != "none":
                    suffix += f"_vocals"
                default_name = f"{video_title}_{suffix}.srt"
                save_path = save_file_dialog(default_name)
                if not save_path:
                    output_path = Path.cwd() / default_name
                else:
                    output_path = Path(save_path)
            else:
                if mode == "translate":
                    suffix = f"{lang_name}_translated"
                else:
                    suffix = lang_name
                if vocal_separation != "none":
                    suffix += f"_vocals"
                output_path = media_path.parent / f"{media_path.stem}_{suffix}.srt"
            
            segments = result.get("segments", [])
            self.stats.total_segments = len(segments)
            
            if line_type == "auto":
                subtitles = self.auto_break_sentences(segments)
            else:
                subtitles = []
                index = 1
                
                for segment in segments:
                    segment_text = segment.get("text", "").strip()
                    if not segment_text:
                        continue
                        
                    segment_start = segment.get("start", 0)
                    segment_end = segment.get("end", segment_start + 1)
                    
                    words_data = segment.get("words", [])
                    
                    if line_type == "words" and words_data:
                        words = []
                        word_starts = []
                        word_ends = []
                        
                        for w in words_data:
                            word = w.get("word", "").strip()
                            if word:
                                words.append(word)
                                word_starts.append(w.get("start", segment_start))
                                word_ends.append(w.get("end", segment_end))
                        
                        for i in range(0, len(words), number_per_line):
                            chunk_words = words[i:i + number_per_line]
                            line_text = " ".join(chunk_words).strip()
                            if not line_text:
                                continue
                            chunk_start = word_starts[i]
                            chunk_end = word_ends[min(i + number_per_line - 1, len(word_ends) - 1)]
                            
                            subtitles.append(SubtitleEntry(
                                index=index,
                                start=timedelta(seconds=chunk_start),
                                end=timedelta(seconds=chunk_end),
                                text=line_text
                            ))
                            index += 1
                    else:
                        if line_type == "letters":
                            segment_text = self.limit_letters_per_line(segment_text, number_per_line)
                        
                        if len(segment_text) > 42:
                            lines = self.smart_split_subtitle(segment_text)
                            duration = segment_end - segment_start
                            line_duration = duration / len(lines)
                            for idx, line in enumerate(lines):
                                line_start = segment_start + (idx * line_duration)
                                line_end = line_start + line_duration
                                subtitles.append(SubtitleEntry(
                                    index=index,
                                    start=timedelta(seconds=line_start),
                                    end=timedelta(seconds=line_end),
                                    text=line
                                ))
                                index += 1
                        else:
                            subtitles.append(SubtitleEntry(
                                index=index,
                                start=timedelta(seconds=segment_start),
                                end=timedelta(seconds=segment_end),
                                text=segment_text
                            ))
                            index += 1
            
            self.print_progress("Writing subtitle file...", 90)
            with open(output_path, 'w', encoding='utf-8') as f:
                for sub in subtitles:
                    f.write(sub.to_srt())
            
            self.stats.end_time = time.time()
            
            show_message_box("Success", f"Captions saved to:\n{output_path}", "info")
            
            self.print_progress("Complete!", 100)
            print()
            self.print_success(f"Saved to: {output_path}")
            self.print_info(f"Generated {len(subtitles)} subtitle entries")
            self.stats.display()
            return True
            
        except Exception as e:
            self.print_error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            show_message_box("Error", f"Failed to generate captions:\n{str(e)}", "error")
            return False
            
    def show_about(self):
        self.clear_screen()
        print_header()
        self.print_box([
            f"{APP_NAME} v{APP_VERSION}",
            f"Author: {APP_AUTHOR}",
            f"License: {APP_LICENSE}",
            "",
            "Powered by:",
            "  • OpenAI Whisper - Speech Recognition",
            "  • Spleeter - Vocal Separation",
            "  • yt-dlp - YouTube Downloading",
            "  • FFmpeg - Audio Processing",
            "",
            "Support:",
            f"  Telegram: {APP_TELEGRAM}",
            f"  YouTube: {APP_YOUTUBE}"
        ])
        input("\nPress Enter to continue...")
        
    def run(self):
        if not self.check_ffmpeg():
            self.print_warning("FFmpeg not found! Some features may not work.")
        
        if not WHISPER_AVAILABLE:
            self.print_error("Whisper not available!")
            self.print_info("Please install: pip install openai-whisper torch")
            input("\nPress Enter to exit...")
            return
        
        if SPLEETER_AVAILABLE:
            self.print_success("Spleeter available for high-quality vocal separation")
            if self.has_local_spleeter_models:
                self.print_success("Local Spleeter models found (no download needed)")
            else:
                self.print_info("Spleeter models will be downloaded on first use")
        else:
            self.print_warning("Spleeter not available. Install: pip install spleeter tensorflow")
            
        # Check for Send To file
        if self.media_path_arg and not self.is_sendto:
            media_path = Path(self.media_path_arg)
            if media_path.exists() and media_path.suffix.lower() in SUPPORTED_EXTENSIONS['all']:
                self.print_success(f"File received: {media_path}")
                platform_choice = 2
                passed_file = media_path
            else:
                self.print_error(f"File not found: {media_path}")
                passed_file = None
                platform_choice = None
        elif self.media_path_arg and self.is_sendto:
            media_path = Path(self.media_path_arg)
            if media_path.exists() and media_path.suffix.lower() in SUPPORTED_EXTENSIONS['all']:
                self.print_success(f"File received from Send To: {media_path}")
                platform_choice = 2
                passed_file = media_path
            else:
                self.print_error(f"Invalid file: {media_path}")
                passed_file = None
                platform_choice = None
        else:
            platform_choice = None
            passed_file = None
        
        self.print_success("Whisper loaded successfully")
        
        while True:
            try:
                if platform_choice is None:
                    self.clear_screen()
                    print_header()
                    print(f"\n{Colors.CYAN}{Colors.BOLD}MAIN MENU{Colors.RESET}")
                    print(f"{Colors.CYAN}┌{'─' * 50}┐{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  1) YouTube - Download and generate captions{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  2) Local File - Use local video/audio file{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  3) About - Information about the app{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  0) Exit{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}└{'─' * 50}┘{Colors.RESET}")
                    
                    platform_choice = self.get_number_input("Choose option (0-3): ", 0, 3)
                    
                    if platform_choice == 0:
                        break
                    elif platform_choice == 3:
                        self.show_about()
                        platform_choice = None
                        continue
                    
                    self.menu_stack = []
                    self.current_menu = "main"
                    
                    platform_name = "YouTube" if platform_choice == 1 else "Local File"
                    self.clear_screen()
                    print_header()
                    print(f"\n{Colors.CYAN}Use {platform_name}?{Colors.RESET}")
                    print(f"\n  1) Continue")
                    print(f"  0) Back")
                    
                    confirm_choice = self.get_number_input("\nChoose option (0-1): ", 0, 1)
                    if confirm_choice == 0:
                        platform_choice = None
                        continue
                
                media_path = None
                video_title = None
                
                if platform_choice == 1:
                    while True:
                        self.clear_screen()
                        print_header()
                        url = self.get_youtube_url()
                        if not url:
                            platform_choice = None
                            break
                        
                        self.clear_screen()
                        print_header()
                        print(f"\n{Colors.CYAN}URL: {url}{Colors.RESET}")
                        print(f"\n  1) Continue")
                        print(f"  2) Paste again")
                        print(f"  0) Back")
                        
                        url_choice = self.get_number_input("\nChoose option (0-2): ", 0, 2)
                        if url_choice == 0:
                            platform_choice = None
                            break
                        elif url_choice == 2:
                            continue
                        
                        self.print_info("Downloading...")
                        media_path, video_title = self.download_youtube_audio(url)
                        
                        if not media_path:
                            self.print_error("Download failed!")
                            input("Press Enter...")
                            continue
                        break
                    
                    if not media_path:
                        continue
                        
                else:
                    if passed_file:
                        media_path = passed_file
                        passed_file = None
                    else:
                        self.clear_screen()
                        print_header()
                        print(f"\n{Colors.CYAN}Supported Formats:{Colors.RESET}")
                        self.print_table(
                            ["Type", "Formats"],
                            [["Video", ", ".join(SUPPORTED_EXTENSIONS['video'])],
                             ["Audio", ", ".join(SUPPORTED_EXTENSIONS['audio'])]]
                        )
                        print()
                        
                        media_path_str = select_file_dialog()
                        if not media_path_str:
                            platform_choice = None
                            continue
                        media_path = Path(media_path_str)
                    
                    if not media_path.exists():
                        self.print_error("File not found!")
                        platform_choice = None
                        continue
                
                self.print_success(f"Source: {media_path.name if platform_choice == 2 else video_title or 'YouTube Audio'}")
                
                # Select vocal separation
                self.clear_screen()
                print_header()
                print(f"\n{Colors.CYAN}{Colors.BOLD}VOCAL SEPARATION{Colors.RESET}")
                print(f"  Spleeter can isolate vocals for better transcription accuracy")
                if self.has_local_spleeter_models:
                    print(f"  {Colors.GREEN}✓ Local models available (no download needed){Colors.RESET}")
                print()
                
                vocal_options = [f"{v[0]} - {v[2]}" for v in self.vocal_quality_options]
                vocal_choice = self.show_menu("SELECT VOCAL SEPARATION", vocal_options, "vocal")
                if vocal_choice == -1:
                    platform_choice = None
                    continue
                    
                self.selected_vocal_quality = self.vocal_quality_options[vocal_choice]
                vocal_separation = self.selected_vocal_quality[1]
                self.use_vocal_separation = (vocal_separation != "none")
                self.spleeter_model = vocal_separation if self.use_vocal_separation else "2stems"
                
                if self.use_vocal_separation:
                    self.print_info(f"Vocal separation: {self.selected_vocal_quality[0]}")
                
                # Select Whisper model
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}Source: {media_path.name if platform_choice == 2 else 'YouTube Audio'}{Colors.RESET}")
                if self.use_vocal_separation:
                    print(f"{Colors.GREEN}Vocal: {self.selected_vocal_quality[0]}{Colors.RESET}")
                print()
                
                model_options = [f"{m[0].upper()} ({m[1]}) - {m[2]}" for m in self.models]
                model_choice = self.show_menu("SELECT WHISPER MODEL", model_options, "model")
                if model_choice == -1:
                    platform_choice = None
                    continue
                self.selected_model = self.models[model_choice][0]
                
                # Select mode
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}Source: {media_path.name if platform_choice == 2 else 'YouTube Audio'}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                if self.use_vocal_separation:
                    print(f"{Colors.GREEN}Vocal: {self.selected_vocal_quality[0]}{Colors.RESET}")
                print()
                
                mode_options = [f"{m[0]} - {m[2]}" for m in self.modes]
                mode_choice = self.show_menu("SELECT MODE", mode_options, "mode")
                if mode_choice == -1:
                    self.menu_stack.pop()
                    self.current_menu = "model"
                    continue
                self.selected_mode = self.modes[mode_choice]
                mode = self.selected_mode[1]
                
                # Select language
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}Source: {media_path.name if platform_choice == 2 else 'YouTube Audio'}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                print(f"{Colors.GREEN}Mode: {self.selected_mode[0]}{Colors.RESET}")
                if self.use_vocal_separation:
                    print(f"{Colors.GREEN}Vocal: {self.selected_vocal_quality[0]}{Colors.RESET}")
                print()
                
                lang_options = [f"{lang[0]} ({lang[1]})" for lang in self.languages]
                lang_choice = self.show_menu("SELECT LANGUAGE", lang_options, "language")
                if lang_choice == -1:
                    self.menu_stack.pop()
                    self.current_menu = "mode"
                    continue
                self.selected_language = self.languages[lang_choice]
                language_code = self.selected_language[1]
                language_name = self.selected_language[0]
                
                # Select line type
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}Source: {media_path.name if platform_choice == 2 else 'YouTube Audio'}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                print(f"{Colors.GREEN}Mode: {self.selected_mode[0]}{Colors.RESET}")
                print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}")
                if self.use_vocal_separation:
                    print(f"{Colors.GREEN}Vocal: {self.selected_vocal_quality[0]}{Colors.RESET}")
                print()
                
                line_options = [f"{l[0]} - {l[2]}" for l in self.line_types]
                line_choice = self.show_menu("LINE BREAK TYPE", line_options, "line_type")
                if line_choice == -1:
                    self.menu_stack.pop()
                    self.current_menu = "language"
                    continue
                self.selected_line_type = self.line_types[line_choice]
                line_type = self.selected_line_type[1]
                
                number_per_line = 5
                if line_type == "words":
                    number_per_line = self.get_number_input("How many words per line? (1-30): ", 1, 30)
                elif line_type == "letters":
                    number_per_line = self.get_number_input("How many letters per line? (1-50): ", 1, 50)
                
                self.clear_screen()
                print_header()
                self.print_box([
                    f"Source: {'YouTube' if platform_choice == 1 else 'Local File'}",
                    f"File: {media_path.name if platform_choice == 2 else video_title or 'YouTube Audio'}",
                    f"Vocal Separation: {self.selected_vocal_quality[0] if self.use_vocal_separation else 'No'}",
                    f"Model: {self.selected_model.upper()}",
                    f"Mode: {self.selected_mode[0]}",
                    f"Language: {language_name}",
                    f"Line Break: {self.selected_line_type[0]}",
                    f"Settings: {number_per_line if line_type != 'auto' else 'Smart detection'}"
                ])
                
                if not self.confirm("Generate captions?"):
                    platform_choice = None
                    continue
                
                self.print_info("Generating captions... This may take several minutes.")
                success = self.generate_captions(
                    media_path, self.selected_model, mode, line_type,
                    number_per_line, language_code, vocal_separation,
                    is_youtube=(platform_choice == 1), video_title=video_title
                )
                
                if platform_choice == 1 and media_path and media_path.exists():
                    try:
                        media_path.unlink()
                    except:
                        pass
                
                if success:
                    self.print_success(f"Thanks for using {APP_NAME}!")
                    
                    try:
                        webbrowser.open(APP_TELEGRAM)
                        webbrowser.open(APP_YOUTUBE)
                    except:
                        pass
                    
                    if not self.confirm("Process another file?"):
                        break
                    else:
                        platform_choice = None
                        passed_file = None
                        self.is_sendto = False
                        self.menu_stack = []
                        self.current_menu = "main"
                        self.model = None  # Reset model to save memory
                else:
                    self.print_error("Failed to generate captions")
                    if not self.confirm("Try again?"):
                        platform_choice = None
                        continue
                        
            except KeyboardInterrupt:
                print("\n")
                self.print_warning("Interrupted by user")
                break
            except Exception as e:
                self.print_error(f"Error: {e}")
                if not self.confirm("Continue?"):
                    break
                    
        self.clear_screen()
        print_header("Thank You!")
        self.print_success(f"Thanks for using {APP_NAME}!")
        print()
        self.print_info("Cleaning up temporary files...")
        cleanup_temp_files()
        self.print_success("Cleanup complete!")
        
        print("\n" + "=" * 60)
        print("Application will now close...")
        print("=" * 60)
        time.sleep(2)
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'{APP_NAME} - {APP_AUTHOR}')
    parser.add_argument('file', nargs='?', help='Video/Audio file to process (supports Send To)')
    args = parser.parse_args()
    
    app = NotYCaptionGenerator(args.file)
    app.run()