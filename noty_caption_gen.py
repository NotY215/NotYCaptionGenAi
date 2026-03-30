#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NotY Caption Generator AI v4.4
Using OpenAI Whisper (PyTorch)
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
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BLACK = '\033[40m'

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
APP_VERSION = "4.4"
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

class NotYCaptionGenerator:
    def __init__(self, media_path: str = None):
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
            
        self.models_dir = self.base_dir / "models"
        self.resources_dir = self.base_dir / "resources"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.resources_dir.mkdir(parents=True, exist_ok=True)
        
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
            ("Normal", "normal", "Generate subtitles in selected language"),
            ("Translate to English", "translate", "Translate any language to English"),
            ("Transliteration", "transliterate", "Convert Hindi/Japanese to English/Romanized text")
        ]
        
        self.selected_model = None
        self.selected_language = None
        self.selected_mode = None
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
            
    def load_model(self, model_name: str):
        try:
            import whisper
            self.print_info(f"Loading {model_name.upper()} model...")
            self.model = whisper.load_model(model_name, download_root=str(self.models_dir))
            self.print_success("Model loaded successfully")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False
            
    def transliterate_text(self, text: str, language_code: str) -> str:
        """Simple transliteration for Hindi and Japanese"""
        if language_code == "hi":
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
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def limit_letters_per_line(self, text: str, max_letters: int) -> str:
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
        
    def generate_captions(self, media_path: Path, model_name: str, line_type: str, 
                          number_per_line: int, language_code: str, mode: str) -> bool:
        try:
            import whisper
            
            if self.model is None:
                if not self.load_model(model_name):
                    return False
                    
            self.print_info("Transcribing audio...")
            
            task = "translate" if mode == "translate" else "transcribe"
            language = language_code if language_code != "auto" else None
            
            result = self.model.transcribe(
                str(media_path),
                task=task,
                language=language,
                verbose=False,
                word_timestamps=True
            )
            
            # Determine output filename
            output_path = media_path.parent / f"{media_path.stem}"
            if mode == "translate":
                output_path = output_path.with_name(f"{media_path.stem}_en")
            elif language_code != "auto":
                output_path = output_path.with_name(f"{media_path.stem}_{language_code}")
            output_path = output_path.with_suffix(".srt")
            
            subtitle_index = 1
            MIN_DURATION = 0.5  # Minimum 0.5 seconds per subtitle
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for segment in result["segments"]:
                    text = segment["text"].strip()
                    
                    # Apply transliteration if needed
                    if mode == "transliterate":
                        text = self.transliterate_text(text, language_code)
                    
                    if line_type == "words":
                        words = segment.get("words", [])
                        if words:
                            for i in range(0, len(words), number_per_line):
                                chunk = words[i:i + number_per_line]
                                if chunk:
                                    start_time = chunk[0]["start"]
                                    end_time = chunk[-1]["end"]
                                    
                                    # Ensure minimum duration
                                    if end_time - start_time < MIN_DURATION:
                                        end_time = start_time + MIN_DURATION
                                    
                                    chunk_text = " ".join([w["word"].strip() for w in chunk])
                                    start_str = self.format_time(start_time)
                                    end_str = self.format_time(end_time)
                                    f.write(f"{subtitle_index}\n{start_str} --> {end_str}\n{chunk_text}\n\n")
                                    subtitle_index += 1
                        else:
                            # Fallback: use segment timestamps
                            words_list = text.split()
                            if len(words_list) == 0:
                                continue
                                
                            # Calculate duration per word
                            segment_duration = segment["end"] - segment["start"]
                            duration_per_word = segment_duration / len(words_list)
                            
                            for i in range(0, len(words_list), number_per_line):
                                chunk = words_list[i:i + number_per_line]
                                chunk_text = " ".join(chunk)
                                start_time = segment["start"] + (i * duration_per_word)
                                end_time = segment["start"] + ((i + len(chunk)) * duration_per_word)
                                
                                # Ensure minimum duration
                                if end_time - start_time < MIN_DURATION:
                                    end_time = start_time + MIN_DURATION
                                
                                start_str = self.format_time(start_time)
                                end_str = self.format_time(end_time)
                                f.write(f"{subtitle_index}\n{start_str} --> {end_str}\n{chunk_text}\n\n")
                                subtitle_index += 1
                    else:
                        # Letters per line - use segment timestamps
                        formatted_text = self.limit_letters_per_line(text, number_per_line)
                        start_time = segment["start"]
                        end_time = segment["end"]
                        
                        # Ensure minimum duration
                        if end_time - start_time < MIN_DURATION:
                            end_time = start_time + MIN_DURATION
                        
                        start_str = self.format_time(start_time)
                        end_str = self.format_time(end_time)
                        f.write(f"{subtitle_index}\n{start_str} --> {end_str}\n{formatted_text}\n\n")
                        subtitle_index += 1
                    
            self.print_success(f"Captions saved to: {output_path}")
            self.print_info(f"Generated {subtitle_index - 1} subtitle entries")
            return True
            
        except Exception as e:
            self.print_error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def run(self):
        # Try to import whisper to verify it works
        try:
            import whisper
            self.print_success("Whisper loaded successfully")
        except ImportError as e:
            self.print_error(f"Whisper import failed: {e}")
            self.print_info("Please ensure openai-whisper is installed")
            input("\nPress Enter to exit...")
            return
            
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
                
                # Select mode (only show appropriate modes based on language)
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}\n")
                
                mode_options = []
                if language_name in ["Hindi", "Japanese"]:
                    mode_options = [f"{m[0]} - {m[2]}" for m in self.modes]
                else:
                    mode_options = [f"{self.modes[0][0]} - {self.modes[0][2]}", f"{self.modes[1][0]} - {self.modes[1][2]}"]
                
                mode_choice = self.show_menu("SELECT MODE", mode_options)
                if mode_choice == -1:
                    continue
                    
                if language_name in ["Hindi", "Japanese"]:
                    self.selected_mode = self.modes[mode_choice]
                else:
                    self.selected_mode = self.modes[mode_choice]
                mode = self.selected_mode[1]
                
                # Choose line preference
                self.clear_screen()
                print_header()
                print(f"\n{Colors.BOLD}File: {media_path.name}{Colors.RESET}")
                print(f"{Colors.GREEN}Model: {self.selected_model.upper()}{Colors.RESET}")
                print(f"{Colors.GREEN}Language: {language_name}{Colors.RESET}")
                print(f"{Colors.GREEN}Mode: {self.selected_mode[0]}{Colors.RESET}\n")
                
                line_options = ["Words", "Letters"]
                line_choice = self.show_menu("LINE PREFERENCE", line_options)
                if line_choice == -1:
                    continue
                line_type = "words" if line_choice == 0 else "letters"
                
                number_per_line = self.get_number_input(
                    f"How many {line_type} per line? (1-30): ", 1, 30
                )
                
                # Confirm and generate
                self.clear_screen()
                print_header()
                self.print_box([
                    f"Media File: {media_path}",
                    f"Model: {self.selected_model.upper()}",
                    f"Language: {language_name}",
                    f"Mode: {self.selected_mode[0]}",
                    f"Line Type: {line_type}",
                    f"{line_type.title()} per line: {number_per_line}"
                ])
                
                if not self.confirm("Generate captions?"):
                    continue
                
                self.print_info("Generating captions... This may take several minutes.")
                success = self.generate_captions(
                    media_path,
                    self.selected_model,
                    line_type,
                    number_per_line,
                    language_code,
                    mode
                )
                
                if success:
                    self.print_success(f"Thanks for using {APP_NAME}!")
                    self.print_success("Your caption has been generated successfully!")
                    
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