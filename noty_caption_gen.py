#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NotY Caption Generator AI v6.1
Using OpenAI Whisper (PyTorch) with YouTube Support & Smart Lyrics Matching
Copyright (c) 2026 NotY215
"""

# CRITICAL: These imports must be at the top for frozen apps
import os
import sys
import atexit
import glob

# Fix for PyInstaller/Nuitka packaged app
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
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

# Import torch with fallback
try:
    import torch
    if not hasattr(torch, 'cuda') or torch.cuda.is_available() is None:
        torch.cuda = _MockCuda()
except ImportError:
    class _MockTorch:
        cuda = _MockCuda()
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
from typing import List, Tuple, Dict, Optional
from datetime import timedelta
import re
import json
import urllib.request
import urllib.parse
import tempfile
import shutil
import hashlib
import sqlite3
from dataclasses import dataclass
from enum import Enum

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
    """Clean up temporary files created by the app"""
    try:
        temp_dir = Path(tempfile.gettempdir())
        patterns = ["*_temp_audio.wav", "*_vocals.wav", "youtube_audio_*"]
        for pattern in patterns:
            for file in temp_dir.glob(pattern):
                try:
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
    print("|" + "Powered by OpenAI Whisper".center(58) + "|")
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

# Language codes with full transliteration support
class Language(Enum):
    ENGLISH = ("en", "English", False)
    HINDI = ("hi", "Hindi", True)
    JAPANESE = ("ja", "Japanese", True)
    SPANISH = ("es", "Spanish", True)
    KOREAN = ("ko", "Korean", True)
    CHINESE = ("zh", "Chinese (Mandarin)", True)
    RUSSIAN = ("ru", "Russian", True)
    AUTO = ("auto", "Auto Detect", False)

# Complete transliteration mappings - IMPROVED for better accuracy
TRANSLITERATION_MAPS = {
    # Russian (Cyrillic to Latin) - ISO 9 standard
    "ru": {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    },
    # Spanish (accent removal and special chars)
    "es": {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ü': 'U',
        'ñ': 'n', 'Ñ': 'N',
        '¿': '', '¡': '', 'º': 'o', 'ª': 'a',
        'ç': 'c', 'Ç': 'C'
    },
    # Chinese Pinyin (tone marks to letters)
    "zh": {
        'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
        'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
        'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
        'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
        'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
        'ǖ': 'v', 'ǘ': 'v', 'ǚ': 'v', 'ǜ': 'v',
    },
    # Hindi (Devanagari to Latin) - IMPROVED
    "hi": {
        'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
        'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'am', 'अः': 'ah',
        'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
        'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nya',
        'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
        'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
        'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
        'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va', 'श': 'sha', 'ष': 'sha', 'स': 'sa', 'ह': 'ha',
        'क्ष': 'ksha', 'त्र': 'tra', 'ज्ञ': 'gya', 'श्र': 'shra',
        'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
        'ं': 'n', 'ः': 'h', '्': '',
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    },
    # Japanese (Kana to Romaji) - IMPROVED
    "ja": {
        'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
        'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
        'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
        'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
        'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
        'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
        'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
        'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
        'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
        'わ': 'wa', 'を': 'wo', 'ん': 'n',
        'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
        'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
        'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
        'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
        'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
        'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo',
        'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho',
        'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
        'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo',
        'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo',
        'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
        'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
        'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo',
        'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
        'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo',
        'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo',
        'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o',
        'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko',
        'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so',
        'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to',
        'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no',
        'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho',
        'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo',
        'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo',
        'ラ': 'ra', 'リ': 'ri', 'ル': 'ru', 'レ': 're', 'ロ': 'ro',
        'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n',
        'ガ': 'ga', 'ギ': 'gi', 'グ': 'gu', 'ゲ': 'ge', 'ゴ': 'go',
        'ザ': 'za', 'ジ': 'ji', 'ズ': 'zu', 'ゼ': 'ze', 'ゾ': 'zo',
        'ダ': 'da', 'ヂ': 'ji', 'ヅ': 'zu', 'デ': 'de', 'ド': 'do',
        'バ': 'ba', 'ビ': 'bi', 'ブ': 'bu', 'ベ': 'be', 'ボ': 'bo',
        'パ': 'pa', 'ピ': 'pi', 'プ': 'pu', 'ペ': 'pe', 'ポ': 'po',
        'キャ': 'kya', 'キュ': 'kyu', 'キョ': 'kyo',
        'シャ': 'sha', 'シュ': 'shu', 'ショ': 'sho',
        'チャ': 'cha', 'チュ': 'chu', 'チョ': 'cho',
        'ニャ': 'nya', 'ニュ': 'nyu', 'ニョ': 'nyo',
        'ヒャ': 'hya', 'ヒュ': 'hyu', 'ヒョ': 'hyo',
        'ミャ': 'mya', 'ミュ': 'myu', 'ミョ': 'myo',
        'リャ': 'rya', 'リュ': 'ryu', 'リョ': 'ryo',
        'ギャ': 'gya', 'ギュ': 'gyu', 'ギョ': 'gyo',
        'ジャ': 'ja', 'ジュ': 'ju', 'ジョ': 'jo',
        'ビャ': 'bya', 'ビュ': 'byu', 'ビョ': 'byo',
        'ピャ': 'pya', 'ピュ': 'pyu', 'ピョ': 'pyo',
        'っ': 't', 'ッ': 't', 'ー': ''
    },
    # Korean (Hangul to Romanized) - IMPROVED
    "ko": {
        'ㄱ': 'g', 'ㄲ': 'kk', 'ㄴ': 'n', 'ㄷ': 'd', 'ㄸ': 'tt',
        'ㄹ': 'r', 'ㅁ': 'm', 'ㅂ': 'b', 'ㅃ': 'pp', 'ㅅ': 's',
        'ㅆ': 'ss', 'ㅇ': '', 'ㅈ': 'j', 'ㅉ': 'jj', 'ㅊ': 'ch',
        'ㅋ': 'k', 'ㅌ': 't', 'ㅍ': 'p', 'ㅎ': 'h',
        'ㅏ': 'a', 'ㅐ': 'ae', 'ㅑ': 'ya', 'ㅒ': 'yae', 'ㅓ': 'eo',
        'ㅔ': 'e', 'ㅕ': 'yeo', 'ㅖ': 'ye', 'ㅗ': 'o', 'ㅘ': 'wa',
        'ㅙ': 'wae', 'ㅚ': 'oe', 'ㅛ': 'yo', 'ㅜ': 'u', 'ㅝ': 'wo',
        'ㅞ': 'we', 'ㅟ': 'wi', 'ㅠ': 'yu', 'ㅡ': 'eu', 'ㅢ': 'ui',
        'ㅣ': 'i'
    }
}

# Whisper models
WHISPER_MODELS = {
    "tiny": {"size": "75 MB", "desc": "Fastest"},
    "base": {"size": "150 MB", "desc": "Balanced"},
    "small": {"size": "500 MB", "desc": "Good"},
    "medium": {"size": "1.5 GB", "desc": "Accurate"},
    "large": {"size": "2.9 GB", "desc": "Best"}
}

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm'],
    'audio': ['.mp3', '.wav', '.m4a', '.flac'],
    'all': ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm', '.mp3', '.wav', '.m4a', '.flac']
}

@dataclass
class SubtitleEntry:
    index: int
    start: timedelta
    end: timedelta
    text: str
    
class NotYCaptionGenerator:
    def __init__(self, media_path: str = None):
        # Register cleanup on exit
        atexit.register(cleanup_temp_files)
        
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
            
        self.models_dir = self.base_dir / "models"
        self.ffmpeg_dir = self.base_dir / "ffmpeg"
        self.cache_dir = self.base_dir / "cache"
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
        
        # Language mapping for display
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
            ("Normal Mode", "normal", "Standard transcription without transliteration"),
            ("Transliteration Mode", "transliterate", "Convert non-Latin scripts to Latin alphabet"),
            ("Translate Mode", "translate", "Translate to English while transcribing")
        ]
        
        self.line_types = [
            ("Words", "words", "Break by word count (1-30)"),
            ("Letters", "letters", "Break by character limit (1-30)"),
            ("Auto", "auto", "Auto-detect sentence breaks by audio gaps")
        ]
        
        self.selected_model = None
        self.selected_language = None
        self.selected_mode = None
        self.selected_line_type = None
        self.media_path_arg = media_path
        self.model = None
        self.is_sendto = media_path is not None
        
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
        
        self.conn.commit()
        
    def get_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def cache_transcription(self, file_hash: str, model_name: str, language: str, mode: str, result: dict):
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO transcriptions (file_hash, model_name, language, mode, result) VALUES (?, ?, ?, ?, ?)",
                (file_hash, model_name, language, mode, json.dumps(result))
            )
            self.conn.commit()
        except:
            pass
            
    def get_cached_transcription(self, file_hash: str, model_name: str, language: str, mode: str) -> Optional[dict]:
        try:
            self.cursor.execute(
                "SELECT result FROM transcriptions WHERE file_hash = ? AND model_name = ? AND language = ? AND mode = ?",
                (file_hash, model_name, language, mode)
            )
            row = self.cursor.fetchone()
            if row:
                return json.loads(row[0])
        except:
            pass
        return None
        
    def clear_screen(self):
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
    def print_success(self, message: str):
        print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")
        
    def print_error(self, message: str):
        print(f"{Colors.RED}[ERROR] {message}{Colors.RESET}")
        
    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}[WARNING] {message}{Colors.RESET}")
        
    def print_info(self, message: str):
        print(f"{Colors.CYAN}[INFO] {message}{Colors.RESET}")
        
    def print_progress(self, message: str, percent: int = None):
        if percent is not None:
            bar_length = 40
            filled = int(bar_length * percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r{Colors.CYAN}[PROGRESS] {bar} {percent}% - {message}{Colors.RESET}", end="", flush=True)
            if percent == 100:
                print()
        else:
            print(f"{Colors.CYAN}[PROGRESS] {message}{Colors.RESET}")
        
    def print_box(self, lines: List[str]):
        width = max(len(line) for line in lines) + 4
        print(f"{Colors.GREEN}")
        print("+" + "-" * (width - 2) + "+")
        for line in lines:
            print(f"| {line.ljust(width - 4)} |")
        print("+" + "-" * (width - 2) + "+")
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
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            self.print_error("Please enter y or n")
            
    def show_menu(self, title: str, options: List[str]) -> int:
        while True:
            print(f"\n{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
            print(f"{Colors.CYAN}┌{'─' * 50}┐{Colors.RESET}")
            for i, option in enumerate(options, 1):
                print(f"{Colors.CYAN}│{Colors.RESET} {i:2}) {option:<45} {Colors.CYAN}│{Colors.RESET}")
            print(f"{Colors.CYAN}│{Colors.RESET}  0) Back{' ' * 45}{Colors.CYAN}│{Colors.RESET}")
            print(f"{Colors.CYAN}└{'─' * 50}┘{Colors.RESET}")
            
            choice = self.get_number_input(f"Choose option (0-{len(options)}): ", 0, len(options))
            if choice == 0:
                return -1
            return choice - 1
            
    def get_media_path_sendto(self, file_path: str) -> Path:
        path = Path(file_path)
        if path.exists() and path.suffix.lower() in SUPPORTED_EXTENSIONS['all']:
            self.print_success(f"File received from Send To: {path}")
            return path
        return None
        
    def get_youtube_url(self) -> Optional[str]:
        print(f"\n{Colors.CYAN}Paste YouTube URL:{Colors.RESET}")
        print(f"   Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        url = self.get_input("\n> ").strip()
        if not url:
            self.print_error("URL cannot be empty!")
            return None
        return url
        
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
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', '')
                # Clean title for filename
                video_title_clean = re.sub(r'[<>:"/\\|?*]', '', video_title)[:50]
                self.print_info(f"Video: {video_title}")
                
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
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return True
        except:
            pass
        return False
            
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
                self.print_progress("Audio extracted", 20)
                return audio_path
        except:
            pass
        return None
        
    def transliterate_text(self, text: str, language_code: str) -> str:
        """Convert text from non-Latin scripts to Latin alphabet"""
        if language_code not in TRANSLITERATION_MAPS:
            return text
            
        mapping = TRANSLITERATION_MAPS[language_code]
        # Sort keys by length (longest first) for proper replacement
        sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
        
        result = text
        for original in sorted_keys:
            translit = mapping[original]
            result = result.replace(original, translit)
        
        # Clean up extra spaces and normalize
        result = re.sub(r'\s+', ' ', result)
        result = result.strip()
        
        return result
        
    def load_model(self, model_name: str):
        if not WHISPER_AVAILABLE:
            self.print_error("Whisper not available!")
            return False
            
        try:
            self.print_progress(f"Loading {model_name} model...", 60)
            self.model = whisper.load_model(model_name, download_root=str(self.models_dir))
            self.print_success("Model loaded")
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
        
    def auto_break_sentences(self, segments) -> List[SubtitleEntry]:
        subtitles = []
        index = 1
        min_gap = 0.3
        
        i = 0
        while i < len(segments):
            segment = segments[i]
            text = segment["text"].strip()
            if not text:
                i += 1
                continue
                
            start_time = segment["start"]
            end_time = segment["end"]
            
            if text.endswith(('.', '!', '?')):
                subtitles.append(SubtitleEntry(
                    index=index,
                    start=timedelta(seconds=start_time),
                    end=timedelta(seconds=end_time),
                    text=text
                ))
                index += 1
                i += 1
            elif i < len(segments) - 1 and segments[i+1]["start"] - end_time > min_gap:
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
                    merged_text += " " + next_text
                    merged_end = segments[j]["end"]
                    
                    if next_text.endswith(('.', '!', '?')) or (j < len(segments) - 1 and 
                       segments[j+1]["start"] - segments[j]["end"] > min_gap):
                        j += 1
                        break
                    j += 1
                
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
                          number_per_line: int, language_code: str, is_youtube: bool = False, video_title: str = None) -> bool:
        try:
            if not WHISPER_AVAILABLE:
                self.print_error("Whisper not available!")
                return False
                
            file_hash = self.get_file_hash(media_path)
            cached_result = self.get_cached_transcription(file_hash, model_name, language_code, mode)
            
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
                
                if self.model is None:
                    if not self.load_model(model_name):
                        return False
                        
                self.print_progress("Transcribing with word-level timestamps...", 70)
                
                language = language_code if language_code != "auto" else None
                task = "translate" if mode == "translate" else "transcribe"
                
                result = self.model.transcribe(
                    str(audio_path),
                    language=language,
                    task=task,
                    verbose=False,
                    word_timestamps=True
                )
                
                self.cache_transcription(file_hash, model_name, language_code, mode, result)
                
                if audio_path != media_path and audio_path and audio_path.exists():
                    try:
                        audio_path.unlink()
                    except:
                        pass
            
            self.print_progress("Processing transcription with proper timing...", 80)
            
            # Determine output path based on source
            lang_map = {
                "en": "english", "hi": "hindi", "ja": "japanese", "es": "spanish",
                "ko": "korean", "zh": "chinese", "ru": "russian", "auto": "auto"
            }
            lang_name = lang_map.get(language_code, language_code)
            
            if is_youtube and video_title:
                # YouTube mode - ask user where to save
                default_name = f"{video_title}_{lang_name}.srt"
                save_path = save_file_dialog(default_name)
                if not save_path:
                    self.print_warning("No save location selected. Saving in current directory.")
                    output_path = Path.cwd() / default_name
                else:
                    output_path = Path(save_path)
            else:
                # Local mode - save in same directory as source file
                if mode == "translate":
                    suffix = f"{lang_name}_translated"
                elif mode == "transliterate":
                    suffix = lang_name
                else:
                    suffix = lang_name
                output_path = media_path.parent / f"{media_path.stem}_{suffix}.srt"
            
            segments = result.get("segments", [])
            
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
                    
                    # Apply transliteration if mode is transliterate
                    if mode == "transliterate" and language_code in TRANSLITERATION_MAPS:
                        segment_text = self.transliterate_text(segment_text, language_code)
                    
                    words_data = segment.get("words", [])
                    
                    if line_type == "words" and words_data:
                        # Use word-level timestamps for perfect sync
                        words = []
                        word_starts = []
                        word_ends = []
                        
                        for w in words_data:
                            word = w.get("word", "").strip()
                            if word:
                                if mode == "transliterate" and language_code in TRANSLITERATION_MAPS:
                                    word = self.transliterate_text(word, language_code)
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
                        
                        if mode == "transliterate" and language_code in TRANSLITERATION_MAPS:
                            segment_text = self.transliterate_text(segment_text, language_code)
                        
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
                    start_str = self.format_time(sub.start.total_seconds())
                    end_str = self.format_time(sub.end.total_seconds())
                    f.write(f"{sub.index}\n{start_str} --> {end_str}\n{sub.text}\n\n")
            
            show_message_box("Success", f"Captions saved to:\n{output_path}", "info")
            
            self.print_progress("Complete!", 100)
            print()
            self.print_success(f"Saved to: {output_path}")
            self.print_info(f"Generated {len(subtitles)} subtitle entries")
            return True
            
        except Exception as e:
            self.print_error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            show_message_box("Error", f"Failed to generate captions:\n{str(e)}", "error")
            return False
            
    def run(self):
        if not self.check_ffmpeg():
            self.print_warning("FFmpeg not found! Some features may not work.")
        
        if not WHISPER_AVAILABLE:
            self.print_error("Whisper is not available!")
            self.print_info("Please install: pip install openai-whisper torch")
            input("\nPress Enter to exit...")
            return
            
        # Check if file was sent via Send To
        if self.media_path_arg and not self.is_sendto:
            media_path = Path(self.media_path_arg)
            if media_path.exists() and media_path.suffix.lower() in SUPPORTED_EXTENSIONS['all']:
                self.print_success(f"File received: {media_path}")
                platform_choice = 2
                passed_file = media_path
            else:
                self.print_error(f"File not found: {media_path}")
                self.is_sendto = False
                passed_file = None
        elif self.media_path_arg and self.is_sendto:
            media_path = Path(self.media_path_arg)
            if media_path.exists() and media_path.suffix.lower() in SUPPORTED_EXTENSIONS['all']:
                self.print_success(f"File received from Send To: {media_path}")
                platform_choice = 2
                passed_file = media_path
            else:
                self.print_error(f"Invalid file: {media_path}")
                self.is_sendto = False
                passed_file = None
        else:
            platform_choice = None
            passed_file = None
        
        self.print_success("Whisper loaded successfully")
        
        while True:
            try:
                if platform_choice is None:
                    self.clear_screen()
                    print_header()
                    print(f"\n{Colors.CYAN}{Colors.BOLD}SELECT PLATFORM{Colors.RESET}")
                    print(f"{Colors.CYAN}┌{'─' * 50}┐{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  1) YouTube - Download and generate captions{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  2) Local File - Use local video/audio file{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  0) Exit{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}└{'─' * 50}┘{Colors.RESET}")
                    
                    platform_choice = self.get_number_input("Choose option (0-2): ", 0, 2)
                    
                    if platform_choice == 0:
                        break
                    
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
                    # YouTube mode
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
                    # Local file mode
                    if passed_file:
                        media_path = passed_file
                        passed_file = None
                    else:
                        self.clear_screen()
                        print_header()
                        print(f"\n{Colors.CYAN}Supported Formats:{Colors.RESET}")
                        print(f"  Video: {', '.join(SUPPORTED_EXTENSIONS['video'])}")
                        print(f"  Audio: {', '.join(SUPPORTED_EXTENSIONS['audio'])}")
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
                
                # Select model
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}Source: {media_path.name if platform_choice == 2 else 'YouTube Audio'}{Colors.RESET}\n")
                
                model_options = [f"{m[0].upper()} ({m[1]}) - {m[2]}" for m in self.models]
                model_choice = self.show_menu("SELECT MODEL", model_options)
                if model_choice == -1:
                    if platform_choice == 1 and media_path and media_path.exists():
                        try:
                            media_path.unlink()
                        except:
                            pass
                    platform_choice = None
                    continue
                self.selected_model = self.models[model_choice][0]
                
                # Select mode
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}Source: {media_path.name if platform_choice == 2 else 'YouTube Audio'}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}\n")
                
                mode_options = [f"{m[0]} - {m[2]}" for m in self.modes]
                mode_choice = self.show_menu("SELECT MODE", mode_options)
                if mode_choice == -1:
                    if platform_choice == 1 and media_path and media_path.exists():
                        try:
                            media_path.unlink()
                        except:
                            pass
                    platform_choice = None
                    continue
                self.selected_mode = self.modes[mode_choice]
                mode = self.selected_mode[1]
                
                # Select language
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}Source: {media_path.name if platform_choice == 2 else 'YouTube Audio'}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                print(f"{Colors.GREEN}Mode: {self.selected_mode[0]}{Colors.RESET}\n")
                
                lang_options = [f"{lang[0]} ({lang[1]})" for lang in self.languages]
                lang_choice = self.show_menu("SELECT LANGUAGE", lang_options)
                if lang_choice == -1:
                    if platform_choice == 1 and media_path and media_path.exists():
                        try:
                            media_path.unlink()
                        except:
                            pass
                    platform_choice = None
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
                print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}\n")
                
                line_options = [f"{l[0]} - {l[2]}" for l in self.line_types]
                line_choice = self.show_menu("LINE BREAK TYPE", line_options)
                if line_choice == -1:
                    if platform_choice == 1 and media_path and media_path.exists():
                        try:
                            media_path.unlink()
                        except:
                            pass
                    platform_choice = None
                    continue
                self.selected_line_type = self.line_types[line_choice]
                line_type = self.selected_line_type[1]
                
                number_per_line = 5
                if line_type != "auto":
                    number_per_line = self.get_number_input(
                        f"How many {line_type} per line? (1-30): ", 1, 30
                    )
                
                self.clear_screen()
                print_header()
                self.print_box([
                    f"Source: {'YouTube' if platform_choice == 1 else 'Local File'}",
                    f"File: {media_path.name if platform_choice == 2 else video_title or 'YouTube Audio'}",
                    f"Model: {self.selected_model.upper()}",
                    f"Mode: {self.selected_mode[0]}",
                    f"Language: {language_name}",
                    f"Line Break: {self.selected_line_type[0]}",
                    f"Settings: {number_per_line if line_type != 'auto' else 'Auto-detect'}"
                ])
                
                if not self.confirm("Generate captions?"):
                    if platform_choice == 1 and media_path and media_path.exists():
                        try:
                            media_path.unlink()
                        except:
                            pass
                    platform_choice = None
                    continue
                
                self.print_info("Generating captions... This may take several minutes.")
                success = self.generate_captions(
                    media_path,
                    self.selected_model,
                    mode,
                    line_type,
                    number_per_line,
                    language_code,
                    is_youtube=(platform_choice == 1),
                    video_title=video_title
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