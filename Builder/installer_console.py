#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Installer v6.1 (Console)
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
import tempfile
import winreg

# Application metadata
APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "6.1"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"
MAIN_EXE = "NotYCaptionGenAI.exe"
UNINSTALL_EXE = "NotYCaptionGenAI_Uninstaller.exe"

# Colors for console output
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

if platform.system() == "Windows":
    os.system('color')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return True
    except:
        return False

def print_header():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("+" + "=" * 58 + "+")
    print("|" + f"{APP_NAME} Installer v{APP_VERSION}".center(58) + "|")
    print("|" + f"Copyright (c) {APP_YEAR} {APP_AUTHOR}".center(58) + "|")
    print("|" + f"License: LGPL-3.0".center(58) + "|")
    print("+" + "=" * 58 + "+")
    print(f"{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}[ERROR] {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING] {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.CYAN}[INFO] {message}{Colors.RESET}")

def get_input(prompt, default=None):
    if default:
        print(f"{Colors.CYAN}{prompt} [{default}]: {Colors.RESET}", end="")
        value = input().strip()
        return value if value else default
    else:
        print(f"{Colors.CYAN}{prompt}{Colors.RESET}", end="")
        return input().strip()

def get_number_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(get_input(prompt))
            if min_val <= value <= max_val:
                return value
            print_error(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print_error("Invalid input! Please enter a number.")

def select_folder_dialog():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = filedialog.askdirectory(title="Select Installation Directory")
        root.destroy()
        return folder_path
    except Exception as e:
        print_error(f"Could not open folder dialog: {e}")
        return None

def register_uninstall(install_path):
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, APP_AUTHOR)
        winreg.SetValueEx(key, "URLInfoAbout", 0, winreg.REG_SZ, "https://t.me/Noty_215")
        winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(install_path / MAIN_EXE))
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(install_path / UNINSTALL_EXE))
        winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ, f'"{install_path / UNINSTALL_EXE}" /S')
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, 0)
        
        winreg.CloseKey(key)
        print_success("Application registered in Windows Add/Remove Programs")
        return True
    except PermissionError:
        print_error("Permission denied - run as administrator")
        return False
    except Exception as e:
        print_error(f"Registry error: {e}")
        return False

def create_shortcut(path, target, description=""):
    ps = f'''$s = New-Object -ComObject WScript.Shell
$l = $s.CreateShortcut("{path}")
$l.TargetPath = "{target}"
$l.Description = "{description}"
$l.WorkingDirectory = "{Path(target).parent}"
$l.Save()'''
    subprocess.run(["powershell", "-Command", ps], capture_output=True)

def create_start_menu_shortcut(install_dir):
    start = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAI.lnk"
    create_shortcut(str(start), str(install_dir / MAIN_EXE), f"{APP_NAME} v{APP_VERSION}")

def create_desktop_shortcut(install_dir):
    desktop = Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAI.lnk"
    create_shortcut(str(desktop), str(install_dir / MAIN_EXE), f"{APP_NAME} v{APP_VERSION}")

def register_sendto_menu(install_dir):
    sendto = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAI.lnk"
    sendto.parent.mkdir(parents=True, exist_ok=True)
    create_shortcut(str(sendto), str(install_dir / MAIN_EXE), f"{APP_NAME} v{APP_VERSION}")

def get_free_space(path):
    try:
        if platform.system() == "Windows":
            drive = str(Path(path).drive)
            if not drive:
                drive = "C:"
            free_bytes = ctypes.c_ulonglong(0)
            ret = ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(drive + "\\"),
                ctypes.byref(free_bytes),
                None,
                None
            )
            if ret:
                return free_bytes.value
        import shutil
        return shutil.disk_usage(path).free
    except:
        return 1024 * 1024 * 1024 * 100

def check_requirements(install_path):
    print_info("Checking system requirements...")
    all_requirements_met = True
    
    try:
        install_path.mkdir(parents=True, exist_ok=True)
        free_space = get_free_space(install_path)
        free_space_gb = free_space / (1024 ** 3)
        print_info(f"Free disk space: {free_space_gb:.2f} GB")
        
        if free_space_gb < 4:
            print_error(f"Insufficient disk space! Need 4 GB, only {free_space_gb:.2f} GB available.")
            all_requirements_met = False
        else:
            print_success(f"Disk space OK (4 GB required)")
    except Exception as e:
        print_warning(f"Could not check disk space: {e}")
    
    return all_requirements_met

