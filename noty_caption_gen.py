#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NotY Caption Generator AI v4.3
Using OpenAI Whisper (PyTorch .pt models)
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
from pathlib import Path
from typing import List, Tuple, Optional

# Fix Windows console encoding
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# Check and install dependencies
def check_and_install_dependencies():
    """Check if required packages are installed, install if missing"""
    required_packages = {
        'whisper': 'openai-whisper',
        'torch': 'torch',
        'numpy': 'numpy',
        'colorama': 'colorama'
    }
    
    missing_packages = []
    for module, package in required_packages.items():
        if importlib.util.find_spec(module) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"{Colors.YELLOW}⚠ Missing required packages: {', '.join(missing_packages)}{Colors.RESET}")
        print(f"{Colors.CYAN}ℹ Installing dependencies...{Colors.RESET}")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"{Colors.GREEN}✓ Installed: {package}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}✗ Failed to install {package}: {e}{Colors.RESET}")
                return False
        
        print(f"{Colors.GREEN}✓ All dependencies installed!{Colors.RESET}")
        return True
    
    return True

# Try to import whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# Application metadata
APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "4.3"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"
APP_LICENSE = "LGPL-3.0"
APP_TELEGRAM = "https://t.me/NotY215"
APP_YOUTUBE = "https://www.youtube.com/@NotY215"

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
    except ImportError:
        Colors.RESET = ''
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.CYAN = ''
        Colors.BOLD = ''

def draw_turtle_logo():
    """Draw a colorful turtle logo in console"""
    turtle_art = f"""
{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}
                    ╔═══════════════════════════════════════════════════╗
                    ║                    🐢 NOTY AI 🐢                   ║
                    ║         The Fastest Subtitle Generator           ║
                    ║            Copyright (c) 2026 NotY215            ║
                    ╚═══════════════════════════════════════════════════╝
{Colors.RESET}

{Colors.CYAN}    ╔═══════════════════════════════════════════════════════════════════╗
    ║                           TURTLE POWER!                            ║
    ╚═══════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.GREEN}          ▄▄▄▄▄▄▄▄▄▄▄  {Colors.YELLOW}▄▄▄▄▄▄▄▄▄▄▄  {Colors.RED}▄▄▄▄▄▄▄▄▄▄▄  {Colors.BLUE}▄▄▄▄▄▄▄▄▄▄▄{Colors.RESET}
{Colors.GREEN}         █{Colors.WHITE}░░░░░░░░░{Colors.GREEN}█{Colors.YELLOW}█{Colors.WHITE}░░░░░░░░░{Colors.YELLOW}█{Colors.RED}█{Colors.WHITE}░░░░░░░░░{Colors.RED}█{Colors.BLUE}█{Colors.WHITE}░░░░░░░░░{Colors.BLUE}█{Colors.RESET}
{Colors.GREEN}         █{Colors.WHITE}░░░░░░░░░{Colors.GREEN}█{Colors.YELLOW}█{Colors.WHITE}░░░░░░░░░{Colors.YELLOW}█{Colors.RED}█{Colors.WHITE}░░░░░░░░░{Colors.RED}█{Colors.BLUE}█{Colors.WHITE}░░░░░░░░░{Colors.BLUE}█{Colors.RESET}
{Colors.GREEN}         █{Colors.WHITE}░░░░░░░░░{Colors.GREEN}█{Colors.YELLOW}█{Colors.WHITE}░░░░░░░░░{Colors.YELLOW}█{Colors.RED}█{Colors.WHITE}░░░░░░░░░{Colors.RED}█{Colors.BLUE}█{Colors.WHITE}░░░░░░░░░{Colors.BLUE}█{Colors.RESET}
{Colors.GREEN}         █{Colors.WHITE}░░░░░░░░░{Colors.GREEN}█{Colors.YELLOW}█{Colors.WHITE}░░░░░░░░░{Colors.YELLOW}█{Colors.RED}█{Colors.WHITE}░░░░░░░░░{Colors.RED}█{Colors.BLUE}█{Colors.WHITE}░░░░░░░░░{Colors.BLUE}█{Colors.RESET}
{Colors.GREEN}         █{Colors.WHITE}░░░░░░░░░{Colors.GREEN}█{Colors.YELLOW}█{Colors.WHITE}░░░░░░░░░{Colors.YELLOW}█{Colors.RED}█{Colors.WHITE}░░░░░░░░░{Colors.RED}█{Colors.BLUE}█{Colors.WHITE}░░░░░░░░░{Colors.BLUE}█{Colors.RESET}
{Colors.GREEN}         █{Colors.WHITE}░░░░░░░░░{Colors.GREEN}█{Colors.YELLOW}█{Colors.WHITE}░░░░░░░░░{Colors.YELLOW}█{Colors.RED}█{Colors.WHITE}░░░░░░░░░{Colors.RED}█{Colors.BLUE}█{Colors.WHITE}░░░░░░░░░{Colors.BLUE}█{Colors.RESET}
{Colors.GREEN}          ▀▀▀▀▀▀▀▀▀▀▀  {Colors.YELLOW}▀▀▀▀▀▀▀▀▀▀▀  {Colors.RED}▀▀▀▀▀▀▀▀▀▀▀  {Colors.BLUE}▀▀▀▀▀▀▀▀▀▀▀{Colors.RESET}
{Colors.RESET}
{Colors.PURPLE}              ╔══════════════════════════════════════════╗
              ║     🚀 AI-POWERED SUBTITLE GENERATION 🚀      ║
              ╚══════════════════════════════════════════════╝{Colors.RESET}
"""
    print(turtle_art)

