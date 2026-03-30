#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Installer v4.4 (Console)
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
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'

if platform.system() == "Windows":
    os.system('color')

def draw_turtle_logo():
    """Draw colorful turtle logo"""
    logo = f"""
{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}
                    ╔═══════════════════════════════════════════════════╗
                    ║                    🐢 NOTY AI 🐢                   ║
                    ║         The Fastest Subtitle Generator           ║
                    ║            Copyright (c) 2026 NotY215            ║
                    ╚═══════════════════════════════════════════════════╝
{Colors.RESET}

{Colors.CYAN}    ╔═══════════════════════════════════════════════════════════════════╗
    ║                 NOTY CAPTION GENERATOR INSTALLER v4.4                 ║
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
              ║     🚀 FAST • EASY • POWERFUL SUBTITLES 🚀      ║
              ╚══════════════════════════════════════════════╝{Colors.RESET}
"""
    print(logo)

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")

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

def get_free_space(path):
    if platform.system() == "Windows":
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(str(path)), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        stat = os.statvfs(path)
        return stat.f_bavail * stat.f_frsize

def get_total_ram():
    if platform.system() == "Windows":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        
        memory_status = MEMORYSTATUSEX()
        memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
        return memory_status.ullTotalPhys
    return 0

def check_requirements(install_path):
    print_info("Checking system requirements...")
    
    try:
        free_space = get_free_space(install_path)
        free_space_gb = free_space / (1024 ** 3)
        print_info(f"Free disk space: {free_space_gb:.2f} GB")
        
        if free_space_gb < 3:
            print_error(f"Insufficient disk space! Need 3 GB, but only {free_space_gb:.2f} GB available.")
            return False
        print_success(f"Disk space OK (3 GB required)")
    except Exception as e:
        print_warning(f"Could not check disk space: {e}")
    
    try:
        total_ram = get_total_ram()
        total_ram_gb = total_ram / (1024 ** 3)
        print_info(f"Total RAM: {total_ram_gb:.2f} GB")
        
        if total_ram_gb < 2:
            print_error(f"Insufficient RAM! Need 2 GB, but only {total_ram_gb:.2f} GB available.")
            return False
        print_success(f"RAM OK (2 GB required)")
    except Exception as e:
        print_warning(f"Could not check RAM: {e}")
    
    return True

def copy_directory(src, dst):
    total_files = sum(1 for _ in src.rglob('*') if _.is_file())
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

def create_uninstaller(install_dir):
    uninstaller_content = f'''@echo off
echo ============================================================
echo   NotY Caption Generator AI Uninstaller v4.4
echo   Copyright (c) 2026 NotY215
echo ============================================================
echo.

echo Removing files...
rmdir /s /q "{install_dir}" 2>nul

echo Removing shortcuts...
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\NotYCaptionGenAi.lnk" 2>nul
del "%USERPROFILE%\\Desktop\\NotYCaptionGenAi.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\SendTo\\NotYCaptionGenAi.lnk" 2>nul

echo Removing registry entries...
reg delete "HKCU\\Software\\NotYCaptionGenAi" /f 2>nul

echo.
echo ============================================================
echo Uninstallation complete!
echo ============================================================
echo.
echo The uninstaller will now delete itself...
timeout /t 2 /nobreak >nul
del "%~f0" 2>nul
exit
'''
    uninstaller_path = install_dir / "uninstall.bat"
    with open(uninstaller_path, 'w', encoding='utf-8') as f:
        f.write(uninstaller_content)

def create_shortcut(path, target):
    ps = f'''$s = New-Object -ComObject WScript.Shell
$l = $s.CreateShortcut("{path}")
$l.TargetPath = "{target}"
$l.Save()'''
    subprocess.run(["powershell", "-Command", ps], capture_output=True)

def create_start_menu_shortcut(install_dir):
    start = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAi.lnk"
    create_shortcut(str(start), str(install_dir / "NotYCaptionGenAI.exe"))

def create_desktop_shortcut(install_dir):
    desktop = Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAi.lnk"
    create_shortcut(str(desktop), str(install_dir / "NotYCaptionGenAI.exe"))

def register_sendto_menu(install_dir):
    sendto = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAi.lnk"
    sendto.parent.mkdir(parents=True, exist_ok=True)
    create_shortcut(str(sendto), str(install_dir / "NotYCaptionGenAI.exe"))

def register_application(install_dir):
    reg = f'''
New-Item -Path "HKCU:\\Software\\NotYCaptionGenAi" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "InstallPath" -Value "{install_dir}"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "Version" -Value "4.4"
'''
    subprocess.run(["powershell", "-Command", reg], capture_output=True)

