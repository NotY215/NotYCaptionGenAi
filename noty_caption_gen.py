#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NotY Caption Generator AI v5.2
Using OpenAI Whisper (PyTorch) with FFmpeg Vocal Separation & Smart Lyrics Matching
Copyright (c) 2026 NotY215
"""

import os
import sys
import webbrowser
import time
import platform
import argparse
import subprocess
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import timedelta
import re
import json
import urllib.request
import urllib.parse
import tempfile
import shutil

# Fix Windows console encoding
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# Set environment variables
os.environ['TORCH_USE_RTLD_GLOBAL'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

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

if platform.system() == "Windows":
    try:
        import colorama
        colorama.init()
    except:
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')

def select_file_dialog():
    """Open file selection dialog for video/audio"""
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
        file_path = filedialog.askopenfilename(
            title="Select Video/Audio File",
            filetypes=file_types
        )
        root.destroy()
        return file_path
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Could not open file dialog: {e}{Colors.RESET}")
        return None

def print_header(title: str = None):
    """Print application header"""
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
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"
APP_LICENSE = "LGPL-3.0"
APP_TELEGRAM = "https://t.me/Noty_215"
APP_YOUTUBE = "https://www.youtube.com/@NotY215"

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

class NotYCaptionGenerator:
    def __init__(self, media_path: str = None):
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
            
        self.models_dir = self.base_dir / "models"
        self.ffmpeg_dir = self.base_dir / "ffmpeg"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup ffmpeg path
        if platform.system() == "Windows":
            self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg.exe"
            self.ffprobe_exe = self.ffmpeg_dir / "ffprobe.exe"
        else:
            self.ffmpeg_exe = self.ffmpeg_dir / "ffmpeg"
            self.ffprobe_exe = self.ffmpeg_dir / "ffprobe"
        
        # Add ffmpeg to PATH
        if self.ffmpeg_dir.exists():
            os.environ['PATH'] = str(self.ffmpeg_dir) + os.pathsep + os.environ['PATH']
        
        self.models = [
            ("tiny", WHISPER_MODELS["tiny"]["size"], WHISPER_MODELS["tiny"]["desc"]),
            ("base", WHISPER_MODELS["base"]["size"], WHISPER_MODELS["base"]["desc"]),
            ("small", WHISPER_MODELS["small"]["size"], WHISPER_MODELS["small"]["desc"]),
            ("medium", WHISPER_MODELS["medium"]["size"], WHISPER_MODELS["medium"]["desc"]),
            ("large", WHISPER_MODELS["large"]["size"], WHISPER_MODELS["large"]["desc"])
        ]
        
        self.languages = [
            ("English", "en"),
            ("Hindi", "hi"),
            ("Japanese", "ja"),
            ("Auto Detect", "auto")
        ]
        
        self.modes = [
            ("Normal Mode", "normal", "Generate subtitles from audio"),
            ("Song Mode", "song", "Enhanced lyrics with vocal separation")
        ]
        
        self.song_search_options = [
            ("Auto Detect Song", "auto", "Automatically detect song name from filename"),
            ("Manual Song Name", "manual", "Enter song name manually for accurate lyrics")
        ]
        
        self.line_types = [
            ("Words", "words", "Break by word count"),
            ("Letters", "letters", "Break by character limit"),
            ("Auto", "auto", "Auto-detect sentence breaks by audio gaps")
        ]
        
        self.selected_model = None
        self.selected_language = None
        self.selected_mode = None
        self.selected_song_search = None
        self.selected_line_type = None
        self.manual_song_name = None
        self.media_path_arg = media_path
        self.model = None
        self.temp_audio = None
        self.vocal_audio = None
        
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
                print(f"{Colors.RED}Please enter a number between {min_val} and {max_val}{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid input! Please enter a number.{Colors.RESET}")
                
    def confirm(self, prompt: str) -> bool:
        while True:
            response = self.get_input(f"{prompt} (y/n): ").lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print(f"{Colors.RED}Please enter y or n{Colors.RESET}")
            
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
            
    def get_media_path(self, allowed_extensions: List[str]) -> Path:
        if self.media_path_arg:
            path = Path(self.media_path_arg.strip('"'))
            if path.exists() and path.suffix.lower() in allowed_extensions:
                self.print_success(f"Using file: {path}")
                return path
        
        self.print_info("Opening file selection dialog...")
        self.print_info(f"Supported formats: {', '.join(allowed_extensions)}")
        file_path = select_file_dialog()
        
        if file_path:
            path = Path(file_path)
            if path.exists() and path.suffix.lower() in allowed_extensions:
                self.print_success(f"Selected: {path}")
                return path
            else:
                self.print_error("Invalid file selected!")
        
        while True:
            print(f"\n{Colors.CYAN}Provide Video/Audio Path{Colors.RESET}")
            print(f"   Supported formats: {', '.join(allowed_extensions)}")
            print(f"   Tip: You can drag and drop a file here, then press Enter")
            path_str = self.get_input("> ").strip().strip('"')
            
            if not path_str:
                self.print_error("Path cannot be empty!")
                continue
                
            path = Path(path_str)
            if not path.exists():
                self.print_error(f"File not found: {path}")
                continue
                
            if path.suffix.lower() not in allowed_extensions:
                self.print_error(f"Invalid extension! Supported: {', '.join(allowed_extensions)}")
                continue
                
            return path
            
    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        if self.ffmpeg_exe.exists():
            return True
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return True
        except:
            pass
        return False
            
    def extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video file"""
        if not self.check_ffmpeg():
            self.print_error("FFmpeg not found!")
            return None
            
        temp_dir = Path(os.environ.get('TEMP', '.'))
        audio_path = temp_dir / f"{video_path.stem}_temp_audio.wav"
        
        self.print_progress("Extracting audio from video...", 10)
        
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
                self.print_progress("Audio extracted successfully", 20)
                return audio_path
        except:
            pass
        
        return None
        
    def separate_vocals_ffmpeg(self, audio_path: Path) -> Path:
        """Separate vocals using FFmpeg filters"""
        self.print_progress("Isolating vocals from music...", 35)
        
        temp_dir = Path(os.environ.get('TEMP', '.'))
        vocal_path = temp_dir / f"{audio_path.stem}_vocals.wav"
        
        ffmpeg_cmd = str(self.ffmpeg_exe) if self.ffmpeg_exe.exists() else 'ffmpeg'
        
        # Enhanced vocal isolation using multiple filters
        cmd = [
            ffmpeg_cmd, '-i', str(audio_path),
            '-af', 'highpass=f=200, lowpass=f=8000, volume=2.0',
            '-y',
            str(vocal_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=180)
            if vocal_path.exists() and vocal_path.stat().st_size > 0:
                self.print_progress("Vocal isolation complete", 40)
                return vocal_path
        except:
            pass
        
        return audio_path
        
    def clean_lyrics_text(self, lyrics: str) -> str:
        """Remove unwanted metadata, hashtags, and promotional content from lyrics"""
        if not lyrics:
            return lyrics
            
        unwanted_patterns = [
            r'(?i)^song:.*$', r'(?i)^artist:.*$', r'(?i)^album:.*$',
            r'(?i)^copyright.*$', r'(?i)^no copyright infringement.*$',
            r'(?i)^all rights reserved.*$', r'(?i)^subscribe.*$',
            r'(?i)^like.*$', r'(?i)^comment.*$', r'(?i)^share.*$',
            r'(?i)^follow.*$', r'(?i)^instagram.*$', r'(?i)^facebook.*$',
            r'(?i)^twitter.*$', r'(?i)^tiktok.*$', r'(?i)^discord.*$',
            r'(?i)^#.*$', r'(?i)^@.*$', r'(?i)^https?://.*$',
            r'(?i)^www\..*$', r'^\s*\[\s*(?:verse|chorus|bridge|intro|outro|hook)\s*\].*$',
            r'^\s*\(\s*(?:verse|chorus|bridge|intro|outro|hook)\s*\).*$',
        ]
        
        lines = lyrics.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            should_skip = False
            for pattern in unwanted_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            if not should_skip and len(line) > 1:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
        
    def search_lyrics_online(self, song_name: str) -> Tuple[str, str]:
        """Search for lyrics online with exact matching"""
        self.print_progress(f"Searching lyrics for: {song_name}", 45)
        
        if not song_name:
            return None, None
            
        song_name = re.sub(r'[_\-\[\]\(\)]', ' ', song_name)
        song_name = re.sub(r'\s+', ' ', song_name).strip()
        
        # Method 1: Try Lyrics.ovh API first (most reliable)
        try:
            self.print_info("Trying Lyrics.ovh API...")
            # Try to extract artist from filename if format is "Artist - Song"
            parts = song_name.split('-')
            if len(parts) >= 2:
                artist = parts[0].strip()
                song = parts[1].strip()
                api_url = f"https://api.lyrics.ovh/v1/{urllib.parse.quote(artist)}/{urllib.parse.quote(song)}"
                
                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    if 'lyrics' in data and data['lyrics']:
                        lyrics = data['lyrics'].strip()
                        if len(lyrics) > 100:
                            cleaned_lyrics = self.clean_lyrics_text(lyrics)
                            self.print_progress("Found lyrics via Lyrics.ovh", 50)
                            return cleaned_lyrics, "Lyrics.ovh"
        except:
            pass
        
        # Method 2: Try Genius.com
        try:
            self.print_info("Searching Genius...")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            # Try multiple search variations
            search_variations = [
                song_name,
                song_name.replace(' ', '-'),
                song_name.replace(' ', '')
            ]
            
            for variation in search_variations[:3]:
                encoded = urllib.parse.quote(variation)
                search_url = f"https://genius.com/search?q={encoded}"
                
                req = urllib.request.Request(search_url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as response:
                    html = response.read().decode('utf-8')
                    
                    # Find song URLs
                    song_links = re.findall(r'href="([^"]*)"[^>]*>([^<]+)</a>', html)
                    
                    for link, title in song_links:
                        if song_name.lower() in title.lower() or title.lower() in song_name.lower():
                            if 'lyrics' in link:
                                song_url = link if link.startswith('http') else 'https://genius.com' + link
                                
                                req2 = urllib.request.Request(song_url, headers=headers)
                                with urllib.request.urlopen(req2, timeout=15) as response2:
                                    lyrics_html = response2.read().decode('utf-8')
                                    
                                    patterns = [
                                        r'<div[^>]*data-lyrics-container="true"[^>]*>(.*?)</div>',
                                        r'<div[^>]*class="[^"]*Lyrics__Container[^"]*"[^>]*>(.*?)</div>',
                                    ]
                                    
                                    for pattern in patterns:
                                        matches = re.findall(pattern, lyrics_html, re.DOTALL)
                                        if matches:
                                            lyrics = ' '.join(matches)
                                            lyrics = re.sub(r'<br\s*/?>', '\n', lyrics)
                                            lyrics = re.sub(r'<[^>]+>', '', lyrics)
                                            lyrics = re.sub(r'&amp;', '&', lyrics)
                                            lyrics = lyrics.strip()
                                            
                                            if len(lyrics) > 200 and not re.search(r'contributors?|reimagined|remix', lyrics.lower()):
                                                cleaned_lyrics = self.clean_lyrics_text(lyrics)
                                                if len(cleaned_lyrics) > 100:
                                                    self.print_progress("Found lyrics on Genius", 50)
                                                    return cleaned_lyrics, "Genius"
        except:
            pass
        
        # Method 3: Try AZLyrics
        try:
            self.print_info("Searching AZLyrics...")
            search_name = re.sub(r'[^\w\s]', '', song_name).lower().replace(' ', '')
            az_url = f"https://www.azlyrics.com/lyrics/{search_name}.html"
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            req = urllib.request.Request(az_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', errors='ignore')
                match = re.search(r'<!-- start of lyrics -->(.*?)<!-- end of lyrics -->', html, re.DOTALL)
                if match:
                    lyrics = match.group(1)
                    lyrics = re.sub(r'<br\s*/?>', '\n', lyrics)
                    lyrics = re.sub(r'<[^>]+>', '', lyrics)
                    lyrics = re.sub(r'&nbsp;', ' ', lyrics)
                    lyrics = lyrics.strip()
                    
                    if len(lyrics) > 200:
                        cleaned_lyrics = self.clean_lyrics_text(lyrics)
                        self.print_progress("Found lyrics on AZLyrics", 50)
                        return cleaned_lyrics, "AZLyrics"
        except:
            pass
        
        self.print_warning(f"Could not find exact lyrics for: {song_name}")
        self.print_info("Tips for better results:")
        self.print_info("  1. Use Manual Song Name with format: Artist - Song Name")
        self.print_info("  2. Example: Coldplay - Hymn for the Weekend")
        self.print_info("  3. Check spelling - the correct song is 'Hymn for the Weekend'")
        return None, None
        
    def load_model(self, model_name: str):
        try:
            import whisper
            self.print_progress(f"Loading {model_name.upper()} model...", 60)
            self.model = whisper.load_model(model_name, download_root=str(self.models_dir))
            self.print_success("Model loaded successfully")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False
            
    def transliterate_text(self, text: str, language_code: str) -> str:
        if language_code == "hi":
            hindi_map = {
                'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
                'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'am', 'अः': 'ah',
                'ऋ': 'ri', 'ॠ': 'ree', 'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
                'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nya',
                'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
                'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
                'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
                'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va', 'श': 'sha',
                'ष': 'sha', 'स': 'sa', 'ह': 'ha', 'क्ष': 'ksha', 'त्र': 'tra',
                'ज्ञ': 'gya', 'श्र': 'shra', 'ा': 'a', 'ि': 'i', 'ी': 'ee',
                'ु': 'u', 'ू': 'oo', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
                'ं': 'n', 'ः': 'h', '्': '', '०': '0', '१': '1', '२': '2',
                '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
            }
            for hindi, english in hindi_map.items():
                text = text.replace(hindi, english)
        elif language_code == "ja":
            ja_map = {
                'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
                'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
                'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
                'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
                'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
                'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
                'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
                'や': 'ya', 'ゆ': 'yu', 'よ': 'yo', 'ら': 'ra', 'り': 'ri',
                'る': 'ru', 'れ': 're', 'ろ': 'ro', 'わ': 'wa', 'を': 'wo', 'ん': 'n',
                'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o',
                'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko',
                'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so',
                'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to',
                'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no',
                'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho',
                'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo',
                'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo', 'ラ': 'ra', 'リ': 'ri',
                'ル': 'ru', 'レ': 're', 'ロ': 'ro', 'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n',
                'ゃ': 'ya', 'ゅ': 'yu', 'ょ': 'yo', 'ャ': 'ya', 'ュ': 'yu', 'ョ': 'yo',
                'っ': 't', 'ッ': 't'
            }
            for japanese, romaji in ja_map.items():
                text = text.replace(japanese, romaji)
            text = re.sub(r'([bcdfghjklmnpqrstvwxyz])\1+', r'\1\1', text)
        return text
        
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
        
    def auto_break_sentences(self, segments) -> List[dict]:
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
                subtitles.append({
                    "index": index,
                    "start": timedelta(seconds=start_time),
                    "end": timedelta(seconds=end_time),
                    "text": text
                })
                index += 1
                i += 1
            elif i < len(segments) - 1 and segments[i+1]["start"] - end_time > min_gap:
                subtitles.append({
                    "index": index,
                    "start": timedelta(seconds=start_time),
                    "end": timedelta(seconds=end_time),
                    "text": text
                })
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
                
                subtitles.append({
                    "index": index,
                    "start": timedelta(seconds=start_time),
                    "end": timedelta(seconds=merged_end),
                    "text": merged_text
                })
                index += 1
                i = j
                
        return subtitles
        
    def generate_song_lyrics(self, media_path: Path, model_name: str, language_code: str, 
                              song_search_type: str, manual_song_name: str = None) -> bool:
        try:
            import whisper
            from datetime import timedelta
            
            # Extract audio
            audio_path = media_path
            if media_path.suffix.lower() in ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm']:
                audio_path = self.extract_audio(media_path)
                if not audio_path:
                    self.print_error("Could not extract audio from video file")
                    return False
            
            # Get song name
            if song_search_type == "manual" and manual_song_name:
                song_name = manual_song_name.strip()
                self.print_info(f"Searching for: {song_name}")
            else:
                original_name = media_path.stem
                clean_name = re.sub(r'[_\-\[\]\(\)]', ' ', original_name)
                clean_name = re.sub(r'\s+', ' ', clean_name).strip()
                song_name = clean_name
                self.print_info(f"Auto-detected: {song_name}")
            
            # Search for lyrics
            online_lyrics, lyrics_source = self.search_lyrics_online(song_name)
            
            # Vocal separation
            vocal_path = self.separate_vocals_ffmpeg(audio_path)
            
            if self.model is None:
                if not self.load_model(model_name):
                    return False
                    
            self.print_progress("Transcribing audio for timing...", 70)
            
            language = language_code if language_code != "auto" else None
            
            result = self.model.transcribe(
                str(vocal_path),
                language=language,
                verbose=False,
                word_timestamps=True
            )
            
            self.print_progress("Processing lyrics...", 80)
            
            output_path = media_path.parent / f"{media_path.stem}_lyrics.srt"
            
            if online_lyrics:
                lyrics_lines = [line.strip() for line in online_lyrics.split('\n') if line.strip() and len(line.strip()) > 2]
                segments = result.get("segments", [])
                
                subtitles = []
                index = 1
                
                lyrics_lines = [line for line in lyrics_lines if not re.match(r'^[\d\W]+$', line)]
                
                total_duration = segments[-1]["end"] if segments else 0
                avg_duration = total_duration / max(len(lyrics_lines), 1)
                
                for i, line in enumerate(lyrics_lines):
                    if i < len(segments):
                        segment = segments[i]
                        start_time = segment["start"]
                        end_time = segment["end"]
                    else:
                        start_time = avg_duration * i
                        end_time = start_time + avg_duration
                    
                    text = line
                    if language_code in ["hi", "ja"]:
                        text = self.transliterate_text(text, language_code)
                    
                    subtitles.append({
                        "index": index,
                        "start": timedelta(seconds=start_time),
                        "end": timedelta(seconds=end_time),
                        "text": text
                    })
                    index += 1
            else:
                self.print_warning("No online lyrics found, using AI transcription")
                segments = result.get("segments", [])
                if language_code in ["hi", "ja"]:
                    for seg in segments:
                        seg["text"] = self.transliterate_text(seg["text"], language_code)
                subtitles = self.auto_break_sentences(segments)
            
            self.print_progress("Writing lyrics file...", 90)
            with open(output_path, 'w', encoding='utf-8') as f:
                for sub in subtitles:
                    start_str = self.format_time(sub["start"].total_seconds())
                    end_str = self.format_time(sub["end"].total_seconds())
                    f.write(f"{sub['index']}\n{start_str} --> {end_str}\n{sub['text']}\n\n")
            
            # Clean up
            if audio_path != media_path and audio_path and audio_path.exists():
                try:
                    audio_path.unlink()
                except:
                    pass
            if vocal_path != audio_path and vocal_path and vocal_path.exists():
                try:
                    vocal_path.unlink()
                except:
                    pass
            
            self.print_progress("Complete!", 100)
            print()
            
            if online_lyrics:
                self.print_success(f"Lyrics saved to: {output_path} (from {lyrics_source})")
            else:
                self.print_success(f"Lyrics saved to: {output_path} (AI-generated)")
            self.print_info(f"Generated {len(subtitles)} lyrics entries")
            return True
            
        except Exception as e:
            self.print_error(f"Error in song mode: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def generate_captions(self, media_path: Path, model_name: str, line_type: str, 
                          number_per_line: int, language_code: str) -> bool:
        try:
            import whisper
            from datetime import timedelta
            
            audio_path = media_path
            if media_path.suffix.lower() in ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm']:
                audio_path = self.extract_audio(media_path)
                if not audio_path:
                    self.print_error("Could not extract audio from video file")
                    return False
            
            if self.model is None:
                if not self.load_model(model_name):
                    return False
                    
            self.print_progress("Transcribing audio...", 70)
            
            language = language_code if language_code != "auto" else None
            
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                verbose=False,
                word_timestamps=True
            )
            
            self.print_progress("Processing transcription...", 80)
            
            output_path = media_path.parent / f"{media_path.stem}"
            if language_code != "auto":
                output_path = output_path.with_name(f"{media_path.stem}_{language_code}")
            output_path = output_path.with_suffix(".srt")
            
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
                    
                    if language_code in ["hi", "ja"]:
                        segment_text = self.transliterate_text(segment_text, language_code)
                    
                    words_data = segment.get("words", [])
                    
                    if line_type == "words" and words_data:
                        words = [w["word"].strip() for w in words_data]
                        word_starts = [w.get("start", segment_start) for w in words_data]
                        word_ends = [w.get("end", segment_end) for w in words_data]
                        
                        for i in range(0, len(words), number_per_line):
                            chunk_words = words[i:i + number_per_line]
                            line_text = " ".join(chunk_words).strip()
                            if not line_text:
                                continue
                            chunk_start = word_starts[i]
                            chunk_end = word_ends[min(i + number_per_line - 1, len(word_ends) - 1)]
                            
                            subtitles.append({
                                "index": index,
                                "start": timedelta(seconds=chunk_start),
                                "end": timedelta(seconds=chunk_end),
                                "text": line_text
                            })
                            index += 1
                    else:
                        if line_type == "letters":
                            segment_text = self.limit_letters_per_line(segment_text, number_per_line)
                        
                        subtitles.append({
                            "index": index,
                            "start": timedelta(seconds=segment_start),
                            "end": timedelta(seconds=segment_end),
                            "text": segment_text
                        })
                        index += 1
            
            self.print_progress("Writing subtitle file...", 90)
            with open(output_path, 'w', encoding='utf-8') as f:
                for sub in subtitles:
                    start_str = self.format_time(sub["start"].total_seconds())
                    end_str = self.format_time(sub["end"].total_seconds())
                    f.write(f"{sub['index']}\n{start_str} --> {end_str}\n{sub['text']}\n\n")
            
            if audio_path != media_path and audio_path and audio_path.exists():
                try:
                    audio_path.unlink()
                except:
                    pass
            
            self.print_progress("Complete!", 100)
            print()
            self.print_success(f"Captions saved to: {output_path}")
            self.print_info(f"Generated {len(subtitles)} subtitle entries")
            return True
            
        except Exception as e:
            self.print_error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def run(self):
        # Check ffmpeg
        if not self.check_ffmpeg():
            self.print_warning("FFmpeg not found! Video extraction may fail.")
        
        # Try to import whisper (handle missing torch.cuda gracefully)
        try:
            import whisper
            self.print_success("Whisper loaded successfully (CPU mode)")
        except ImportError as e:
            if 'torch.cuda' in str(e):
                self.print_warning("CUDA not available, using CPU mode")
                # Try importing again - whisper will use CPU automatically
                try:
                    import whisper
                    self.print_success("Whisper loaded successfully (CPU mode)")
                except ImportError as e2:
                    self.print_error(f"Whisper import failed: {e2}")
                    self.print_info("Please install: pip install openai-whisper torch numpy")
                    input("\nPress Enter to exit...")
                    return
            else:
                self.print_error(f"Whisper import failed: {e}")
                self.print_info("Please install: pip install openai-whisper torch numpy")
                input("\nPress Enter to exit...")
                return
            
        while True:
            try:
                self.clear_screen()
                print_header()
                print(f"\n{Colors.CYAN}Supported Formats:{Colors.RESET}")
                print(f"  Video: {', '.join(SUPPORTED_EXTENSIONS['video'])}")
                print(f"  Audio: {', '.join(SUPPORTED_EXTENSIONS['audio'])}")
                print()
                
                allowed_extensions = SUPPORTED_EXTENSIONS['all']
                media_path = self.get_media_path(allowed_extensions)
                self.print_success(f"Selected: {media_path}")
                
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}\n")
                
                model_options = [f"{m[0].upper()} ({m[1]}) - {m[2]}" for m in self.models]
                model_choice = self.show_menu("SELECT MODEL", model_options)
                if model_choice == -1:
                    continue
                self.selected_model = self.models[model_choice][0]
                
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}\n")
                
                lang_options = [f"{lang[0]} ({lang[1]})" for lang in self.languages]
                lang_choice = self.show_menu("SELECT LANGUAGE", lang_options)
                if lang_choice == -1:
                    continue
                self.selected_language = self.languages[lang_choice]
                language_code = self.selected_language[1]
                language_name = self.selected_language[0]
                
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}\n")
                
                mode_options = [f"{m[0]} - {m[2]}" for m in self.modes]
                mode_choice = self.show_menu("SELECT MODE", mode_options)
                if mode_choice == -1:
                    continue
                    
                self.selected_mode = self.modes[mode_choice]
                mode = self.selected_mode[1]
                
                if mode == "song":
                    self.clear_screen()
                    print_header()
                    print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}")
                    print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                    print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}\n")
                    
                    song_options = [f"{s[0]} - {s[2]}" for s in self.song_search_options]
                    song_choice = self.show_menu("SONG SEARCH OPTION", song_options)
                    if song_choice == -1:
                        continue
                    
                    self.selected_song_search = self.song_search_options[song_choice]
                    song_search_type = self.selected_song_search[1]
                    
                    manual_song_name = None
                    if song_search_type == "manual":
                        print(f"\n{Colors.CYAN}Enter song name (e.g., Artist - Song Name):{Colors.RESET}")
                        manual_song_name = self.get_input("> ").strip()
                        if not manual_song_name:
                            self.print_error("Song name cannot be empty!")
                            continue
                    
                    self.clear_screen()
                    print_header()
                    search_display = "Auto Detect" if song_search_type == "auto" else f"Manual: {manual_song_name}"
                    self.print_box([
                        f"Media File: {media_path}",
                        f"Model: {self.selected_model.upper()}",
                        f"Language: {language_name}",
                        f"Mode: SONG MODE",
                        f"Search: {search_display}"
                    ])
                    
                    if not self.confirm("Generate lyrics?"):
                        continue
                    
                    self.print_info("Generating lyrics with vocal separation...")
                    success = self.generate_song_lyrics(
                        media_path,
                        self.selected_model,
                        language_code,
                        song_search_type,
                        manual_song_name
                    )
                else:
                    self.clear_screen()
                    print_header()
                    print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}")
                    print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                    print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}")
                    print(f"{Colors.GREEN}Mode: {self.selected_mode[0]}{Colors.RESET}\n")
                    
                    line_options = [f"{l[0]} - {l[2]}" for l in self.line_types]
                    line_choice = self.show_menu("LINE TYPE", line_options)
                    if line_choice == -1:
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
                        f"Media File: {media_path}",
                        f"Model: {self.selected_model.upper()}",
                        f"Language: {language_name}",
                        f"Mode: {self.selected_mode[0]}",
                        f"Line Type: {self.selected_line_type[0]}",
                        f"Settings: {number_per_line if line_type != 'auto' else 'Auto-detect'}"
                    ])
                    
                    if not self.confirm("Generate captions?"):
                        continue
                    
                    self.print_info("Generating captions... This may take several minutes.")
                    success = self.generate_captions(
                        media_path,
                        self.selected_model,
                        line_type,
                        number_per_line,
                        language_code
                    )
                
                if success:
                    self.print_success(f"Thanks for using {APP_NAME}!")
                    self.print_success("Your caption has been generated successfully!")
                    
                    try:
                        webbrowser.open(APP_TELEGRAM)
                        webbrowser.open(APP_YOUTUBE)
                    except:
                        pass
                    
                    if not self.confirm("Process another file?"):
                        break
                else:
                    self.print_error("Failed to generate captions")
                    if not self.confirm("Try again?"):
                        continue
                        
            except KeyboardInterrupt:
                print("\n")
                self.print_warning("Interrupted by user")
                break
            except Exception as e:
                self.print_error(f"Unexpected error: {e}")
                if not self.confirm("Continue?"):
                    break
                    
        self.clear_screen()
        print_header("Thank You!")
        self.print_success(f"Thanks for using {APP_NAME}!")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'{APP_NAME} - {APP_AUTHOR}')
    parser.add_argument('file', nargs='?', help='Video/Audio file to process')
    args = parser.parse_args()
    
    app = NotYCaptionGenerator(args.file)
    app.run()