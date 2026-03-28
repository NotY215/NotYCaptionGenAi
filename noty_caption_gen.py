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
from pathlib import Path
from typing import List, Tuple, Optional

# Fix Windows console encoding
if platform.system() == "Windows":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

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
APP_TELEGRAM = "https://t.me/Noty_215"
APP_YOUTUBE = "https://www.youtube.com/@NotY215"

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    BOLD = '\033[1m'

if platform.system() == "Windows":
    try:
        import colorama
        colorama.init()
    except ImportError:
        Colors.RESET = ''
        Colors.GREEN = ''
        Colors.RED = ''
        Colors.YELLOW = ''
        Colors.CYAN = ''
        Colors.BOLD = ''

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
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
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
        """Clear console screen"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
    def print_header(self, title: str = None):
        if title is None:
            title = f"{APP_NAME} v{APP_VERSION}"
        width = 60
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔" + "═" * (width - 2) + "╗")
        print("║" + title.center(width - 2) + "║")
        print("║" + f"Copyright (c) {APP_YEAR} {APP_AUTHOR}".center(width - 2) + "║")
        print("║" + f"License: {APP_LICENSE}".center(width - 2) + "║")
        print("║" + "Powered by OpenAI Whisper (.pt models)".center(width - 2) + "║")
        print("╚" + "═" * (width - 2) + "╝")
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
        """Get user input with proper encoding"""
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
        # Handle drag and drop (Windows removes quotes)
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
        if not WHISPER_AVAILABLE:
            self.print_error("OpenAI Whisper not installed!")
            self.print_info("Install it with: pip install openai-whisper torch")
            return False
        return True
        
    def load_model(self, model_name: str):
        """Load whisper .pt model"""
        model_info = WHISPER_MODELS[model_name]
        self.print_info(f"Loading {model_name.upper()} model (.pt format)...")
        self.print_info(f"Size: {model_info['size']}")
        self.print_info(f"Models will be saved to: {self.models_dir}")
        try:
            # Whisper automatically downloads .pt models from OpenAI servers
            self.model = whisper.load_model(model_name, download_root=str(self.models_dir))
            self.print_success(f"Model loaded successfully")
            return True
        except Exception as e:
            self.print_error(f"Failed to load model: {e}")
            self.print_info("Make sure you have an internet connection for first-time download")
            return False
            
    def format_subtitle_text(self, text: str, line_type: str, number_per_line: int) -> str:
        """Format subtitle text with proper line breaks"""
        if not text:
            return text
            
        # First, split the text into sentences or phrases
        # Handle different line types
        if line_type == "words":
            return self.limit_words_per_line(text, number_per_line)
        else:
            return self.limit_letters_per_line(text, number_per_line)
    
    def limit_words_per_line(self, text: str, max_words: int) -> str:
        """Split text into lines with max_words per line"""
        if max_words <= 0:
            return text
            
        # Split into words
        words = text.split()
        
        if len(words) <= max_words:
            return text
        
        # Build lines with max_words per line
        lines = []
        for i in range(0, len(words), max_words):
            line_words = words[i:i + max_words]
            lines.append(' '.join(line_words))
        
        return '\n'.join(lines)
    
    def limit_letters_per_line(self, text: str, max_letters: int) -> str:
        """Split text into lines with max_letters per line"""
        if max_letters <= 0:
            return text
            
        if len(text) <= max_letters:
            return text
        
        lines = []
        current_line = ""
        current_length = 0
        
        # Split by spaces to preserve words
        words = text.split()
        
        for word in words:
            word_length = len(word)
            
            # If adding this word would exceed the limit
            if current_length + word_length + (1 if current_line else 0) > max_letters:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                    current_length = word_length
                else:
                    # Word itself is longer than max_letters, force break
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
        
        # Add the last line
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
            
            # Set task
            task = "transcribe"
            if mode == 2:
                task = "translate"
                
            language = language_code if language_code != "auto" else None
            
            # Transcribe with word timestamps for better accuracy
            result = self.model.transcribe(
                str(media_path),
                task=task,
                language=language,
                verbose=False,
                word_timestamps=True
            )
            
            # Generate output path
            output_path = media_path.parent / f"{media_path.stem}"
            if mode == 2:
                output_path = output_path.with_name(f"{media_path.stem}_en")
            elif language_code != "auto":
                output_path = output_path.with_name(f"{media_path.stem}_{language_code}")
            output_path = output_path.with_suffix(".srt")
            
            # Write SRT
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(result["segments"], 1):
                    start = self.format_time(segment["start"])
                    end = self.format_time(segment["end"])
                    text = segment["text"].strip()
                    
                    # Apply transliteration
                    if mode == 3:
                        text = self.transliterate(text, language_code)
                    
                    # Apply line limit
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
        
    def transliterate(self, text: str, lang: str) -> str:
        """Basic transliteration for Japanese and Hindi"""
        # Japanese Hiragana to Romaji
        japanese_map = {
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
        
        # Hindi to Romanized Hindi
        hindi_map = {
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'nga',
            'च': 'cha', 'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'nya',
            'ट': 'ta', 'ठ': 'tha', 'ड': 'da', 'ढ': 'dha', 'ण': 'na',
            'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
            'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
            'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va', 'श': 'sha',
            'ष': 'sha', 'स': 'sa', 'ह': 'ha'
        }
        
        if lang == 'ja':
            for k, v in japanese_map.items():
                text = text.replace(k, v)
        elif lang == 'hi':
            for k, v in hindi_map.items():
                text = text.replace(k, v)
        return text
        
    def open_browser_links(self):
        """Open Telegram and YouTube links"""
        self.print_info("Opening links...")
        try:
            webbrowser.open(APP_TELEGRAM)
            self.print_success("Telegram channel opened")
            time.sleep(0.5)
            webbrowser.open(APP_YOUTUBE)
            self.print_success("YouTube channel opened")
        except Exception as e:
            self.print_warning(f"Could not open browser: {e}")
            self.print_info(f"Telegram: {APP_TELEGRAM}")
            self.print_info(f"YouTube: {APP_YOUTUBE}")
            
    def run(self):
        self.clear_screen()
        self.print_header()
        
        if not self.check_whisper_available():
            self.print_info("\nRun: pip install openai-whisper torch")
            input("\nPress Enter to exit...")
            return
            
        continue_app = True
        
        while continue_app:
            try:
                allowed_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav', '.m4a', '.flac', '.webm', '.m4v', '.mpg', '.mpeg']
                media_path = self.get_media_path(allowed_extensions)
                self.print_success(f"Selected: {media_path}")
                
                # Reset selections for new video
                self.selected_model = None
                self.selected_language = None
                self.language_code = "auto"
                self.language_name = "Auto Detect"
                self.model = None
                
                # Main selection loop - only 2 options max
                while True:
                    self.clear_screen()
                    self.print_header()
                    print(f"\n📁 Current file: {media_path.name}")
                    
                    # Show current selections
                    if self.selected_model:
                        print(f"   🤖 Model: {self.selected_model[0].upper()} ({WHISPER_MODELS[self.selected_model[0]]['size']})")
                    if self.selected_language:
                        print(f"   🌐 Language: {self.language_name}")
                    print()
                    
                    # Build menu - only show options for what's NOT selected
                    options = []
                    if self.selected_model is None:
                        options.append("Choose Model")
                    if self.selected_language is None:
                        options.append("Choose Language")
                    
                    # If both are selected, show continue option
                    if self.selected_model and self.selected_language:
                        options.append("Continue to Subtitle Settings")
                    
                    # Always add back option
                    options.append("Back to File Selection")
                    
                    # Show menu with only 2-3 options
                    print(f"{Colors.CYAN}{Colors.BOLD}MAIN MENU{Colors.RESET}")
                    print(f"{Colors.CYAN}┌{'─' * 50}┐{Colors.RESET}")
                    for i, option in enumerate(options, 1):
                        print(f"{Colors.CYAN}│{Colors.RESET} {i:2}) {option:<45} {Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}└{'─' * 50}┘{Colors.RESET}")
                    
                    choice = self.get_number_input(f"➤ Choose option (1-{len(options)}): ", 1, len(options))
                    
                    if choice == len(options):  # Back to file selection
                        break
                    
                    selected_option = options[choice - 1]
                    
                    if selected_option == "Choose Model":
                        # Show model selection
                        model_options = [f"{m[0].upper()} ({WHISPER_MODELS[m[0]]['size']}) - {m[2]}" for m in self.models]
                        model_choice = self.show_menu("SELECT MODEL", model_options)
                        
                        if model_choice != -1:
                            self.selected_model = self.models[model_choice]
                            self.model = None  # Reset model to reload
                            self.print_success(f"Model selected: {self.selected_model[0].upper()}")
                            input("\nPress Enter to continue...")
                            
                    elif selected_option == "Choose Language":
                        # Show language selection
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
                
                # If both selected, proceed to subtitle settings
                if self.selected_model and self.selected_language:
                    self.clear_screen()
                    self.print_header()
                    
                    # Line preference
                    line_options = ["Words", "Letters"]
                    line_choice = self.show_menu("LINE PREFERENCE", line_options)
                    if line_choice == -1:
                        continue
                    line_type = "words" if line_choice == 0 else "letters"
                    
                    # Subtitle mode
                    mode_options = [
                        "Normal (Generate in selected language)",
                        "Translation (Translate to English)",
                        "Transliteration (Japanese/Hindi to English)"
                    ]
                    mode_choice = self.show_menu("SUBTITLE MODE", mode_options)
                    if mode_choice == -1:
                        continue
                    mode = mode_choice + 1
                    
                    if mode == 3:
                        self.print_warning("Transliteration works best for Japanese and Hindi")
                        input("Press Enter to continue...")
                    
                    # Number per line
                    number_per_line = self.get_number_input(
                        f"How many {line_type} per line? (1-30): ", 1, 30
                    )
                    
                    # Confirmation
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
                    
                    # Generate captions
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
                        
                        # Open browser links
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