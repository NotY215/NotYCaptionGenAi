#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Uninstaller v6.1
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import ctypes
from pathlib import Path
import winreg

APP_NAME = "NotYCaptionGenAI"
APP_DISPLAY_NAME = "NotY Caption Generator AI"

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

def remove_registry():
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        return True
    except:
        return False

def remove_shortcuts():
    try:
        # Remove Start Menu shortcut
        start = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAI.lnk"
        if start.exists():
            start.unlink()
        
        # Remove Desktop shortcut
        desktop = Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAI.lnk"
        if desktop.exists():
            desktop.unlink()
        
        # Remove Send To shortcut
        sendto = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAI.lnk"
        if sendto.exists():
            sendto.unlink()
        
        return True
    except:
        return False

def main():
    print("=" * 60)
    print(f"  {APP_DISPLAY_NAME} Uninstaller v6.1")
    print("=" * 60)
    
    if not is_admin():
        print("\n[WARNING] Administrator privileges required!")
        print("Uninstaller will now restart with administrator privileges...")
        if run_as_admin():
            sys.exit(0)
        else:
            print("[ERROR] Failed to elevate privileges.")
            input("Press Enter to exit...")
            sys.exit(1)
    
    # Get installation path from registry or current location
    install_path = None
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        install_path = Path(winreg.QueryValueEx(key, "InstallLocation")[0])
        winreg.CloseKey(key)
    except:
        # If not in registry, try current directory
        if getattr(sys, 'frozen', False):
            install_path = Path(sys.executable).parent.parent
        else:
            install_path = Path.cwd()
    
    print(f"\n[INFO] Installation found at: {install_path}")
    print("\nThis will remove:")
    print("  - Main executable")
    print("  - Uninstaller")
    print("  - resources folder")
    print("  - ffmpeg folder")
    print("  - models folder (Whisper models)")
    print("  - pretrained_models folder (Spleeter models)")
    print("  - Desktop and Start Menu shortcuts")
    print("  - Send To menu entry")
    print("  - Windows registry entry")
    
    response = input("\n[?] Are you sure you want to uninstall? (y/n): ").lower()
    if response not in ['y', 'yes']:
        print("[INFO] Uninstall cancelled.")
        input("Press Enter to exit...")
        return
    
    print("\n[INFO] Removing files...")
    
    # Remove files and folders
    items_to_remove = [
        install_path / "NotYCaptionGenAI.exe",
        install_path / "NotYCaptionGenAI_Uninstaller.exe",
        install_path / "resources",
        install_path / "ffmpeg",
        install_path / "models",
        install_path / "pretrained_models",
        install_path / "cache",
    ]
    
    for item in items_to_remove:
        if item.exists():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"  Removed: {item}")
                else:
                    item.unlink()
                    print(f"  Removed: {item}")
            except Exception as e:
                print(f"  Failed to remove {item}: {e}")
    
    # Remove the installation directory if empty
    try:
        if install_path.exists() and not any(install_path.iterdir()):
            install_path.rmdir()
            print(f"  Removed directory: {install_path}")
    except:
        pass
    
    print("\n[INFO] Removing shortcuts...")
    remove_shortcuts()
    
    print("\n[INFO] Removing registry entries...")
    if remove_registry():
        print("  Registry entries removed")
    else:
        print("  No registry entries found")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Uninstallation completed!")
    print("=" * 60)
    
    # Self-delete the uninstaller
    try:
        if getattr(sys, 'frozen', False):
            current_file = Path(sys.executable)
            if current_file.exists():
                batch_file = current_file.parent / "del_uninstaller.bat"
                with open(batch_file, 'w') as f:
                    f.write(f'''@echo off
timeout /t 2 /nobreak > nul
del "{current_file}" > nul 2>&1
del "%~f0" > nul 2>&1
''')
                subprocess.Popen(['cmd', '/c', str(batch_file)], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()