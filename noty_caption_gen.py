#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NotY Caption Generator AI v4.4
Using pywhispercpp (Whisper.cpp bindings)
Copyright (c) 2026 NotY215
"""

import os
import sys
import webbrowser
import time
import platform
import argparse
import subprocess
import importlib.util
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import List, Tuple, Optional

# Fix Windows console encoding
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# ANSI color codes without emojis for Windows compatibility
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
    except ImportError:
        # If colorama not installed, disable colors
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
            ("Video Files", "*.mp4;*.avi;*.mkv;*.mov;*.m4v;*.mpg;*.mpeg"),
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
        print(f"{Colors.RED}X Could not open file dialog: {e}{Colors.RESET}")
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
    print("|" + "Powered by Whisper.cpp".center(58) + "|")
    print("+" + "=" * 58 + "+")
    print(f"{Colors.RESET}")

# Application metadata
APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "4.4"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"
APP_LICENSE = "LGPL-3.0"
APP_TELEGRAM = "https://t.me/Noty_215"
APP_YOUTUBE = "https://www.youtube.com/@NotY215"

# Whisper models with correct URLs
WHISPER_MODELS = {
    "tiny": {
        "size": "75 MB",
        "desc": "Fastest",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin"
    },
    "base": {
        "size": "150 MB",
        "desc": "Balanced",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"
    },
    "small": {
        "size": "500 MB",
        "desc": "Good",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
    },
    "medium": {
        "size": "1.5 GB",
        "desc": "Accurate",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"
    },
    "large": {
        "size": "2.9 GB",
        "desc": "Best",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large.bin"
    }
}

class NotYCaptionGenerator:
    def __init__(self, media_path: str = None):
        # Get application directory
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
            
        self.models_dir = self.base_dir / "models"
        self.resources_dir = self.base_dir / "resources"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.resources_dir.mkdir(parents=True, exist_ok=True)
        
        # Models list for display
        self.models = [
            ("tiny", WHISPER_MODELS["tiny"]["size"], WHISPER_MODELS["tiny"]["desc"]),
            ("base", WHISPER_MODELS["base"]["size"], WHISPER_MODELS["base"]["desc"]),
            ("small", WHISPER_MODELS["small"]["size"], WHISPER_MODELS["small"]["desc"]),
            ("medium", WHISPER_MODELS["medium"]["size"], WHISPER_MODELS["medium"]["desc"]),
            ("large", WHISPER_MODELS["large"]["size"], WHISPER_MODELS["large"]["desc"])
        ]
        
        # Language options
        self.languages = [
            ("English", "en"),
            ("Hindi", "hi"),
            ("Japanese", "ja"),
            ("Auto Detect", "auto")
        ]
        
        self.selected_model = None
        self.selected_language = None
        self.media_path_arg = media_path
        self.model = None
        
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
            
    def check_model_exists(self, model_name: str) -> bool:
        """Check if model exists in models directory"""
        model_path = self.models_dir / f"ggml-{model_name}.bin"
        return model_path.exists()
        
    def download_model(self, model_name: str):
        """Download model from URL"""
        import requests
        model_info = WHISPER_MODELS[model_name]
        model_url = model_info["url"]
        model_path = self.models_dir / f"ggml-{model_name}.bin"
        
        self.print_info(f"Downloading {model_name.upper()} model...")
        self.print_info(f"URL: {model_url}")
        self.print_info(f"Size: {model_info['size']}")
        
        try:
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r  Progress: {percent:.1f}%", end="", flush=True)
            
            print()  # New line
            self.print_success(f"Model downloaded: {model_path}")
            return True
        except Exception as e:
            self.print_error(f"Failed to download model: {e}")
            return False
            
    def get_model_path(self, model_name: str) -> Path:
        """Get path to model file"""
        return self.models_dir / f"ggml-{model_name}.bin"
        
    def load_model(self, model_name: str):
        """Load model using pywhispercpp"""
        try:
            from pywhispercpp.model import Model
            
            model_path = self.get_model_path(model_name)
            if not model_path.exists():
                self.print_error(f"Model not found: {model_path}")
                return False
                
            self.print_info(f"Loading {model_name.upper()} model...")
            self.model = Model(str(model_path), n_threads=4)
            self.print_success("Model loaded successfully")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False
            
    def generate_captions(self, media_path: Path, model_name: str, line_type: str, 
                          number_per_line: int, language_code: str) -> bool:
        """Generate captions using pywhispercpp with proper segment handling"""
        try:
            if self.model is None:
                if not self.load_model(model_name):
                    return False
                    
            self.print_info("Transcribing audio...")
            self.print_info("This may take a few minutes...")
            
            # Set language (None for auto-detect)
            lang = None if language_code == "auto" else language_code
            
            # Transcribe with proper parameters
            segments = self.model.transcribe(
                str(media_path),
                language=lang,
                print_progress=True,
                print_special=False,
                print_realtime=False,
                print_timestamps=True,
                max_len=0,  # No maximum length
                best_of=5,  # Better accuracy
                beam_size=5  # Beam search for better accuracy
            )
            
            # Determine output filename
            output_path = media_path.parent / f"{media_path.stem}"
            if language_code != "auto":
                output_path = output_path.with_name(f"{media_path.stem}_{language_code}")
            output_path = output_path.with_suffix(".srt")
            
            subtitle_index = 1
            segment_count = 0
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for segment in segments:
                    # Get segment text
                    text = segment.text.strip()
                    if not text:
                        continue
                    
                    segment_count += 1
                    
                    # Apply transliteration for Hindi/Japanese if needed
                    if language_code in ["hi", "ja"]:
                        text = self.transliterate_text(text, language_code)
                    
                    # Get timestamps
                    start_time = segment.start if hasattr(segment, 'start') else 0
                    end_time = segment.end if hasattr(segment, 'end') else start_time + 1
                    
                    if line_type == "words":
                        # Split into words
                        words_list = text.split()
                        words_per_line = number_per_line
                        word_count = len(words_list)
                        
                        if word_count == 0:
                            continue
                        
                        # Group words into chunks
                        for i in range(0, word_count, words_per_line):
                            chunk_words = words_list[i:i + words_per_line]
                            chunk_text = " ".join(chunk_words)
                            
                            # Calculate approximate timestamps for word groups
                            chunk_start = start_time + (i / word_count) * (end_time - start_time)
                            chunk_end = start_time + ((i + len(chunk_words)) / word_count) * (end_time - start_time)
                            
                            start_str = self.format_time(chunk_start)
                            end_str = self.format_time(chunk_end)
                            f.write(f"{subtitle_index}\n{start_str} --> {end_str}\n{chunk_text}\n\n")
                            subtitle_index += 1
                    else:
                        # Letters per line
                        formatted_text = self.limit_letters_per_line(text, number_per_line)
                        start_str = self.format_time(start_time)
                        end_str = self.format_time(end_time)
                        f.write(f"{subtitle_index}\n{start_str} --> {end_str}\n{formatted_text}\n\n")
                        subtitle_index += 1
                    
                    # Show progress every 10 segments
                    if segment_count % 10 == 0:
                        print(f"  Processed {segment_count} segments...", flush=True)
                    
            if segment_count == 0:
                self.print_error("No segments were transcribed! Check if audio is valid.")
                return False
                
            self.print_success(f"Captions saved to: {output_path}")
            self.print_info(f"Generated {subtitle_index - 1} subtitle entries from {segment_count} segments")
            return True
            
        except Exception as e:
            self.print_error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def transliterate_text(self, text: str, language_code: str) -> str:
        """Simple transliteration for Hindi and Japanese"""
        if language_code == "hi":
            # Simple Hindi to English transliteration mapping
            hindi_map = {
                'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
                'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'am', 'अः': 'ah',
                'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
                'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nya',
                'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
                'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
                'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
                'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va', 'श': 'sha',
                'ष': 'sha', 'स': 'sa', 'ह': 'ha', 'क्ष': 'ksha', 'त्र': 'tra',
                'ज्ञ': 'gya', 'ॐ': 'om'
            }
            for hindi, english in hindi_map.items():
                text = text.replace(hindi, english)
        elif language_code == "ja":
            # Simple Japanese to Romaji mapping (basic)
            ja_map = {
                'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
                'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
                'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
                'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
                'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
                'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
                'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
                'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
                'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
                'わ': 'wa', 'を': 'wo', 'ん': 'n'
            }
            for japanese, romaji in ja_map.items():
                text = text.replace(japanese, romaji)
        return text
            
    def format_time(self, seconds: float) -> str:
        """Format time for SRT subtitle"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def limit_letters_per_line(self, text: str, max_letters: int) -> str:
        """Limit text to max letters per line"""
        if max_letters <= 0:
            return text
        if len(text) <= max_letters:
            return text
        lines = []
        current_line = ""
        current_length = 0
        words = text.split()
        for word in words:
            word_length = len(word)
            if current_length + word_length + (1 if current_line else 0) > max_letters:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                    current_length = word_length
                else:
                    lines.append(word)
                    current_line = ""
                    current_length = 0
            else:
                if current_line:
                    current_line += " " + word
                    current_length += word_length + 1
                else:
                    current_line = word
                    current_length = word_length
        if current_line:
            lines.append(current_line)
        return '\n'.join(lines)
        
    def get_media_path(self, allowed_extensions: List[str]) -> Path:
        """Get media file path from user"""
        # If media path was provided via command line, use it
        if self.media_path_arg:
            path = Path(self.media_path_arg.strip('"'))
            if path.exists() and path.suffix.lower() in allowed_extensions:
                self.print_success(f"Using file: {path}")
                return path
        
        # Use file dialog to select file
        self.print_info("Opening file selection dialog...")
        file_path = select_file_dialog()
        
        if file_path:
            path = Path(file_path)
            if path.exists() and path.suffix.lower() in allowed_extensions:
                self.print_success(f"Selected: {path}")
                return path
            else:
                self.print_error("Invalid file selected!")
        
        # Fallback to manual input
        while True:
            print(f"\n{Colors.CYAN}Provide Video/Audio Path{Colors.RESET}")
            print(f"   Allowed extensions: {', '.join(allowed_extensions)}")
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
                self.print_error(f"Invalid extension! Allowed: {', '.join(allowed_extensions)}")
                continue
                
            return path
            
    def show_menu(self, title: str, options: List[str]) -> int:
        """Show a menu and return selected index"""
        while True:
            print(f"\n{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
            print(f"{Colors.CYAN}┌{'─' * 50}┐{Colors.RESET}")
            for i, option in enumerate(options, 1):
                print(f"{Colors.CYAN}│{Colors.RESET} {i:2}) {option:<45} {Colors.CYAN}│{Colors.RESET}")
            print(f"{Colors.CYAN}│{Colors.RESET}  0) Back{' ' * 45}{Colors.CYAN}│{Colors.RESET}")
            print(f"{Colors.CYAN}└{'─' * 50}┘{Colors.RESET}")
            
            choice = self.get_number_input(f"➤ Choose option (0-{len(options)}): ", 0, len(options))
            if choice == 0:
                return -1
            return choice - 1
            
    def run(self):
        """Main application loop"""
        while True:
            try:
                allowed_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.m4a', '.flac', '.webm', '.m4v', '.mpg', '.mpeg']
                media_path = self.get_media_path(allowed_extensions)
                self.print_success(f"Selected: {media_path}")
                
                # Select model
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}\n")
                
                model_options = [f"{m[0].upper()} ({m[1]}) - {m[2]}" for m in self.models]
                model_choice = self.show_menu("SELECT MODEL", model_options)
                if model_choice == -1:
                    continue
                    
                self.selected_model = self.models[model_choice][0]
                
                # Check if model exists, download if not
                if not self.check_model_exists(self.selected_model):
                    self.print_warning(f"{self.selected_model.upper()} model not found!")
                    if self.confirm("Download model now?"):
                        if not self.download_model(self.selected_model):
                            continue
                    else:
                        continue
                
                # Select language
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
                
                # Choose line preference
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}\n")
                
                line_options = ["Words", "Letters"]
                line_choice = self.show_menu("LINE PREFERENCE", line_options)
                if line_choice == -1:
                    continue
                line_type = "words" if line_choice == 0 else "letters"
                
                # Number per line
                number_per_line = self.get_number_input(
                    f"How many {line_type} per line? (1-30): ", 1, 30
                )
                
                # Confirm and generate
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}File: {media_path}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}")
                print(f"Line Type: {line_type}")
                print(f"{line_type.title()} per line: {number_per_line}\n")
                
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
                    
                    # Open links
                    try:
                        webbrowser.open(APP_TELEGRAM)
                        webbrowser.open(APP_YOUTUBE)
                    except:
                        pass
                    
                    if not self.confirm("Process another video?"):
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
                import traceback
                traceback.print_exc()
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