def copy_directory(src, dst):
    total_files = sum(1 for _ in src.rglob('*') if _.is_file())
    if total_files == 0:
        return
    
    copied = 0
    for item in src.rglob('*'):
        if item.is_file():
            rel_path = item.relative_to(src)
            dest_file = dst / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_file)
            copied += 1
            if copied % 10 == 0:
                percent = int(copied * 100 / total_files)
                print(f"\r  Progress: {percent}%", end="", flush=True)
    print(f"\r  Progress: 100%")

def get_executable_path(installer_dir):
    exe_path = installer_dir / MAIN_EXE
    if exe_path.exists():
        return exe_path
    
    exe_path = Path.cwd() / MAIN_EXE
    if exe_path.exists():
        return exe_path
    
    temp_dir = Path(tempfile.gettempdir())
    for temp_subdir in temp_dir.iterdir():
        if temp_subdir.is_dir() and "MEI" in temp_subdir.name:
            exe_path = temp_subdir / MAIN_EXE
            if exe_path.exists():
                return exe_path
    
    if getattr(sys, 'frozen', False):
        exe_path = Path(sys.executable).parent / MAIN_EXE
        if exe_path.exists():
            return exe_path
    
    return None

def get_uninstaller_path(installer_dir):
    uninstaller_path = installer_dir / UNINSTALL_EXE
    if uninstaller_path.exists():
        return uninstaller_path
    
    uninstaller_path = Path.cwd() / UNINSTALL_EXE
    if uninstaller_path.exists():
        return uninstaller_path
    
    temp_dir = Path(tempfile.gettempdir())
    for temp_subdir in temp_dir.iterdir():
        if temp_subdir.is_dir() and "MEI" in temp_subdir.name:
            uninstaller_path = temp_subdir / UNINSTALL_EXE
            if uninstaller_path.exists():
                return uninstaller_path
    
    if getattr(sys, 'frozen', False):
        uninstaller_path = Path(sys.executable).parent / UNINSTALL_EXE
        if uninstaller_path.exists():
            return uninstaller_path
    
    return None

def get_directory_size(path):
    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            total += item.stat().st_size
    return total / (1024 * 1024)