def get_directory_size(path):
    total = 0
    for item in path.rglob('*'):
        if item.is_file():
            total += item.stat().st_size
    return total / (1024 * 1024)

def install():
    draw_turtle_logo()
    
    # Get installer directory
    if getattr(sys, 'frozen', False):
        installer_dir = Path(sys.executable).parent
    else:
        installer_dir = Path(__file__).parent
    
    default_path = "C:\\NotYCaptionGenAI"
    
    while True:
        print(f"\n{Colors.BOLD}Installation Directory{Colors.RESET}")
        print(f"  Default location: {default_path}")
        print(f"\n  1) Continue with this location")
        print(f"  2) Change location")
        print(f"  0) Cancel installation")
        
        choice = get_number_input("\n➤ Choose option (0-2): ", 0, 2)
        
        if choice == 0:
            print_info("Installation cancelled.")
            return False
        elif choice == 1:
            install_path = Path(default_path)
            break
        else:
            while True:
                draw_turtle_logo()
                print(f"\n{Colors.BOLD}Enter Installation Path{Colors.RESET}")
                print(f"  Example: D:\\Applications\\NotYCaptionGenAI")
                print(f"  0) Back to previous menu")
                
                path_input = get_input("\n➤ Installation path: ")
                
                if path_input == "0":
                    break
                
                install_path = Path(path_input.strip().strip('"'))
                
                try:
                    install_path.mkdir(parents=True, exist_ok=True)
                    print_success(f"Directory created/verified: {install_path}")
                    
                    draw_turtle_logo()
                    print(f"\n{Colors.BOLD}Confirm Installation{Colors.RESET}")
                    print(f"  Installation Path: {install_path}")
                    print(f"\n  1) Yes, proceed with installation")
                    print(f"  2) No, cancel installation")
                    print(f"  0) Back to path selection")
                    
                    confirm_choice = get_number_input("\n➤ Choose option (0-2): ", 0, 2)
                    
                    if confirm_choice == 0:
                        continue
                    elif confirm_choice == 1:
                        break
                    else:
                        print_info("Installation cancelled.")
                        return False
                        
                except Exception as e:
                    print_error(f"Cannot create directory: {e}")
                    continue
    
    draw_turtle_logo()
    if not check_requirements(install_path):
        print_error("\nSystem requirements not met!")
        print_info("Requirements: 3 GB free disk space, 2 GB RAM")
        input("\nPress Enter to exit...")
        return False
    
    draw_turtle_logo()
    print_info(f"Installing to: {install_path}")
    print_info("This may take a few minutes...")
    print()
    
    try:
        install_path.mkdir(parents=True, exist_ok=True)
        
        # Copy main executable
        exe_file = installer_dir / "NotYCaptionGenAI.exe"
        if exe_file.exists():
            print_info("Copying main executable...")
            shutil.copy2(exe_file, install_path / "NotYCaptionGenAI.exe")
            print_success("Main executable copied")
        else:
            print_error("Main executable not found!")
            return False
        
        # Copy resources
        resources_dir = installer_dir / "resources"
        if resources_dir.exists():
            print_info("Copying resources...")
            dest_resources = install_path / "resources"
            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            copy_directory(resources_dir, dest_resources)
            print_success("Resources copied")
        
        # Copy models if they exist
        models_dir = installer_dir / "models"
        if models_dir.exists():
            print_info("Copying models...")
            dest_models = install_path / "models"
            if dest_models.exists():
                shutil.rmtree(dest_models)
            copy_directory(models_dir, dest_models)
            print_success("Models copied")
        
        # Create uninstaller
        print_info("Creating uninstaller...")
        create_uninstaller(install_path)
        print_success("Uninstaller created")
        
        # Create shortcuts
        print_info("Creating shortcuts...")
        create_start_menu_shortcut(install_path)
        create_desktop_shortcut(install_path)
        register_sendto_menu(install_path)
        print_success("Shortcuts created")
        
        # Register application
        print_info("Registering application...")
        register_application(install_path)
        print_success("Application registered")
        
        draw_turtle_logo()
        print_success(f"Installation Complete!")
        print_info(f"Installed to: {install_path}")
        print_info(f"Size: {get_directory_size(install_path):.2f} MB")
        print()
        print_info("You can now run NotYCaptionGenAI.exe from the installation directory")
        print_info("Or right-click any video/audio file and select 'Send To' > 'NotYCaptionGenAi'")
        
        return True
        
    except Exception as e:
        print_error(f"Installation failed: {e}")
        return False

if __name__ == "__main__":
    success = install()
    
    if success:
        print_success("\nInstallation completed successfully!")
    else:
        print_error("\nInstallation failed!")
    
    input("\nPress Enter to exit...")