# Whisper models with correct OpenAI URLs
WHISPER_MODELS = {
    "tiny": {
        "size": "75 MB",
        "desc": "Fastest",
        "url": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt"
    },
    "base": {
        "size": "150 MB",
        "desc": "Balanced",
        "url": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt"
    },
    "small": {
        "size": "500 MB",
        "desc": "Good",
        "url": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt"
    },
    "medium": {
        "size": "1.5 GB",
        "desc": "Accurate",
        "url": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674b08dcb1/medium.pt"
    },
    "large-v3": {
        "size": "2.9 GB",
        "desc": "Best",
        "url": "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt"
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
        self.files_dir = self.base_dir / "files"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        
        # Models list for display
        self.models = [
            ("tiny", WHISPER_MODELS["tiny"]["size"], WHISPER_MODELS["tiny"]["desc"]),
            ("base", WHISPER_MODELS["base"]["size"], WHISPER_MODELS["base"]["desc"]),
            ("small", WHISPER_MODELS["small"]["size"], WHISPER_MODELS["small"]["desc"]),
            ("medium", WHISPER_MODELS["medium"]["size"], WHISPER_MODELS["medium"]["desc"]),
            ("large-v3", WHISPER_MODELS["large-v3"]["size"], WHISPER_MODELS["large-v3"]["desc"])
        ]
        
        # Language options
        self.languages = [
            ("English", "en"),
            ("Hindi", "hi"),
            ("Japanese", "ja"),
            ("Chinese", "zh"),
            ("Urdu", "ur")
        ]
        
        self.selected_model = None
        self.selected_language = None
        self.language_code = "auto"
        self.language_name = "Auto Detect"
        self.media_path_arg = media_path
        self.model = None
        
    def clear_screen(self):
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
    def print_header(self, title: str = None):
        if title is None:
            title = f"{APP_NAME} v{APP_VERSION}"
        draw_turtle_logo()
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔" + "═" * 58 + "╗")
        print("║" + title.center(58) + "║")
        print("║" + f"Copyright (c) {APP_YEAR} {APP_AUTHOR}".center(58) + "║")
        print("║" + f"License: {APP_LICENSE}".center(58) + "║")
        print("║" + "Powered by OpenAI Whisper (.pt models)".center(58) + "║")
        print("╚" + "═" * 58 + "╝")
        print(f"{Colors.RESET}")
        
    def print_success(self, message: str):
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")
        
    def print_error(self, message: str):
        print(f"{Colors.RED}✗ {message}{Colors.RESET}")
        
    def print_warning(self, message: str):
        print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")
        
    def print_info(self, message: str):
        print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")
        
    def print_box(self, lines: List[str]):
        width = max(len(line) for line in lines) + 4
        print(f"{Colors.GREEN}")
        print("┌" + "─" * (width - 2) + "┐")
        for line in lines:
            print(f"│ {line.ljust(width - 4)} │")
        print("└" + "─" * (width - 2) + "┘")
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
            
            choice = self.get_number_input("➤ Choose option (0-{}): ".format(len(options)), 0, len(options))
            if choice == 0:
                return -1
            return choice - 1
            
    def get_media_path(self, allowed_extensions: List[str]) -> Path:
        if self.media_path_arg:
            path = Path(self.media_path_arg.strip('"'))
            if path.exists() and path.suffix.lower() in allowed_extensions:
                self.print_success(f"Using file: {path}")
                return path
                
        while True:
            print(f"\n{Colors.CYAN}📂 Provide Video/Audio Path{Colors.RESET}")
            print(f"   Allowed extensions: {', '.join(allowed_extensions)}")
            print(f"   Tip: You can drag and drop a file here, then press Enter")
            path_str = self.get_input("➤ ").strip().strip('"')
            
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
            
    def check_whisper_available(self) -> bool:
        global WHISPER_AVAILABLE
        if not WHISPER_AVAILABLE:
            self.print_error("OpenAI Whisper not installed!")
            self.print_info("Installing dependencies automatically...")
            
            if check_and_install_dependencies():
                # Reload whisper module
                import importlib
                try:
                    global whisper
                    whisper = importlib.import_module('whisper')
                    WHISPER_AVAILABLE = True
                    self.print_success("Dependencies installed successfully!")
                    return True
                except ImportError:
                    self.print_error("Failed to load Whisper after installation")
                    return False
            else:
                return False
        return True
        
    def check_model_exists(self, model_name: str) -> bool:
        model_path = self.models_dir / f"{model_name}.pt"
        if model_path.exists():
            return True
        # Check for existing model files
        for f in self.models_dir.glob("*.pt"):
            if f.stem == model_name or model_name in f.stem:
                return True
        return False
        
    def get_model_path(self, model_name: str) -> Path:
        # Check for exact match
        exact_path = self.models_dir / f"{model_name}.pt"
        if exact_path.exists():
            return exact_path
        # Check for partial match
        for f in self.models_dir.glob("*.pt"):
            if model_name in f.stem:
                return f
        return self.models_dir / f"{model_name}.pt"
        
    def load_model(self, model_name: str):
        model_info = WHISPER_MODELS[model_name]
        self.print_info(f"Loading {model_name.upper()} model (.pt format)...")
        self.print_info(f"Size: {model_info['size']}")
        try:
            self.model = whisper.load_model(model_name, download_root=str(self.models_dir))
            self.print_success(f"Model loaded successfully")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            return False
            
    def format_subtitle_text(self, text: str, line_type: str, number_per_line: int) -> str:
        if not text:
            return text
        if line_type == "words":
            return self.limit_words_per_line(text, number_per_line)
        else:
            return self.limit_letters_per_line(text, number_per_line)
    
    def limit_words_per_line(self, text: str, max_words: int) -> str:
        if max_words <= 0:
            return text
        words = text.split()
        if len(words) <= max_words:
            return text
        lines = []
        for i in range(0, len(words), max_words):
            line_words = words[i:i + max_words]
            lines.append(' '.join(line_words))
        return '\n'.join(lines)
    
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
                          number_per_line: int, mode: int, language_code: str) -> bool:
        try:
            if self.model is None:
                if not self.load_model(model_name):
                    return False
                    
            self.print_info("Transcribing audio... This may take several minutes.")
            
            task = "transcribe"
            if mode == 2:
                task = "translate"
            language = language_code if language_code != "auto" else None
            
            result = self.model.transcribe(
                str(media_path),
                task=task,
                language=language,
                verbose=False,
                word_timestamps=True
            )
            
            output_path = media_path.parent / f"{media_path.stem}"
            if mode == 2:
                output_path = output_path.with_name(f"{media_path.stem}_en")
            elif language_code != "auto":
                output_path = output_path.with_name(f"{media_path.stem}_{language_code}")
            output_path = output_path.with_suffix(".srt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(result["segments"], 1):
                    start = self.format_time(segment["start"])
                    end = self.format_time(segment["end"])
                    text = segment["text"].strip()
                    text = self.format_subtitle_text(text, line_type, number_per_line)
                    f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
                    
            self.print_success(f"Captions saved to: {output_path}")
            return True
            
        except Exception as e:
            self.print_error(f"Error: {e}")
            return False
            
    def format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def open_browser_links(self):
        self.print_info("Opening links...")
        try:
            webbrowser.open(APP_TELEGRAM)
            self.print_success("Telegram channel opened")
            time.sleep(0.5)
            webbrowser.open(APP_YOUTUBE)
            self.print_success("YouTube channel opened")
        except Exception as e:
            self.print_warning(f"Could not open browser: {e}")
            
    def run(self):
        self.clear_screen()
        self.print_header()
        
        # Check and install dependencies
        if not check_and_install_dependencies():
            self.print_error("Failed to install dependencies!")
            input("\nPress Enter to exit...")
            return
            
        if not self.check_whisper_available():
            self.print_error("Whisper not available!")
            input("\nPress Enter to exit...")
            return
            
        continue_app = True
        
        while continue_app:
            try:
                allowed_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.m4a', '.flac', '.webm', '.m4v', '.mpg', '.mpeg']
                media_path = self.get_media_path(allowed_extensions)
                self.print_success(f"Selected: {media_path}")
                
                self.selected_model = None
                self.selected_language = None
                self.language_code = "auto"
                self.language_name = "Auto Detect"
                self.model = None
                
                while True:
                    self.clear_screen()
                    self.print_header()
                    print(f"\n{Colors.BOLD}📁 Current file: {media_path.name}{Colors.RESET}")
                    
                    if self.selected_model:
                        print(f"   {Colors.GREEN}🤖 Model: {self.selected_model[0].upper()} ({WHISPER_MODELS[self.selected_model[0]]['size']}){Colors.RESET}")
                    if self.selected_language:
                        print(f"   {Colors.GREEN}🌐 Language: {self.language_name}{Colors.RESET}")
                    print()
                    
                    options = []
                    if self.selected_model is None:
                        options.append("Choose Model")
                    if self.selected_language is None:
                        options.append("Choose Language")
                    
                    if self.selected_model and self.selected_language:
                        options.append("Continue to Subtitle Settings")
                    
                    options.append("Back to File Selection")
                    
                    print(f"{Colors.CYAN}{Colors.BOLD}MAIN MENU{Colors.RESET}")
                    print(f"{Colors.CYAN}┌{'─' * 50}┐{Colors.RESET}")
                    for i, option in enumerate(options, 1):
                        print(f"{Colors.CYAN}│{Colors.RESET} {i:2}) {option:<45} {Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}└{'─' * 50}┘{Colors.RESET}")
                    
                    choice = self.get_number_input(f"➤ Choose option (1-{len(options)}): ", 1, len(options))
                    
                    if choice == len(options):
                        break
                    
                    selected_option = options[choice - 1]
                    
                    if selected_option == "Choose Model":
                        model_options = [f"{m[0].upper()} ({WHISPER_MODELS[m[0]]['size']}) - {m[2]}" for m in self.models]
                        model_choice = self.show_menu("SELECT MODEL", model_options)
                        if model_choice != -1:
                            self.selected_model = self.models[model_choice]
                            self.model = None
                            self.print_success(f"Model selected: {self.selected_model[0].upper()}")
                            input("\nPress Enter to continue...")
                            
                    elif selected_option == "Choose Language":
                        lang_options = [f"{lang[0]} ({lang[1]})" for lang in self.languages]
                        lang_choice = self.show_menu("SELECT LANGUAGE", lang_options)
                        if lang_choice != -1:
                            self.selected_language = self.languages[lang_choice]
                            self.language_name = self.selected_language[0]
                            self.language_code = self.selected_language[1]
                            self.print_success(f"Language selected: {self.language_name}")
                            input("\nPress Enter to continue...")
                            
                    elif selected_option == "Continue to Subtitle Settings":
                        break
                
                if self.selected_model and self.selected_language:
                    self.clear_screen()
                    self.print_header()
                    
                    line_options = ["Words", "Letters"]
                    line_choice = self.show_menu("LINE PREFERENCE", line_options)
                    if line_choice == -1:
                        continue
                    line_type = "words" if line_choice == 0 else "letters"
                    
                    mode_options = [
                        "Normal (Generate in selected language)",
                        "Translation (Translate to English)",
                        "Transliteration (Japanese/Hindi to English)"
                    ]
                    mode_choice = self.show_menu("SUBTITLE MODE", mode_options)
                    if mode_choice == -1:
                        continue
                    mode = mode_choice + 1
                    
                    number_per_line = self.get_number_input(
                        f"How many {line_type} per line? (1-30): ", 1, 30
                    )
                    
                    model_name = self.selected_model[0].upper()
                    self.print_box([
                        f"📁 Media File: {media_path}",
                        f"🤖 Model: {model_name} (.pt format)",
                        f"🌐 Language: {self.language_name}",
                        f"🎯 Mode: {mode_options[mode-1].split(' (')[0]}",
                        f"📝 Line Type: {line_type}",
                        f"🔢 {line_type.title()} per line: {number_per_line}"
                    ])
                    
                    if not self.confirm("Generate captions?"):
                        continue
                    
                    self.print_info("Generating captions... This may take several minutes.")
                    success = self.generate_captions(
                        media_path,
                        self.selected_model[0],
                        line_type,
                        number_per_line,
                        mode,
                        self.language_code
                    )
                    
                    if success:
                        self.print_success(f"Thanks for using {APP_NAME}!")
                        self.print_success("Your caption has been generated successfully!")
                        self.open_browser_links()
                        
                        if self.confirm("Process another video?"):
                            continue
                        else:
                            continue_app = False
                            break
                    else:
                        self.print_error("Failed to generate captions")
                        if not self.confirm("Try again?"):
                            continue
                else:
                    self.print_warning("Please select both Model and Language first!")
                    input("Press Enter to continue...")
                        
            except KeyboardInterrupt:
                print("\n")
                self.print_warning("Interrupted by user")
                break
            except Exception as e:
                self.print_error(f"Unexpected error: {e}")
                if not self.confirm("Continue?"):
                    break
                    
        self.clear_screen()
        self.print_header("Thank You!")
        self.print_success(f"Thanks for using {APP_NAME}!")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'{APP_NAME} - {APP_AUTHOR}')
    parser.add_argument('file', nargs='?', help='Video/Audio file to process')
    args = parser.parse_args()
    
    app = NotYCaptionGenerator(args.file)
    app.run()