def install():
    if not is_admin():
        print_warning("Administrator privileges required for registry registration!")
        print_info("Installer will now restart with administrator privileges...")
        time.sleep(2)
        if run_as_admin():
            sys.exit(0)
        else:
            print_error("Failed to elevate privileges. Installation will continue without registry registration.")
    
    print_header()
    
    if getattr(sys, 'frozen', False):
        installer_dir = Path(sys.executable).parent
        print_info(f"Running from: {installer_dir}")
    else:
        installer_dir = Path(__file__).parent
    
    default_path = "C:\\NotYCaptionGenAI"
    
    while True:
        print(f"\n{Colors.BOLD}Installation Directory{Colors.RESET}")
        print(f"  Default location: {default_path}")
        print(f"\n  1) Continue with this location")
        print(f"  2) Change location (Browse folder dialog)")
        print(f"  0) Cancel installation")
        
        choice = get_number_input("\nChoose option (0-2): ", 0, 2)
        
        if choice == 0:
            print_info("Installation cancelled.")
            return False
        elif choice == 1:
            install_path = Path(default_path)
            break
        else:
            selected_path = select_folder_dialog()
            if selected_path:
                install_path = Path(selected_path) / "NotYCaptionGenAI"
                print_success(f"Selected: {install_path}")
                
                print_header()
                print(f"\n{Colors.BOLD}Confirm Installation{Colors.RESET}")
                print(f"  Installation Path: {install_path}")
                print(f"\n  1) Yes, proceed with installation")
                print(f"  2) No, cancel installation")
                print(f"  0) Back to path selection")
                
                confirm_choice = get_number_input("\nChoose option (0-2): ", 0, 2)
                
                if confirm_choice == 0:
                    continue
                elif confirm_choice == 1:
                    break
                else:
                    print_info("Installation cancelled.")
                    return False
            else:
                print_error("No folder selected. Please try again.")
                continue
    
    print_header()
    if not check_requirements(install_path):
        print_error("\nSystem requirements not met!")
        print_info("Requirements: 4 GB free disk space")
        response = input(f"{Colors.CYAN}Continue anyway? (y/n): {Colors.RESET}").lower()
        if response not in ['y', 'yes']:
            return False
    
    print_header()
    print_info(f"Installing to: {install_path}")
    print_info("This may take a few minutes...")
    print()
    
    try:
        install_path.mkdir(parents=True, exist_ok=True)
        
        exe_file = get_executable_path(installer_dir)
        if exe_file and exe_file.exists():
            print_info("Copying main executable...")
            shutil.copy2(exe_file, install_path / MAIN_EXE)
            print_success("Main executable copied")
        else:
            print_error("Main executable not found!")
            return False
        
        uninstaller_file = get_uninstaller_path(installer_dir)
        if uninstaller_file and uninstaller_file.exists():
            print_info("Copying uninstaller...")
            shutil.copy2(uninstaller_file, install_path / UNINSTALL_EXE)
            print_success("Uninstaller copied")
        
        # Copy resources
        resources_dir = installer_dir / "resources"
        if not resources_dir.exists():
            temp_dir = Path(tempfile.gettempdir())
            for temp_subdir in temp_dir.iterdir():
                if temp_subdir.is_dir() and "MEI" in temp_subdir.name:
                    resources_dir = temp_subdir / "resources"
                    if resources_dir.exists():
                        break
        
        if resources_dir and resources_dir.exists():
            print_info("Copying resources...")
            dest_resources = install_path / "resources"
            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            copy_directory(resources_dir, dest_resources)
            print_success("Resources copied")
        
        # Copy ffmpeg
        ffmpeg_dir = installer_dir / "ffmpeg"
        if not ffmpeg_dir.exists():
            temp_dir = Path(tempfile.gettempdir())
            for temp_subdir in temp_dir.iterdir():
                if temp_subdir.is_dir() and "MEI" in temp_subdir.name:
                    ffmpeg_dir = temp_subdir / "ffmpeg"
                    if ffmpeg_dir.exists():
                        break
        
        if ffmpeg_dir and ffmpeg_dir.exists():
            print_info("Copying ffmpeg...")
            dest_ffmpeg = install_path / "ffmpeg"
            if dest_ffmpeg.exists():
                shutil.rmtree(dest_ffmpeg)
            copy_directory(ffmpeg_dir, dest_ffmpeg)
            print_success("ffmpeg copied")
        
        # Copy models
        models_dir = installer_dir / "models"
        if not models_dir.exists():
            temp_dir = Path(tempfile.gettempdir())
            for temp_subdir in temp_dir.iterdir():
                if temp_subdir.is_dir() and "MEI" in temp_subdir.name:
                    models_dir = temp_subdir / "models"
                    if models_dir.exists():
                        break
        
        if models_dir and models_dir.exists():
            print_info("Copying models...")
            dest_models = install_path / "models"
            if dest_models.exists():
                shutil.rmtree(dest_models)
            copy_directory(models_dir, dest_models)
            print_success("Models copied")
        
        # Create shortcuts
        print_info("Creating shortcuts...")
        create_start_menu_shortcut(install_path)
        create_desktop_shortcut(install_path)
        register_sendto_menu(install_path)
        print_success("Shortcuts created")
        
        # Register in Windows
        print_info("Registering in Windows...")
        register_uninstall(install_path)
        
        print_header()
        print_success(f"Installation Complete!")
        print_info(f"Installed to: {install_path}")
        print_info(f"Size: {get_directory_size(install_path):.2f} MB")
        print()
        print_info(f"Application: {install_path / MAIN_EXE}")
        print_info("You can now run NotYCaptionGenAI.exe from the installation directory")
        print_info("Or right-click any video/audio file and select 'Send To' > 'NotYCaptionGenAi'")
        print_info("To uninstall, use Windows Add/Remove Programs")
        
        return True
        
    except Exception as e:
        print_error(f"Installation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = install()
    
    if success:
        print_success("\nInstallation completed successfully!")
    else:
        print_error("\nInstallation failed!")
    
    input("\nPress Enter to exit...")