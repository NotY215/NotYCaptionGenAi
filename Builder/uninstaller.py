#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Uninstaller v7.1
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import ctypes
import time
from pathlib import Path
import winreg


APP_NAME = "NotY Caption Generator AI"
APP_PUBLISHER = "NotY215"
PACKAGES_FOLDER = "_pythonPackages_"
APP_DATA_FOLDER = Path(os.environ.get('APPDATA', Path.home())) / 'NotYCaptionGenAI'
REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"


class Colors:
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'


def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Restart the script with administrator privileges"""
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return True
    except:
        return False


def remove_registry():
    """Remove registry entries"""
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
        print(f"  {Colors.GREEN}Removed registry entries{Colors.ENDC}")
        return True
    except:
        return False


def remove_shortcuts():
    """Remove all shortcuts"""
    paths = [
        Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAI.lnk",
        Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAI.lnk",
        Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAI.lnk",
    ]
    
    for p in paths:
        if p.exists():
            p.unlink()
            print(f"  {Colors.GREEN}Removed shortcut: {p.name}{Colors.ENDC}")


def remove_appdata_models():
    """Remove models from AppData"""
    try:
        if APP_DATA_FOLDER.exists():
            shutil.rmtree(APP_DATA_FOLDER, ignore_errors=True)
            print(f"  {Colors.GREEN}Removed AppData models{Colors.ENDC}")
            return True
    except:
        pass
    return False


def remove_from_path(install_path):
    """Remove installation directory from system PATH"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                             r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                             0, winreg.KEY_READ | winreg.KEY_WRITE)
        
        current_path = winreg.QueryValueEx(key, "Path")[0]
        install_path_str = str(install_path)
        
        if install_path_str in current_path:
            # Remove the path
            paths = current_path.split(';')
            paths = [p for p in paths if p and p != install_path_str]
            new_path = ';'.join(paths)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"  {Colors.GREEN}Removed from system PATH{Colors.ENDC}")
        
        winreg.CloseKey(key)
    except Exception as e:
        print(f"  {Colors.WARNING}Could not remove from PATH: {e}{Colors.ENDC}")


def create_self_delete_batch(install_path):
    """Create batch file to delete installation folder and itself"""
    batch_file = install_path / "del_uninstaller.bat"
    batch_content = f'''@echo off
timeout /t 2 /nobreak > nul
echo Removing installation directory...
cd /d C:\\
rd /s /q "{install_path}" 2>nul
echo Removing AppData models...
rd /s /q "{APP_DATA_FOLDER}" 2>nul
echo Uninstall complete.
del "%~f0" 2>nul
exit
'''
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    return batch_file


def main():
    """Main uninstaller routine"""
    print("=" * 60)
    print(f"  {APP_NAME} Uninstaller v7.1")
    print(f"  Publisher: {APP_PUBLISHER}")
    print("=" * 60)
    
    # Check for admin privileges
    if not is_admin():
        print("\nAdministrator privileges required!")
        if run_as_admin():
            sys.exit(0)
        else:
            print("Failed to get admin privileges. Uninstall cancelled.")
            sys.exit(1)
    
    # Find installation path
    install_path = None
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ)
        install_path = Path(winreg.QueryValueEx(key, "InstallLocation")[0])
        winreg.CloseKey(key)
    except:
        # Try common locations
        possible_paths = [
            Path("C:\\NotYCaptionGenAI"),
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "NotYCaptionGenAI",
            Path.cwd()
        ]
        
        for p in possible_paths:
            if (p / "NotYCaptionGenAI.exe").exists():
                install_path = p
                break
    
    if not install_path or not install_path.exists():
        print("\n[ERROR] Installation not found!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"\nInstallation found at: {install_path}")
    confirm = input("\nAre you sure you want to uninstall? (y/n): ").lower()
    
    if confirm != 'y':
        print("Uninstall cancelled.")
        sys.exit(0)
    
    # Remove files and folders
    print("\nRemoving files...")
    items = [
        install_path / "NotYCaptionGenAI.exe",
        install_path / "Uninstaller.exe",
        install_path / PACKAGES_FOLDER,
        install_path / "resources",
        install_path / "ffmpeg",
        install_path / "pretrained_models",
    ]
    
    for item in items:
        if item.exists():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                print(f"  Removed: {item.name if item.is_file() else item.name}")
            except Exception as e:
                print(f"  Warning: Could not remove {item}: {e}")
    
    # Remove from PATH
    remove_from_path(install_path)
    
    # Remove shortcuts
    print("\nRemoving shortcuts...")
    remove_shortcuts()
    
    # Remove registry
    print("\nRemoving registry entries...")
    remove_registry()
    
    # Remove AppData models (ask user)
    print("\nRemove AppData models?")
    print(f"  Location: {APP_DATA_FOLDER}")
    remove_models = input("  Remove models? (y/n): ").lower()
    if remove_models == 'y':
        remove_appdata_models()
    else:
        print("  Keeping AppData models for future installations")
    
    print(f"\n{Colors.GREEN}{'='*50}{Colors.ENDC}")
    print(f"{Colors.GREEN}Uninstallation completed!{Colors.ENDC}")
    print(f"{Colors.GREEN}{'='*50}{Colors.ENDC}")
    
    # Create batch file for self-deletion
    batch_file = create_self_delete_batch(install_path)
    subprocess.Popen(['cmd', '/c', str(batch_file)], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(1)
    sys.exit(0)


if __name__ == "__main__":
    main()