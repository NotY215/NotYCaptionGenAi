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
    sys.stdout.flush()
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Clean previous builds
    if dist_dir.exists():
        print("\n[INFO] Cleaning previous build...")
        shutil.rmtree(dist_dir)
        sys.stdout.flush()
    
    # Step 1: Build main executable
    print("\n[1/2] Building main executable...")
    print("[INFO] This will take 15-20 minutes...")
    sys.stdout.flush()
    
    build_exe_path = builder_dir / "build_exe.py"
    if not build_exe_path.exists():
        print("[ERROR] build_exe.py not found!")
        sys.exit(1)
    
    # Run build_exe
    try:
        result = subprocess.run(
            [sys.executable, str(build_exe_path)],
            capture_output=False,
            text=True,
            timeout=5400
        )
        if result.returncode != 0:
            print("[ERROR] Main executable build failed!")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("[ERROR] Build timed out!")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    
    # Check if executable was created
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        print("[ERROR] Main executable not found!")
        sys.exit(1)
    
    size_mb = exe_file.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Main executable: {exe_file} ({size_mb:.2f} MB)")
    sys.stdout.flush()
    
    # Step 2: Create portable package
    print("\n[2/2] Creating portable package...")
    sys.stdout.flush()
    
    # Create portable directory
    portable_dir = base_dir / f"{APP_NAME}_Portable_v{APP_VERSION}"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True)
    
    # Copy executable
    shutil.copy2(exe_file, portable_dir / exe_file.name)
    print("  Copied executable")
    
    # Copy required folders
    for folder_name in ['models', 'ffmpeg', 'resources']:
        src = base_dir / folder_name
        dst = portable_dir / folder_name
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  Copied {folder_name}")
    
    # Create run script
    run_script = portable_dir / f"Run_{APP_NAME}.bat"
    with open(run_script, 'w') as f:
        f.write(f'''@echo off
title {APP_NAME} v{APP_VERSION}
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
echo ============================================================
echo {APP_NAME} v{APP_VERSION}
echo Copyright (c) 2026 {APP_AUTHOR}
echo ============================================================
echo.
echo Starting application...
echo.
"{exe_file.name}"
if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed!
    echo Please check that all required files are present.
    pause
)
''')
    print(f"  Created run script")
    
    # Create README
    readme = portable_dir / "README.txt"
    with open(readme, 'w') as f:
        f.write(f'''========================================
{APP_NAME} v{APP_VERSION}
========================================

Developed by: {APP_AUTHOR}
License: LGPL-3.0

========================================
HOW TO USE
========================================

1. Double-click "Run_{APP_NAME}.bat"
2. Select either:
   - YouTube: Paste a YouTube URL
   - Local File: Select a video/audio file
3. Choose Whisper model:
   - tiny (fastest, least accurate)
   - base (balanced)
   - small (good)
   - medium (accurate)
   - large (best, slowest)
4. Choose language:
   - English, Hindi, Japanese, Spanish, Korean, Chinese, or Auto Detect
5. Choose line break type:
   - Words: Break by word count
   - Letters: Break by character limit
   - Auto: Smart sentence detection
6. Wait for processing
7. Find your .srt file in the same folder as your media

========================================
REQUIREMENTS
========================================

- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- 4GB free disk space
- Internet connection for YouTube downloads

========================================
SUPPORT
========================================

Telegram: https://t.me/Noty_215
YouTube: https://www.youtube.com/@NotY215

========================================
TROUBLESHOOTING
========================================

If the app doesn't start:
1. Make sure all files are in the same folder
2. Run as Administrator
3. Check Windows Defender isn't blocking it

If transcription fails:
1. Make sure the audio/video file isn't corrupted
2. Try a different Whisper model
3. Check your internet connection (for YouTube)

========================================
''')
    print(f"  Created README.txt")
    
    # Create ZIP archive
    print("\nCreating ZIP archive...")
    zip_name = base_dir / f"{APP_NAME}_Portable_v{APP_VERSION}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, portable_dir.parent)
                zipf.write(file_path, arcname)
    
    zip_size = zip_name.stat().st_size / (1024 * 1024)
    print(f"  Created: {zip_name} ({zip_size:.2f} MB)")
    
    # Clean up portable directory
    shutil.rmtree(portable_dir)
    
    print("\n" + "=" * 70)
    print("BUILD COMPLETE!")
    print("=" * 70)
    print(f"\nExecutable: {exe_file}")
    print(f"Portable ZIP: {zip_name}")
    print(f"\nTo test the app, run:")
    print(f"  cd dist")
    print(f"  Run_App.bat")
    print("=" * 70)

if __name__ == "__main__":
    try:
        build_all()
        print("\n[SUCCESS] All builds completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        input("\nPress Enter to exit...")