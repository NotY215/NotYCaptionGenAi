#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI v5.2 using Nuitka
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"

def install_nuitka():
    """Install Nuitka and dependencies"""
    print("Installing Nuitka and dependencies...")
    packages = [
        "nuitka",
        "ordered-set",
        "zstandard",
        "pyinstaller"
    ]
    for package in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], check=False)

def build_with_nuitka():
    """Build executable using Nuitka"""
    print("=" * 70)
    print(f"Building {APP_NAME} v{APP_VERSION} with Nuitka")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Clean previous builds
    if dist_dir.exists():
        print("Cleaning previous build...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)
    
    # Nuitka build command
    nuitka_cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=tk-inter",
        "--enable-plugin=multiprocessing",
        f"--output-dir={dist_dir}",
        f"--output-filename={APP_NAME}.exe",
        "--windows-console-mode=attach",
        "--windows-icon-from-ico=resources/app.ico",
        f"--product-name={APP_NAME}",
        f"--product-version={APP_VERSION}",
        f"--file-version={APP_VERSION}",
        f"--company-name={APP_AUTHOR}",
        "--copyright=Copyright (c) 2026 NotY215",
        "--nofollow-imports",  # Don't follow all imports automatically
        "--follow-import-to=whisper",
        "--follow-import-to=torch",
        "--follow-import-to=torchaudio",
        "--follow-import-to=numpy",
        "--follow-import-to=yt_dlp",
        "--follow-import-to=colorama",
        "--follow-import-to=requests",
        "--include-package=whisper",
        "--include-package=torch",
        "--include-package=torchaudio",
        "--include-package=numpy",
        "--include-package=yt_dlp",
        "--include-package=colorama",
        "--include-package=regex",
        "--include-package=tiktoken",
        "--include-package=packaging",
        "--include-package=requests",
        "--include-package=urllib3",
        "--include-package=certifi",
        "--include-data-dir=models=models",
        "--include-data-dir=ffmpeg=ffmpeg",
        "--include-data-dir=resources=resources",
        "--no-debug",
        "--lto=no",
        "--windows-disable-console",
        "--quiet",
        "noty_caption_gen.py"
    ]
    
    print("\nRunning Nuitka build...")
    print("This will take 20-30 minutes...")
    print("Nuitka compiles Python to C for better performance\n")
    
    try:
        # Run with real-time output
        process = subprocess.Popen(
            nuitka_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            print(f"  {line.rstrip()}")
            sys.stdout.flush()
        
        process.wait(timeout=5400)
        
        if process.returncode != 0:
            print("\n[ERROR] Nuitka build failed!")
            return False
            
        print("\n[SUCCESS] Nuitka build completed!")
        
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Build timed out!")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False
    
    # Find the executable
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        # Check in .dist subfolder
        dist_subdir = dist_dir / f"{APP_NAME}.dist"
        if dist_subdir.exists():
            possible_exe = dist_subdir / f"{APP_NAME}.exe"
            if possible_exe.exists():
                shutil.move(str(possible_exe), str(exe_file))
    
    if exe_file.exists():
        size = exe_file.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        # Copy additional files
        for folder in ['models', 'ffmpeg', 'resources']:
            src = base_dir / folder
            dst = dist_dir / folder
            if src.exists() and not dst.exists():
                shutil.copytree(src, dst)
                print(f"  Copied {folder}")
        
        # Create run script
        run_script = dist_dir / "Run_App.bat"
        with open(run_script, 'w') as f:
            f.write(f'''@echo off
title NotY Caption Generator AI v{APP_VERSION}
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
echo ============================================================
echo NotY Caption Generator AI v{APP_VERSION}
echo Copyright (c) 2026 {APP_AUTHOR}
echo ============================================================
echo.
echo Starting application...
echo.
"{APP_NAME}.exe"
if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed!
    pause
)
''')
        print("  Created Run_App.bat")
        
        return True
    
    print("\n[ERROR] Executable not found!")
    return False

def build_fallback():
    """Fallback to PyInstaller if Nuitka fails"""
    print("\n[INFO] Falling back to PyInstaller...")
    
    try:
        import PyInstaller.__main__
        
        PyInstaller.__main__.run([
            'noty_caption_gen.py',
            '--name=NotYCaptionGenAI',
            '--onefile',
            '--console',
            '--icon=resources/app.ico',
            '--add-data=models;models',
            '--add-data=ffmpeg;ffmpeg',
            '--add-data=resources;resources',
            '--hidden-import=whisper',
            '--hidden-import=torch',
            '--hidden-import=torchaudio',
            '--hidden-import=numpy',
            '--hidden-import=yt_dlp',
            '--hidden-import=colorama',
            '--hidden-import=regex',
            '--hidden-import=tiktoken',
            '--hidden-import=requests',
            '--noconfirm',
            '--clean'
        ])
        
        print("\n[SUCCESS] PyInstaller build completed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] PyInstaller fallback failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("NotY Caption Generator AI Build Script")
    print("=" * 70)
    
    # Install Nuitka
    install_nuitka()
    
    # Try Nuitka first
    success = build_with_nuitka()
    
    # Fallback to PyInstaller if needed
    if not success:
        print("\n[WARNING] Nuitka build failed, trying PyInstaller...")
        success = build_fallback()
    
    if success:
        print("\n" + "=" * 70)
        print("BUILD SUCCESSFUL!")
        print("=" * 70)
        print("\nYou can find the executable in the 'dist' folder.")
        print("Run 'dist\\Run_App.bat' to start the application.")
    else:
        print("\n" + "=" * 70)
        print("BUILD FAILED!")
        print("=" * 70)
        print("\nPlease check the errors above and try again.")
    
    input("\nPress Enter to exit...")