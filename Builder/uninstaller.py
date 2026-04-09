#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Uninstaller v5.2
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_DISPLAY_NAME = "NotY Caption Generator AI"

def uninstall():
    print("=" * 60)
    print(f"Uninstalling {APP_DISPLAY_NAME}")
    print("=" * 60)
    
    # Get install path from registry
    install_path = None
    try:
        import winreg
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
        install_path, _ = winreg.QueryValueEx(key, "UninstallString")
        install_path = Path(install_path).parent
        winreg.CloseKey(key)
    except:
        pass
    
    if not install_path or not install_path.exists():
        # Default path
        install_path = Path("C:\\NotY Caption Generator AI")
    
    print(f"\nFound installation at: {install_path}")
    
    response = input(f"\nAre you sure you want to uninstall? (y/n): ").lower()
    if response not in ['y', 'yes']:
        print("Uninstall cancelled.")
        return
    
    print("\nRemoving files...")
    
    # Remove installation directory
    try:
        shutil.rmtree(install_path, ignore_errors=True)
        print(f"  Removed: {install_path}")
    except:
        pass
    
    # Remove shortcuts
    shortcuts = [
        Path(os.environ.get('USERPROFILE', '')) / "Desktop" / f"{APP_DISPLAY_NAME}.lnk",
        Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / f"{APP_DISPLAY_NAME}.lnk",
    ]
    
    for shortcut in shortcuts:
        if shortcut.exists():
            shortcut.unlink()
            print(f"  Removed: {shortcut.name}")
    
    # Remove registry
    try:
        import winreg
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        print("  Removed registry entries")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("Uninstall Complete!")
    print("=" * 60)
    
    # Self-delete
    if getattr(sys, 'frozen', False):
        bat_path = Path(os.environ.get('TEMP', '.')) / f"delete_uninstaller.bat"
        with open(bat_path, 'w') as f:
            f.write(f'''@echo off
timeout /t 2 /nobreak >nul
del "{sys.executable}" 2>nul
del "%~f0" 2>nul
''')
        subprocess.Popen([str(bat_path)], shell=True)

if __name__ == "__main__":
    uninstall()
    input("\nPress Enter to exit...")