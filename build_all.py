#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI - Complete Build System v5.2
Copyright (c) 2026 NotY215
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"

def print_header():
    print("=" * 70)
    print(f"  NotY Caption Generator AI v{APP_VERSION} - Complete Build")
    print(f"  Copyright (c) 2026 {APP_AUTHOR}")
    print("=" * 70)

def clean_build():
    print("\n[1/4] Cleaning previous builds...")
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    spec_files = list(base_dir.glob("*.spec"))
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("  Removed dist folder")
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("  Removed build folder")
    for spec in spec_files:
        spec.unlink()
        print(f"  Removed {spec.name}")
    
    # Clean PyInstaller cache
    cache_dir = Path(os.environ.get('LOCALAPPDATA', '')) / "pyinstaller"
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)
        print("  Cleaned PyInstaller cache")
    
    print("[OK] Cleanup complete")

def build_executable():
    print("\n[2/4] Building executable...")
    base_dir = Path(__file__).parent
    builder_dir = base_dir / "Builder"
    
    # Run build_exe.py
    result = subprocess.run(
        [sys.executable, str(builder_dir / "build_exe.py")],
        cwd=base_dir,
        capture_output=False
    )
    
    if result.returncode != 0:
        print("[ERROR] Executable build failed!")
        return False
    
    # Check if executable was created
    exe_file = base_dir / "dist" / f"{APP_NAME}.exe"
    if exe_file.exists():
        size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"[OK] Executable built: {exe_file} ({size_mb:.2f} MB)")
        return True
    
    print("[ERROR] Executable not found!")
    return False

def build_installer():
    print("\n[3/4] Building installer...")
    base_dir = Path(__file__).parent
    builder_dir = base_dir / "Builder"
    
    # Run build_installer.py
    result = subprocess.run(
        [sys.executable, str(builder_dir / "build_installer.py")],
        cwd=base_dir,
        capture_output=False
    )
    
    if result.returncode != 0:
        print("[ERROR] Installer build failed!")
        return False
    
    return True

def create_portable():
    print("\n[4/4] Creating portable version...")
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    import zipfile
    portable_name = dist_dir / f"{APP_NAME}_Portable_v{APP_VERSION}.zip"
    
    with zipfile.ZipFile(portable_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        exe_file = dist_dir / f"{APP_NAME}.exe"
        if exe_file.exists():
            zipf.write(exe_file, f"{APP_NAME}.exe")
        
        # Add ffmpeg
        ffmpeg_dir = dist_dir / "ffmpeg"
        if ffmpeg_dir.exists():
            for file in ffmpeg_dir.rglob("*"):
                if file.is_file():
                    zipf.write(file, f"ffmpeg/{file.relative_to(ffmpeg_dir)}")
        
        # Add resources
        res_dir = dist_dir / "resources"
        if res_dir.exists():
            for file in res_dir.rglob("*"):
                if file.is_file():
                    zipf.write(file, f"resources/{file.relative_to(res_dir)}")
        
        # Add README
        readme_content = f'''NotY Caption Generator AI v{APP_VERSION}
=====================================

Portable Version - No installation required!

HOW TO USE:
1. Extract all files to any folder
2. Run {APP_NAME}.exe
3. First run will download Whisper models automatically

FEATURES:
- YouTube video captioning
- Local video/audio captioning  
- 6 languages + auto detect
- Smart line breaking
- Lyrics search

SUPPORT:
Telegram: https://t.me/Noty_215
YouTube: https://www.youtube.com/@NotY215

Copyright (c) 2026 {APP_AUTHOR}
'''
        zipf.writestr("README.txt", readme_content)
        
        # Create run script
        run_script = f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
start "" "{APP_NAME}.exe"
'''
        zipf.writestr(f"Run_{APP_NAME}.bat", run_script)
    
    size_mb = portable_name.stat().st_size / (1024 * 1024)
    print(f"[OK] Portable version created: {portable_name} ({size_mb:.2f} MB)")
    return True

def main():
    print_header()
    
    # Check if running as admin
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() if sys.platform == "win32" else False
    
    if not is_admin:
        print("\n[WARNING] Not running as Administrator!")
        print("Some features may not work correctly.")
        print("Recommended: Run as Administrator for full functionality.\n")
    
    # Build steps
    clean_build()
    
    if not build_executable():
        print("\n[FAILED] Build failed at executable stage!")
        sys.exit(1)
    
    if not build_installer():
        print("\n[WARNING] Installer build failed, but executable is ready.")
    
    create_portable()
    
    print("\n" + "=" * 70)
    print("BUILD COMPLETE!")
    print("=" * 70)
    print("\nOutput files in 'dist' folder:")
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    for file in dist_dir.iterdir():
        if file.is_file():
            size = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size:.2f} MB)")
    
    print("\n" + "=" * 70)
    print("To test the application:")
    print(f"  cd dist")
    print(f"  {APP_NAME}.exe")
    print("=" * 70)

if __name__ == "__main__":
    main()