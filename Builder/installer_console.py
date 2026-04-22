#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Installer v7.1 - GUI Version
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import time
import platform
import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import winreg

APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "7.1"
APP_AUTHOR = "NotY215"
MAIN_EXE = "NotYCaptionGenAI.exe"
UNINSTALL_EXE = "Uninstaller.exe"
PACKAGES_FOLDER = "_pythonPackages_"
APP_DATA_FOLDER = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'NotYCaptionGenAI')

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

if platform.system() == "Windows":
    os.system('color')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return True
    except:
        return False

def print_header():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("+" + "=" * 58 + "+")
    print("|" + f"{APP_NAME} Installer v{APP_VERSION}".center(58) + "|")
    print("|" + f"Copyright (c) 2026 {APP_AUTHOR}".center(58) + "|")
    print("+" + "=" * 58 + "+")
    print(f"{Colors.RESET}")

def print_success(m): print(f"{Colors.GREEN}[OK] {m}{Colors.RESET}")
def print_error(m): print(f"{Colors.RED}[ERROR] {m}{Colors.RESET}")
def print_warning(m): print(f"{Colors.YELLOW}[WARNING] {m}{Colors.RESET}")
def print_info(m): print(f"{Colors.CYAN}[INFO] {m}{Colors.RESET}")

def get_number_input(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(f"{Colors.CYAN}{prompt}{Colors.RESET}"))
            if min_val <= val <= max_val:
                return val
            print_error(f"Enter number between {min_val} and {max_val}")
        except ValueError:
            print_error("Invalid input!")

def select_folder_dialog():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askdirectory(title="Select Installation Directory")
        root.destroy()
        return path
    except:
        return None

def register_uninstall(install_path):
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, APP_AUTHOR)
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(install_path / UNINSTALL_EXE))
        winreg.CloseKey(key)
        print_success("Registered in Windows")
        return True
    except:
        return False

def create_shortcut(path, target):
    ps = f'''$s = New-Object -ComObject WScript.Shell
$l = $s.CreateShortcut("{path}")
$l.TargetPath = "{target}"
$l.WorkingDirectory = "{Path(target).parent}"
$l.Save()'''
    subprocess.run(["powershell", "-Command", ps], capture_output=True)

def create_shortcuts(install_dir):
    start = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAI.lnk"
    create_shortcut(str(start), str(install_dir / MAIN_EXE))
    desktop = Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAI.lnk"
    create_shortcut(str(desktop), str(install_dir / MAIN_EXE))
    sendto = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAI.lnk"
    sendto.parent.mkdir(parents=True, exist_ok=True)
    create_shortcut(str(sendto), str(install_dir / MAIN_EXE))
    print_success("Shortcuts created")

def copy_directory(src, dst, name):
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print_success(f"{name} copied")
        return True
    return False

def get_embedded_file(path):
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / path
    return Path(__file__).parent / path

def get_directory_size(path):
    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            total += item.stat().st_size
    return total / (1024 * 1024)

def install():
    if not is_admin():
        print_warning("Admin privileges required!")
        if run_as_admin():
            sys.exit(0)
    
    print_header()
    
    default_path = "C:\\NotYCaptionGenAI"
    while True:
        print(f"\nInstallation Directory")
        print(f"  1) Default: {default_path}")
        print(f"  2) Browse")
        print(f"  0) Cancel")
        choice = get_number_input("\nOption (0-2): ", 0, 2)
        if choice == 0:
            return False
        elif choice == 1:
            install_path = Path(default_path)
            break
        else:
            selected = select_folder_dialog()
            if selected:
                install_path = Path(selected) / "NotYCaptionGenAI"
                print_success(f"Selected: {install_path}")
                confirm = input(f"\nConfirm installation? (y/n): ").lower()
                if confirm == 'y':
                    break
    
    print_info(f"Installing to: {install_path}")
    install_path.mkdir(parents=True, exist_ok=True)
    
    # Create AppData folder for models
    os.makedirs(APP_DATA_FOLDER, exist_ok=True)
    
    # Copy main executable
    shutil.copy2(get_embedded_file(MAIN_EXE), install_path / MAIN_EXE)
    print_success("Main executable copied")
    
    # Copy uninstaller
    shutil.copy2(get_embedded_file(UNINSTALL_EXE), install_path / UNINSTALL_EXE)
    print_success("Uninstaller copied")
    
    # Copy packages
    packages_src = get_embedded_file(PACKAGES_FOLDER)
    if packages_src.exists():
        dest_packages = install_path / PACKAGES_FOLDER
        if dest_packages.exists():
            shutil.rmtree(dest_packages)
        shutil.copytree(packages_src, dest_packages)
        print_success("Python packages copied")
    
    # Copy resources
    copy_directory(get_embedded_file("resources"), install_path / "resources", "Resources")
    
    # Copy ffmpeg
    copy_directory(get_embedded_file("ffmpeg"), install_path / "ffmpeg", "FFmpeg")
    
    # Copy models to AppData
    models_src = get_embedded_file("models")
    if models_src.exists():
        dest_models = Path(APP_DATA_FOLDER) / "models"
        if dest_models.exists():
            shutil.rmtree(dest_models)
        shutil.copytree(models_src, dest_models)
        print_success("Whisper models copied to AppData")
    
    # Copy pretrained_models
    copy_directory(get_embedded_file("pretrained_models"), install_path / "pretrained_models", "Spleeter models")
    
    # Create shortcuts
    create_shortcuts(install_path)
    
    # Register in Windows
    register_uninstall(install_path)
    
    print_header()
    print_success("Installation Complete!")
    print_info(f"Installed to: {install_path}")
    print_info(f"Size: {get_directory_size(install_path):.1f} MB")
    print_info(f"Models stored in: {APP_DATA_FOLDER}\\models")
    print_info(f"Run: {install_path / MAIN_EXE}")
    return True

if __name__ == "__main__":
    success = install()
    print_success("\nInstallation completed!" if success else "\nInstallation failed!")
    input("\nPress Enter to exit...")