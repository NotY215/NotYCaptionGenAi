#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Uninstaller v7.1
Removes installation, AppData models, and PATH entries
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
APP_DATA_FOLDER = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'NotYCaptionGenAI')
REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"

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

def remove_from_path(install_path):
    """Remove application from system PATH"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                             0, winreg.KEY_ALL_ACCESS)
        current_path, _ = winreg.QueryValueEx(key, "Path")
        app_path = str(install_path)
        
        if app_path in current_path:
            new_path = current_path.replace(app_path, "").replace(";;", ";").strip(";")
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            
            # Broadcast environment change
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment")
            return True
    except:
        pass
    return False

def remove_registry():
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH)
        return True
    except:
        return False

def remove_shortcuts():
    paths = [
        Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAI.lnk",
        Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAI.lnk",
        Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAI.lnk",
    ]
    for p in paths:
        if p.exists():
            p.unlink()

def remove_appdata_models():
    """Remove models from AppData"""
    try:
        appdata_path = Path(APP_DATA_FOLDER)
        if appdata_path.exists():
            shutil.rmtree(appdata_path, ignore_errors=True)
            return True
    except:
        pass
    return False

def create_self_delete_batch(install_path, current_file):
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
    print("=" * 60)
    print(f"  {APP_NAME} Uninstaller v7.1")
    print(f"  Publisher: {APP_PUBLISHER}")
    print("=" * 60)
    
    if not is_admin():
        print("\nAdmin privileges required!")
        if run_as_admin():
            sys.exit(0)
    
    install_path = None
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_READ)
        install_path = Path(winreg.QueryValueEx(key, "InstallLocation")[0])
        winreg.CloseKey(key)
    except:
        possible = [Path("C:\\NotYCaptionGenAI"), Path.cwd()]
        for p in possible:
            if (p / "NotYCaptionGenAI.exe").exists():
                install_path = p
                break
    
    if not install_path or not install_path.exists():
        print("[ERROR] Installation not found!")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"\nInstallation found at: {install_path}")
    confirm = input("\nAre you sure you want to uninstall? (y/n): ").lower()
    if confirm != 'y':
        print("Uninstall cancelled.")
        return
    
    print("\nRemoving files...")
    items = [
        install_path / "NotYCaptionGenAI.exe",
        install_path / "Uninstaller.exe",
        install_path / PACKAGES_FOLDER,
        install_path / "resources",
        install_path / "ffmpeg",
        install_path / "models",
        install_path / "pretrained_models",
        install_path / "cache",
    ]
    
    for item in items:
        if item.exists():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                print(f"  Removed: {item.name if item.is_file() else item.name}")
            except:
                pass
    
    print("\nRemoving AppData models...")
    remove_appdata_models()
    
    print("\nRemoving shortcuts...")
    remove_shortcuts()
    
    print("\nRemoving from PATH...")
    remove_from_path(install_path)
    
    print("\nRemoving registry entries...")
    remove_registry()
    
    print("\n[SUCCESS] Uninstallation completed!")
    
    # Create batch file to delete installation folder and self
    current_file = Path(sys.executable)
    batch_file = create_self_delete_batch(install_path, current_file)
    
    subprocess.Popen(['cmd', '/c', str(batch_file)], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(1)
    sys.exit(0)

if __name__ == "__main__":
    main()