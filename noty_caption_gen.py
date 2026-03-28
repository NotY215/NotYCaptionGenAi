"""
NotY Caption Generator AI
Powered by Whisper.cpp

Copyright © 2026 NotY215
License: LGPL-3.0
Website: https://www.youtube.com/@NotY215
"""

import os
import sys
import subprocess
import shutil
import json
import urllib.request
import webbrowser
import time
import platform
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import threading
import queue

# Application metadata
APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "4.2"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"
APP_LICENSE = "LGPL-3.0"
APP_WEBSITE = "https://www.youtube.com/@NotY215"

# ANSI color codes for console output
class Colors:
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Windows console doesn't support ANSI by default
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

class NotYCaptionGenerator:
    def __init__(self, media_path: str = None):
        # Get application directory (where executable is located)
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
            
        self.resources_dir = self.base_dir / "resources"
        self.whisper_dir = self.resources_dir / "whisper"
        self.files_dir = self.resources_dir / "files"
        self.models_dir = self.resources_dir / "models"
        
        # Create directories if they don't exist
        self.whisper_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Language options
        self.languages = [
            ("English", "en"),
            ("Hindi", "hi"),
            ("Japanese", "ja"),
            ("Chinese", "zh"),
            ("Urdu", "ur")
        ]
        
        # Model options
        self.models = [
            ("tiny", "75 MB", "Fastest", "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin"),
            ("base", "150 MB", "Balanced", "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin"),
            ("small", "500 MB", "Good", "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"),
            ("medium", "1.5 GB", "Accurate", "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin"),
            ("large", "2.9 GB", "Best", "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin")
        ]
        
        # Selected options
        self.selected_model = None
        self.selected_language = None
        self.language_code = "auto"
        self.language_name = "Auto Detect"
        
        # Media path from command line (for Send To)
        self.media_path_arg = media_path
        
    def print_header(self, title: str = None):
        """Print a fancy header"""
        if title is None:
            title = f"{APP_NAME} v{APP_VERSION}"
        width = 50
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔" + "═" * (width - 2) + "╗")
        print("║" + title.center(width - 2) + "║")
        print("║" + f"Copyright © {APP_YEAR} {APP_AUTHOR}".center(width - 2) + "║")
        print("║" + f"License: {APP_LICENSE}".center(width - 2) + "║")
        print("║" + "Powered by Whisper.cpp".center(width - 2) + "║")
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
        if default:
            print(f"{Colors.CYAN}{prompt} [{default}]: {Colors.RESET}", end="")
            value = input().strip()
            return value if value else default
        else:
            print(f"{Colors.CYAN}{prompt}{Colors.RESET}", end="")
            return input().strip()
            
    def get_number_input(self, prompt: str, min_val: int, max_val: int) -> int:
        while True:
            try:
                value = int(self.get_input(prompt))
                if min_val <= value <= max_val:
                    return value
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
        # If media path was provided via command line, use it
        if self.media_path_arg:
            path = Path(self.media_path_arg)
            if path.exists() and path.suffix.lower() in allowed_extensions:
                self.print_success(f"Using file from Send To: {path}")
                return path
            else:
                self.print_warning(f"Invalid file from command line: {self.media_path_arg}")
                
        while True:
            print(f"\n{Colors.CYAN}📂 Provide Video/Audio Path{Colors.RESET}")
            print(f"   Allowed extensions: {', '.join(allowed_extensions)}")
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
            
    def download_file(self, url: str, dest: Path, description: str) -> bool:
        try:
            self.print_info(f"Downloading {description}...")
            self.print_info(f"URL: {url}")
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                total_size = int(response.getheader('Content-Length', 0))
                downloaded = 0
                block_size = 8192
                
                with open(dest, 'wb') as out_file:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        out_file.write(buffer)
                        downloaded += len(buffer)
                        
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            bar_length = 50
                            filled = int(bar_length * percent / 100)
                            bar = '=' * filled + '>' + ' ' * (bar_length - filled - 1)
                            print(f"\r   [{bar}] {percent}%", end='', flush=True)
                            
            print()
            self.print_success(f"{description} downloaded successfully")
            return True
            
        except Exception as e:
            self.print_error(f"Download failed: {e}")
            if dest.exists():
                dest.unlink()
            return False
            
    def check_required_files(self) -> bool:
        all_good = True
        
        whisper_exe = self.whisper_dir / "whisper-cli.exe"
        if not whisper_exe.exists():
            self.print_error(f"Missing: {whisper_exe}")
            all_good = False
        else:
            self.print_success(f"Found: {whisper_exe.name}")
            
        whisper_dll = self.whisper_dir / "whisper.dll"
        if not whisper_dll.exists():
            self.print_error(f"Missing: {whisper_dll}")
            all_good = False
        else:
            self.print_success(f"Found: {whisper_dll.name}")
            
        ffmpeg = self.files_dir / "ffmpeg.exe"
        if not ffmpeg.exists():
            self.print_error(f"Missing: {ffmpeg}")
            all_good = False
        else:
            self.print_success(f"Found: {ffmpeg.name}")
            
        ffprobe = self.files_dir / "ffprobe.exe"
        if not ffprobe.exists():
            self.print_error(f"Missing: {ffprobe}")
            all_good = False
        else:
            self.print_success(f"Found: {ffprobe.name}")
            
        return all_good
        
    def check_model_exists(self, model_name: str) -> bool:
        model_path = self.models_dir / f"ggml-{model_name}.bin"
        if model_name == "large":
            model_path = self.models_dir / "ggml-large-v1.bin"
        return model_path.exists()
        
    def download_model(self, model_name: str, model_size: str, model_url: str) -> bool:
        model_path = self.models_dir / f"ggml-{model_name}.bin"
        if model_name == "large":
            model_path = self.models_dir / "ggml-large-v1.bin"
        return self.download_file(model_url, model_path, f"{model_name.upper()} model ({model_size})")
        
    def generate_captions(self, media_path: Path, model_name: str, line_type: str, 
                          number_per_line: int, mode: int, language_code: str) -> bool:
        try:
            model_path = self.models_dir / f"ggml-{model_name}.bin"
            if model_name == "large":
                model_path = self.models_dir / "ggml-large-v1.bin"
                
            output_path = media_path.parent / f"{media_path.stem}"
            if mode == 2:
                output_path = output_path.with_name(f"{media_path.stem}_en")
            elif mode == 3:
                output_path = output_path.with_name(f"{media_path.stem}_translit")
            elif language_code != "auto":
                output_path = output_path.with_name(f"{media_path.stem}_{language_code}")
                
            output_path = output_path.with_suffix(".srt")
            
            whisper_exe = self.whisper_dir / "whisper-cli.exe"
            cmd = [
                str(whisper_exe),
                "-m", str(model_path),
                "-f", str(media_path),
                "-of", str(output_path.with_suffix("")),
                "-t", "8",
                "-p", "4"
            ]
            
            if language_code != "auto":
                cmd.extend(["-l", language_code])
                
            if mode == 2:
                cmd.extend(["-tr", "en"])
                
            cmd.append("--output-srt")
            cmd.append("--print-progress")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                if "progress" in line:
                    try:
                        if "=" in line:
                            progress_str = line.split("=")[-1].strip().replace("%", "")
                            percent = int(float(progress_str))
                            self.print_progress(percent)
                    except:
                        print(line.strip())
                elif line.strip():
                    print(line.strip())
                    
            process.wait()
            
            if process.returncode == 0:
                self.post_process_srt(output_path, line_type, number_per_line)
                self.print_success(f"Captions saved to: {output_path}")
                return True
            else:
                self.print_error(f"Whisper process failed with code: {process.returncode}")
                return False
                
        except Exception as e:
            self.print_error(f"Error generating captions: {e}")
            return False
            
    def print_progress(self, percent: int):
        bar_length = 50
        filled = int(bar_length * percent / 100)
        bar = '=' * filled + '>' + ' ' * (bar_length - filled - 1)
        print(f"\r[{bar}] {percent}%", end='', flush=True)
        
    def post_process_srt(self, srt_path: Path, line_type: str, number_per_line: int):
        if not srt_path.exists():
            return
            
        with open(srt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        processed_lines = []
        for i, line in enumerate(lines):
            if i % 4 == 2:
                if line_type == "words":
                    line = self.limit_words_per_line(line, number_per_line)
                else:
                    line = self.limit_letters_per_line(line, number_per_line)
            processed_lines.append(line)
            
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.writelines(processed_lines)
            
    def limit_words_per_line(self, text: str, max_words: int) -> str:
        words = text.split()
        if len(words) <= max_words:
            return text
            
        result = []
        for i in range(0, len(words), max_words):
            result.append(' '.join(words[i:i+max_words]))
        return '\n'.join(result)
        
    def limit_letters_per_line(self, text: str, max_letters: int) -> str:
        if len(text) <= max_letters:
            return text
            
        result = []
        current_line = []
        current_length = 0
        
        for word in text.split():
            if current_length + len(word) + 1 > max_letters and current_line:
                result.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1
                
        if current_line:
            result.append(' '.join(current_line))
            
        return '\n'.join(result)
        
    def open_browser_links(self):
        self.print_info("Opening links...")
        try:
            webbrowser.open("https://t.me/NotY215")
            self.print_success("Telegram opened")
            time.sleep(1)
            webbrowser.open(APP_WEBSITE)
            self.print_success("YouTube opened")
        except Exception as e:
            self.print_warning(f"Could not open browser: {e}")
            
    def run(self):
        self.print_header()
        
        if not self.check_required_files():
            self.print_error("Required files are missing!")
            self.print_box([
                "Please ensure the following files exist:",
                f"  {self.whisper_dir / 'whisper-cli.exe'}",
                f"  {self.whisper_dir / 'whisper.dll'}",
                f"  {self.files_dir / 'ffmpeg.exe'}",
                f"  {self.files_dir / 'ffprobe.exe'}"
            ])
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
                
                while True:
                    options = []
                    if self.selected_model is None:
                        options.append("Choose Model")
                    if self.selected_language is None:
                        options.append("Choose Language")
                        
                    if not options:
                        break
                        
                    title = "MAIN MENU"
                    if self.selected_model:
                        title += f" (Model: {self.selected_model[0].upper()})"
                    if self.selected_language:
                        title += f" (Language: {self.language_name})"
                        
                    choice = self.show_menu(title, options)
                    
                    if choice == -1:
                        break
                        
                    if not self.selected_model:
                        model_options = [f"{m[0].upper()} ({m[1]}) - {m[2]}" for m in self.models]
                        model_choice = self.show_menu("SELECT MODEL", model_options)
                        
                        if model_choice != -1:
                            model = self.models[model_choice]
                            model_name = model[0]
                            model_size = model[1]
                            model_url = model[3]
                            
                            if not self.check_model_exists(model_name):
                                self.print_warning(f"Model {model_name.upper()} not found")
                                if self.confirm(f"Download {model_name.upper()} model ({model_size})?"):
                                    if self.download_model(model_name, model_size, model_url):
                                        self.selected_model = model
                                        self.print_success(f"Model selected: {model_name.upper()}")
                                    else:
                                        continue
                                else:
                                    continue
                            else:
                                self.selected_model = model
                                self.print_success(f"Model selected: {model_name.upper()}")
                                
                    elif not self.selected_language:
                        lang_options = [f"{lang[0]} ({lang[1]})" for lang in self.languages]
                        lang_choice = self.show_menu("SELECT LANGUAGE", lang_options)
                        
                        if lang_choice != -1:
                            self.selected_language = self.languages[lang_choice]
                            self.language_name = self.selected_language[0]
                            self.language_code = self.selected_language[1]
                            self.print_success(f"Language selected: {self.language_name}")
                            
                line_options = ["Words", "Letters"]
                line_choice = self.show_menu("LINE PREFERENCE", line_options)
                if line_choice == -1:
                    continue
                line_type = "words" if line_choice == 0 else "letters"
                
                mode_options = [
                    "Normal (Generate in selected language)",
                    "Translation (Translate to English)",
                    "Transliteration (Convert Japanese/Hindi to English)"
                ]
                mode_choice = self.show_menu("SUBTITLE MODE", mode_options)
                if mode_choice == -1:
                    continue
                mode = mode_choice + 1
                
                if mode == 3:
                    self.print_warning("Transliteration works best for Japanese and Hindi")
                    input("Press Enter to continue...")
                    
                number_per_line = self.get_number_input(
                    f"How many {line_type} per line? (1-30): ", 1, 30
                )
                
                model_name = self.selected_model[0].upper()
                self.print_box([
                    f"📁 Media File: {media_path}",
                    f"🤖 Model: {model_name}",
                    f"🌐 Language: {self.language_name}",
                    f"🎯 Mode: {mode_options[mode-1].split(' (')[0]}",
                    f"📝 Line Type: {line_type}",
                    f"🔢 {line_type.title()} per line: {number_per_line}",
                    f"💾 Output: {media_path.parent / f'{media_path.stem}_output.srt'}"
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
                        self.media_path_arg = None
                        continue
                    else:
                        continue_app = False
                        break
                else:
                    self.print_error("Failed to generate captions")
                    if not self.confirm("Try again?"):
                        break
                        
            except KeyboardInterrupt:
                print("\n")
                self.print_warning("Interrupted by user")
                break
            except Exception as e:
                self.print_error(f"Unexpected error: {e}")
                if not self.confirm("Continue?"):
                    break
                    
        self.print_header("Thank You!")
        self.print_success(f"Thanks for using {APP_NAME}!")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'{APP_NAME} - {APP_AUTHOR}')
    parser.add_argument('file', nargs='?', help='Video/Audio file to process (for Send To)')
    args = parser.parse_args()
    
    app = NotYCaptionGenerator(args.file)
    app.run()