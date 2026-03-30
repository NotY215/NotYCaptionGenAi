#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Uninstaller v4.4 (Console)
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import time
import platform
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

if platform.system() == "Windows":
    os.system('color')

def print_header():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║              NotY Caption Generator AI Uninstaller v4.4       ║")
    print("║                 Copyright (c) 2026 NotY215                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")

def get_install_path():
    """Get install path from registry"""
    try:
        ps = 'Get-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "InstallPath" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty InstallPath'
        result = subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
        if result.stdout.strip():
            return Path(result.stdout.strip())
    except:
        pass
    return None

def get_directory_size(path):
    """Get directory size in MB"""
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except:
        pass
    return total / (1024 * 1024)

def uninstall():
    print_header()
    print_info("Starting uninstallation process...")
    print()
    
    # Get install path from registry
    install_path = get_install_path()
    
    if not install_path or not install_path.exists():
        print_error("Installation not found!")
        print_info("No registry entry found for NotY Caption Generator AI.")
        print_info("If the application was installed manually, please delete the folder manually.")
        return False
    
    print_info(f"Found installation at: {install_path}")
    print_info(f"Installation size: {get_directory_size(install_path):.2f} MB")
    print()
    
    # Confirm uninstallation
    print(f"{Colors.YELLOW}⚠ WARNING: This will permanently remove NotY Caption Generator AI{Colors.RESET}")
    print(f"{Colors.YELLOW}   and all its components from your computer.{Colors.RESET}")
    print()
    
    response = input(f"{Colors.CYAN}Are you sure you want to uninstall? (y/n): {Colors.RESET}").lower()
    if response not in ['y', 'yes']:
        print_info("Uninstallation cancelled.")
        return False
    
    print()
    
    try:
        # Remove installation directory
        print_info("Removing application files...")
        shutil.rmtree(install_path, ignore_errors=True)
        print_success("Application files removed")
        
        # Remove shortcuts
        print_info("Removing shortcuts...")
        shortcuts = [
            Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAi.lnk",
            Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAi.lnk",
            Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAi.lnk"
        ]
        for shortcut in shortcuts:
            if shortcut.exists():
                shortcut.unlink()
                print(f"  Removed: {shortcut.name}")
        print_success("Shortcuts removed")
        
        # Remove registry entries
        print_info("Removing registry entries...")
        subprocess.run(
            ["powershell", "-Command", 'Remove-Item -Path "HKCU:\\Software\\NotYCaptionGenAi" -Recurse -Force -ErrorAction SilentlyContinue'],
            capture_output=True
        )
        print_success("Registry entries removed")
        
        print()
        print_success("Uninstallation complete!")
        print_info("NotY Caption Generator AI has been removed from your computer.")
        
        # Self-delete
        print()
        print_info("The uninstaller will now delete itself...")
        time.sleep(2)
        
        # Create a batch file to delete the uninstaller
        if getattr(sys, 'frozen', False):
            uninstaller_path = Path(sys.executable)
            bat_content = f'''@echo off
timeout /t 1 /nobreak >nul
del "{uninstaller_path}" 2>nul
exit
'''
            bat_path = Path(os.environ["TEMP"]) / "delete_uninstaller.bat"
            with open(bat_path, 'w') as f:
                f.write(bat_content)
            subprocess.Popen([str(bat_path)], shell=True)
        
        return True
        
    except Exception as e:
        print_error(f"Uninstallation failed: {e}")
        return False

if __name__ == "__main__":
    success = uninstall()
    
    if success:
        print_success("\nUninstallation completed successfully!")
    else:
        print_error("\nUninstallation failed!")
    
    input("\nPress Enter to exit...")