#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for building NotY Caption Generator AI v5.2
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"

def build_all():
    print("=" * 60)
    print(f"Building {APP_NAME} v{APP_VERSION}")
    print(f"Copyright (c) 2026 {APP_AUTHOR}")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Clean previous builds
    if dist_dir.exists():
        print("\nCleaning previous build...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Build main executable
    print("\n[1/2] Building main executable...")
    
    # Run build_exe.py
    build_exe_path = builder_dir / "build_exe.py"
    if not build_exe_path.exists():
        print("[ERROR] build_exe.py not found!")
        sys.exit(1)
    
    result = subprocess.run(
        [sys.executable, str(build_exe_path)],
        cwd=base_dir
    )
    
    if result.returncode != 0:
        print("[ERROR] Main executable build failed!")
        sys.exit(1)
    
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        print("[ERROR] Main executable not found!")
        sys.exit(1)
    
    size_mb = exe_file.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Main executable: {exe_file} ({size_mb:.2f} MB)")
    
    # Step 2: Create portable package
    print("\n[2/2] Creating portable package...")
    
    # Change to dist directory
    os.chdir(dist_dir)
    
    # Create portable ZIP
    zip_name = dist_dir / f"{APP_NAME}_Portable_v{APP_VERSION}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        zipf.write(exe_file.name, exe_file.name)
        
        # Add ffmpeg folder
        ffmpeg_dir = dist_dir / "ffmpeg"
        if ffmpeg_dir.exists():
            for file in ffmpeg_dir.rglob('*'):
                if file.is_file():
                    zipf.write(file, str(file.relative_to(dist_dir)))
        
        # Add resources folder
        res_dir = dist_dir / "resources"
        if res_dir.exists():
            for file in res_dir.rglob('*'):
                if file.is_file():
                    zipf.write(file, str(file.relative_to(dist_dir)))
        
        # Add models folder if exists
        models_dir = dist_dir / "models"
        if models_dir.exists():
            for file in models_dir.rglob('*.pt'):
                if file.is_file():
                    zipf.write(file, str(file.relative_to(dist_dir)))
        
        # Add README
        readme_content = f'''NotY Caption Generator AI v{APP_VERSION}
=====================================

Portable Version - No installation required!

HOW TO USE:
1. Extract all files to any folder
2. Double-click {APP_NAME}.exe
3. First run will download Whisper models automatically

FEATURES:
- YouTube video captioning
- Local video/audio captioning
- 7 languages (English, Hindi, Japanese, Spanish, Korean, Chinese, Russian)
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
        zipf.writestr("README.txt", readme_content)
        
        # Add run script
        run_script = f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
start "" "{APP_NAME}.exe"
'''
        zipf.writestr(f"Run_{APP_NAME}.bat", run_script)
    
    zip_size = zip_name.stat().st_size / (1024 * 1024)
    print(f"[OK] Portable ZIP: {zip_name} ({zip_size:.2f} MB)")
    
    # Create simple installer batch
    installer_content = f'''@echo off
title {APP_NAME} v{APP_VERSION} Installer
color 0A

echo ============================================================
echo    {APP_NAME} v{APP_VERSION} Installer
echo    Copyright (c) 2026 {APP_AUTHOR}
echo ============================================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator rights required!
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

:: Installation path
set /p "INSTALL_PATH=Installation directory [C:\\{APP_NAME}]: "
if "%INSTALL_PATH%"=="" set INSTALL_PATH=C:\\{APP_NAME}

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
if exist "models\\*.pt" xcopy /E /I /Y "models" "%INSTALL_PATH%\\models\\" >nul

:: Create shortcuts
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\\Desktop\\{APP_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $SC.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $SC.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\SendTo\\{APP_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $SC.Save()"

:: Registry
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "DisplayName" /d "{APP_NAME} v{APP_VERSION}" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "UninstallString" /d "%INSTALL_PATH%\\Uninstall.bat" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "Publisher" /d "{APP_AUTHOR}" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "DisplayVersion" /d "{APP_VERSION}" /f

:: Create uninstaller
echo @echo off > "%INSTALL_PATH%\\Uninstall.bat"
echo title {APP_NAME} Uninstaller >> "%INSTALL_PATH%\\Uninstall.bat"
echo echo Uninstalling {APP_NAME}... >> "%INSTALL_PATH%\\Uninstall.bat"
echo rmdir /s /q "%INSTALL_PATH%" >> "%INSTALL_PATH%\\Uninstall.bat"
echo del "%%USERPROFILE%%\\Desktop\\{APP_NAME}.lnk" >> "%INSTALL_PATH%\\Uninstall.bat"
echo del "%%APPDATA%%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_NAME}.lnk" >> "%INSTALL_PATH%\\Uninstall.bat"
echo del "%%APPDATA%%\\Microsoft\\Windows\\SendTo\\{APP_NAME}.lnk" >> "%INSTALL_PATH%\\Uninstall.bat"
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
echo You can now run {APP_NAME} from Desktop or Start Menu
echo.
pause
'''
    
    installer_bat = dist_dir / "Install.bat"
    with open(installer_bat, 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print(f"[OK] Installer: {installer_bat}")
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print(f"\nOutput directory: {dist_dir}")
    print("\nFiles created:")
    for file in dist_dir.iterdir():
        if file.is_file():
            size = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size:.2f} MB)")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    build_all()