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
    print("=" * 70)
    print(f"Building {APP_NAME} v{APP_VERSION}")
    print(f"Copyright (c) 2026 {APP_AUTHOR}")
    print("=" * 70)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Step 1: Build main executable
    print("\n[1/2] Building main executable...")
    
    build_exe_path = builder_dir / "build_exe.py"
    if not build_exe_path.exists():
        print("[ERROR] build_exe.py not found!")
        sys.exit(1)
    
    # Import and run build_exe
    sys.path.insert(0, str(builder_dir))
    from build_exe import build_exe
    exe_file = build_exe()
    
    if not exe_file or not exe_file.exists():
        print("[ERROR] Main executable build failed!")
        sys.exit(1)
    
    print(f"\n[OK] Main executable: {exe_file}")
    
    # Step 2: Create portable package
    print("\n[2/2] Creating portable package...")
    
    # Create portable directory
    portable_dir = base_dir / f"{APP_NAME}_Portable_v{APP_VERSION}"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True)
    
    # Copy executable
    shutil.copy2(exe_file, portable_dir / exe_file.name)
    
    # Copy required folders
    for folder in ['models', 'ffmpeg', 'resources']:
        src = base_dir / folder
        dst = portable_dir / folder
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  Copied {folder}")
    
    # Create run script
    run_script = portable_dir / "Run_NotYCaptionGenAI.bat"
    with open(run_script, 'w') as f:
        f.write(f'''@echo off
title NotY Caption Generator AI v{APP_VERSION}
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
echo Starting NotY Caption Generator AI v{APP_VERSION}...
echo.
"{exe_file.name}"
pause
''')
    
    # Create README
    readme = portable_dir / "README.txt"
    with open(readme, 'w') as f:
        f.write(f'''NotY Caption Generator AI v{APP_VERSION}
=====================================

How to use:
1. Run "Run_NotYCaptionGenAI.bat"
2. Select YouTube URL or Local File
3. Choose model (tiny/base/small/medium/large)
4. Choose language
5. Choose line type
6. Wait for processing

Requirements:
- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- 4GB free disk space

Features:
- YouTube video captions
- Local video/audio captions
- 6 languages + auto detect
- Word/Letter/Auto line breaks
- Lyrics search for songs
- Vocal separation for music

Support:
Telegram: https://t.me/Noty_215
YouTube: https://www.youtube.com/@NotY215

License: LGPL-3.0
Copyright (c) 2026 NotY215
''')
    
    # Create ZIP archive
    print("\nCreating ZIP archive...")
    zip_name = base_dir / f"{APP_NAME}_Portable_v{APP_VERSION}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, portable_dir.parent)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    # Clean up
    shutil.rmtree(portable_dir)
    
    # Create simple installer
    print("\nCreating installer...")
    installer_name = base_dir / f"{APP_NAME}_Installer_v{APP_VERSION}.exe"
    
    # Create a simple batch installer
    installer_bat = base_dir / "installer_temp.bat"
    with open(installer_bat, 'w') as f:
        f.write(f'''@echo off
title {APP_NAME} v{APP_VERSION} Installer
echo ============================================================
echo {APP_NAME} v{APP_VERSION} Installer
echo Copyright (c) 2026 {APP_AUTHOR}
echo ============================================================
echo.
echo This will install {APP_NAME} to your computer.
echo.
set /p INSTALL_PATH="Installation directory [C:\\{APP_NAME}]: "
if "%INSTALL_PATH%"=="" set INSTALL_PATH=C:\\{APP_NAME}
echo.
echo Installing to: %INSTALL_PATH%
echo.
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"
echo Copying files...
xcopy /E /I /Y "{portable_dir}" "%INSTALL_PATH%"
echo.
echo Creating shortcuts...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\\Desktop\\{APP_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{exe_file.name}'; $SC.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{exe_file.name}'; $SC.Save()"
echo.
echo Installation complete!
echo.
pause
''')
    
    print(f"\n[OK] Portable package: {zip_name}")
    print(f"[OK] Installer script: {installer_bat}")
    
    print("\n" + "=" * 70)
    print("BUILD COMPLETE!")
    print("=" * 70)
    print(f"\nPortable version: {zip_name}")
    print(f"\nTo test the app, run:")
    print(f"  {exe_file}")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    build_all()