#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Installer v5.2
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_DISPLAY_NAME = "NotY Caption Generator AI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"

def create_windows_installer():
    """Create a self-extracting installer using IExpress or batch"""
    print("\n[1/2] Creating Windows installer...")
    
    base_dir = Path(__file__).parent.parent
    dist_dir = base_dir / "dist"
    
    # Create installer script
    installer_content = f'''@echo off
title {APP_DISPLAY_NAME} v{APP_VERSION} Installer
color 0A

echo ============================================================
echo    {APP_DISPLAY_NAME} v{APP_VERSION} Installer
echo    Copyright (c) 2026 {APP_AUTHOR}
echo ============================================================
echo.

:: Check admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator rights required!
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

:: Installation path
set /p "INSTALL_PATH=Installation directory [C:\\{APP_DISPLAY_NAME}]: "
if "%INSTALL_PATH%"=="" set INSTALL_PATH=C:\\{APP_DISPLAY_NAME}

echo.
echo Installing to: %INSTALL_PATH%
echo.

:: Create directories
mkdir "%INSTALL_PATH%" 2>nul
mkdir "%INSTALL_PATH%\\ffmpeg" 2>nul
mkdir "%INSTALL_PATH%\\resources" 2>nul
mkdir "%INSTALL_PATH%\\models" 2>nul

:: Copy files
copy /Y "{APP_NAME}.exe" "%INSTALL_PATH%\\" >nul
xcopy /E /I /Y "ffmpeg" "%INSTALL_PATH%\\ffmpeg\\" >nul
xcopy /E /I /Y "resources" "%INSTALL_PATH%\\resources\\" >nul

:: Create shortcuts
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\\Desktop\\{APP_DISPLAY_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $SC.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_DISPLAY_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $SC.Save()"

:: Registry
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "DisplayName" /d "{APP_DISPLAY_NAME} v{APP_VERSION}" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "UninstallString" /d "%INSTALL_PATH%\\Uninstall.exe" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "Publisher" /d "{APP_AUTHOR}" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "DisplayVersion" /d "{APP_VERSION}" /f

:: Create uninstaller
echo @echo off > "%INSTALL_PATH%\\Uninstall.bat"
echo title {APP_DISPLAY_NAME} Uninstaller >> "%INSTALL_PATH%\\Uninstall.bat"
echo echo Uninstalling {APP_DISPLAY_NAME}... >> "%INSTALL_PATH%\\Uninstall.bat"
echo rmdir /s /q "%INSTALL_PATH%" >> "%INSTALL_PATH%\\Uninstall.bat"
echo del "%%USERPROFILE%%\\Desktop\\{APP_DISPLAY_NAME}.lnk" >> "%INSTALL_PATH%\\Uninstall.bat"
echo del "%%APPDATA%%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_DISPLAY_NAME}.lnk" >> "%INSTALL_PATH%\\Uninstall.bat"
echo reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /f >> "%INSTALL_PATH%\\Uninstall.bat"
echo echo Uninstall complete! >> "%INSTALL_PATH%\\Uninstall.bat"
echo pause >> "%INSTALL_PATH%\\Uninstall.bat"

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Installed to: %INSTALL_PATH%
echo.
echo You can now run {APP_DISPLAY_NAME} from Desktop or Start Menu
echo.
pause
'''
    
    installer_bat = dist_dir / "Install.bat"
    with open(installer_bat, 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print(f"[OK] Installer created: {installer_bat}")
    return installer_bat

def create_portable_zip():
    """Create portable ZIP archive"""
    print("\n[2/2] Creating portable ZIP...")
    
    base_dir = Path(__file__).parent.parent
    dist_dir = base_dir / "dist"
    zip_name = dist_dir / f"{APP_NAME}_Portable_v{APP_VERSION}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        exe_file = dist_dir / f"{APP_NAME}.exe"
        if exe_file.exists():
            zipf.write(exe_file, f"{APP_NAME}.exe")
        
        # Add folders
        for folder in ['ffmpeg', 'resources']:
            folder_path = dist_dir / folder
            if folder_path.exists():
                for file in folder_path.rglob('*'):
                    if file.is_file():
                        zipf.write(file, f"{folder}/{file.relative_to(folder_path)}")
        
        # Add README
        readme = f'''NotY Caption Generator AI v{APP_VERSION}
=====================================

PORTABLE VERSION - No installation required!

HOW TO USE:
1. Extract all files to any folder
2. Double-click {APP_NAME}.exe
3. First run will download Whisper models automatically

FEATURES:
- YouTube video captioning
- Local video/audio captioning
- 6 languages + auto detect
- Smart line breaking
- Lyrics search

REQUIREMENTS:
- Windows 10 or later
- 4GB RAM (8GB recommended)
- 4GB free disk space

SUPPORT:
Telegram: https://t.me/Noty_215
YouTube: https://www.youtube.com/@NotY215

Copyright (c) 2026 {APP_AUTHOR}
'''
        zipf.writestr("README.txt", readme)
        
        # Run script
        run_script = f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
start "" "{APP_NAME}.exe"
'''
        zipf.writestr(f"Run_{APP_NAME}.bat", run_script)
    
    size = zip_name.stat().st_size / (1024 * 1024)
    print(f"[OK] Portable ZIP: {zip_name} ({size:.2f} MB)")
    return zip_name

def main():
    print("=" * 60)
    print(f"Building {APP_DISPLAY_NAME} v{APP_VERSION} Installers")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    dist_dir = base_dir / "dist"
    
    if not dist_dir.exists():
        print("[ERROR] dist directory not found!")
        print("Please run build_exe.py first")
        sys.exit(1)
    
    # Change to dist directory
    os.chdir(dist_dir)
    
    # Create installers
    create_windows_installer()
    create_portable_zip()
    
    print("\n" + "=" * 60)
    print("INSTALLERS CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nFiles in {dist_dir}:")
    for file in dist_dir.iterdir():
        if file.is_file():
            size = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size:.2f} MB)")

if __name__ == "__main__":
    main()