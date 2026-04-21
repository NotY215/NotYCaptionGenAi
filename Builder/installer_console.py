#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Installer v7.1
With version checking, repair option, and AppData model installation
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
from datetime import datetime

APP_NAME = "NotY Caption Generator AI"
APP_EXE_NAME = "NotYCaptionGenAI"
APP_VERSION = "7.1"
APP_AUTHOR = "NotY215"
MAIN_EXE = "NotYCaptionGenAI.exe"
UNINSTALL_EXE = "Uninstaller.exe"
PACKAGES_FOLDER = "_pythonPackages_"
APP_DATA_FOLDER = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'NotYCaptionGenAI')

# Registry key for version info
REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"

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

def get_installed_version():
    """Get installed version from registry"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ)
        version, _ = winreg.QueryValueEx(key, "DisplayVersion")
        winreg.CloseKey(key)
        return version
    except:
        return None

def get_install_path():
    """Get install path from registry"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ)
        install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
        winreg.CloseKey(key)
        return Path(install_path)
    except:
        return None

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
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, APP_AUTHOR)
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(install_path / UNINSTALL_EXE))
        winreg.CloseKey(key)
        print_success("Registered in Windows")
        return True
    except Exception as e:
        print_error(f"Registry error: {e}")
        return False

def add_to_path(install_path):
    """Add application to system PATH"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                             0, winreg.KEY_ALL_ACCESS)
        current_path, _ = winreg.QueryValueEx(key, "Path")
        app_path = str(install_path)
        
        if app_path not in current_path:
            new_path = current_path + ";" + app_path
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            print_success("Added to system PATH")
            
            # Broadcast environment change
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment")
            return True
    except Exception as e:
        print_warning(f"Could not add to PATH: {e}")
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

def install_models_to_appdata():
    """Copy models from installer to AppData folder"""
    try:
        appdata_models = Path(APP_DATA_FOLDER) / "models"
        appdata_models.mkdir(parents=True, exist_ok=True)
        
        # Get models from embedded files
        models_src = get_embedded_file("models")
        if models_src.exists():
            copy_directory(models_src, appdata_models, "Models to AppData")
            return True
        return False
    except Exception as e:
        print_warning(f"Could not copy models to AppData: {e}")
        return False

def copy_packages(dest_packages_dir):
    """Copy packages from embedded _pythonPackages_ folder"""
    packages_src = get_embedded_file(PACKAGES_FOLDER)
    if packages_src.exists():
        if dest_packages_dir.exists():
            shutil.rmtree(dest_packages_dir)
        shutil.copytree(packages_src, dest_packages_dir)
        print_success(f"Python packages copied")
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

def perform_installation(install_path, is_repair=False):
    """Perform the actual installation"""
    try:
        install_path.mkdir(parents=True, exist_ok=True)
        
        # Copy main executable
        shutil.copy2(get_embedded_file(MAIN_EXE), install_path / MAIN_EXE)
        print_success("Main executable copied")
        
        # Copy uninstaller
        shutil.copy2(get_embedded_file(UNINSTALL_EXE), install_path / UNINSTALL_EXE)
        print_success("Uninstaller copied")
        
        # Copy packages
        packages_dir = install_path / PACKAGES_FOLDER
        copy_packages(packages_dir)
        
        # Copy ffmpeg
        copy_directory(get_embedded_file("ffmpeg"), install_path / "ffmpeg", "FFmpeg")
        
        # Copy resources
        copy_directory(get_embedded_file("resources"), install_path / "resources", "Resources")
        
        # Copy pretrained models for Spleeter
        copy_directory(get_embedded_file("pretrained_models"), install_path / "pretrained_models", "Spleeter models")
        
        # Install models to AppData (for whisper)
        install_models_to_appdata()
        
        # Create shortcuts
        create_shortcuts(install_path)
        
        # Register in Windows
        register_uninstall(install_path)
        
        # Add to PATH
        add_to_path(install_path)
        
        return True
    except Exception as e:
        print_error(f"Installation failed: {e}")
        return False

def main():
    if not is_admin():
        print_warning("Admin privileges required!")
        if run_as_admin():
            sys.exit(0)
    
    print_header()
    
    # Check if already installed
    installed_version = get_installed_version()
    install_path = get_install_path()
    
    if installed_version and install_path and install_path.exists():
        print_info(f"Existing installation found: v{installed_version} at {install_path}")
        print()
        
        if installed_version > APP_VERSION:
            print_warning(f"Installed version ({installed_version}) is NEWER than this installer ({APP_VERSION})")
            print(f"\n  1) Cancel installation")
            print(f"  2) Uninstall v{installed_version} and install v{APP_VERSION}")
            choice = get_number_input("\nOption (1-2): ", 1, 2)
            if choice == 1:
                print_info("Installation cancelled.")
                return False
            else:
                # Uninstall old version
                print_info(f"Uninstalling v{installed_version}...")
                uninstaller = install_path / UNINSTALL_EXE
                if uninstaller.exists():
                    subprocess.run([str(uninstaller), '/S'], capture_output=True)
                shutil.rmtree(install_path, ignore_errors=True)
                
        elif installed_version < APP_VERSION:
            print_info(f"Installed version ({installed_version}) is OLDER than this installer ({APP_VERSION})")
            print(f"\n  1) Update (keep settings)")
            print(f"  2) Clean installation (remove everything)")
            print(f"  3) Cancel")
            choice = get_number_input("\nOption (1-3): ", 1, 3)
            if choice == 1:
                print_info("Updating installation...")
            elif choice == 2:
                print_info("Performing clean installation...")
                shutil.rmtree(install_path, ignore_errors=True)
            else:
                print_info("Installation cancelled.")
                return False
                
        else:  # versions equal
            print_info(f"Installed version ({installed_version}) matches this installer")
            print(f"\n  1) Repair (replace all files)")
            print(f"  2) Uninstall and exit")
            print(f"  3) Cancel")
            choice = get_number_input("\nOption (1-3): ", 1, 3)
            if choice == 1:
                print_info("Repairing installation...")
            elif choice == 2:
                print_info("Uninstalling...")
                uninstaller = install_path / UNINSTALL_EXE
                if uninstaller.exists():
                    subprocess.run([str(uninstaller), '/S'], capture_output=True)
                shutil.rmtree(install_path, ignore_errors=True)
                print_info("Uninstallation completed.")
                return False
            else:
                print_info("Installation cancelled.")
                return False
        
        # Use existing install path for update/repair
        if perform_installation(install_path, is_repair=(installed_version == APP_VERSION)):
            print_header()
            print_success("Installation/Update Complete!")
            print_info(f"Installed to: {install_path}")
            print_info(f"Models stored in: {APP_DATA_FOLDER}\\models")
            print_info(f"Run: {install_path / MAIN_EXE}")
            return True
        else:
            return False
    
    else:
        # New installation
        default_path = "C:\\NotYCaptionGenAI"
        while True:
            print(f"\n{Colors.BOLD}Installation Directory{Colors.RESET}")
            print(f"  Default: {default_path}")
            print(f"\n  1) Use default")
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
        
        if perform_installation(install_path):
            print_header()
            print_success("Installation Complete!")
            print_info(f"Installed to: {install_path}")
            print_info(f"Models stored in: {APP_DATA_FOLDER}\\models")
            print_info(f"Size: {get_directory_size(install_path):.1f} MB")
            print_info(f"Run: {install_path / MAIN_EXE}")
            print_info("Right-click any file > Send To > NotYCaptionGenAi")
            return True
        else:
            return False

if __name__ == "__main__":
    success = main()
    print_success("\nInstallation completed!" if success else "\nInstallation failed!")
    input("\nPress Enter to exit...")