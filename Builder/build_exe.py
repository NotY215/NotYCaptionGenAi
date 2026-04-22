#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI - Build Pure Executable v7.1
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_artifacts():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Cleaned: {dir_path}")
            
    for pattern in files_to_clean:
        for file in Path('.').glob(pattern):
            file.unlink()
            print(f"Cleaned: {file}")


def build_exe():
    """Build the pure code executable"""
    print("=" * 60)
    print("  NotY Caption Generator AI - Build Pure Executable")
    print("=" * 60)
    
    # Clean previous builds
    clean_build_artifacts()
    
    # PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                          # Single executable
        '--windowed',                         # No console for GUI
        '--name', 'NotYCaptionGenAI',
        '--icon', 'resources/app.ico',
        '--add-data', 'ffmpeg;ffmpeg',        # FFmpeg binaries
        '--add-data', 'models;models',        # Whisper models
        '--add-data', 'pretrained_models;pretrained_models',  # Spleeter models
        '--add-data', 'resources;resources',  # Resources
        '--hidden-import', 'whisper',
        '--hidden-import', 'torch',
        '--hidden-import', 'numpy',
        '--collect-all', 'whisper',
        '--exclude-module', 'tensorflow',     # Exclude heavy packages
        '--exclude-module', 'spleeter',
        '--exclude-module', 'torchvision',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'pandas',
        '--exclude-module', 'scipy',
        '--exclude-module', 'PIL',
        'noty_caption_gui.py'
    ]
    
    print("\nRunning PyInstaller...")
    print("Command:", ' '.join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n{Colors.GREEN}Build successful!{Colors.ENDC}")
        
        # Show output file info
        exe_path = Path('dist/NotYCaptionGenAI.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\nOutput: {exe_path}")
            print(f"Size: {size_mb:.2f} MB")
            
    except subprocess.CalledProcessError as e:
        print(f"\n{Colors.FAIL}Build failed: {e}{Colors.ENDC}")
        sys.exit(1)


class Colors:
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


if __name__ == "__main__":
    build_exe()