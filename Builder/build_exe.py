#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v5.2 - Using Nuitka
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"
APP_COPYRIGHT = f"Copyright (c) 2026 {APP_AUTHOR}"

def build_exe():
    print("=" * 60)
    print(f"Building {APP_NAME} Executable v{APP_VERSION} using Nuitka")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    ffmpeg_dir = base_dir / "ffmpeg"
    dist_dir = base_dir / "dist"
    
    # Clean previous builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Install Nuitka if not present
    print("\n[INFO] Ensuring Nuitka is installed...")
    subprocess.run([sys.executable, "-m", "pip", "install", "nuitka", "ordered-set", "zstandard"], 
                   capture_output=True)
    
    source_file = base_dir / "noty_caption_gen.py"
    icon_path = resources_dir / "app.ico"
    
    # Build command for Nuitka
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        f"--output-dir={dist_dir}",
        f"--output-filename={APP_NAME}.exe",
        "--enable-plugin=tk-inter",
        "--enable-plugin=multiprocessing",
        "--windows-console-mode=attach",
        f"--windows-icon-from-ico={icon_path}",
        f"--product-name={APP_NAME}",
        f"--product-version={APP_VERSION}",
        f"--file-version={APP_VERSION}",
        f"--company-name={APP_AUTHOR}",
        f"--copyright={APP_COPYRIGHT}",
        "--follow-imports",
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
        "--include-package=tqdm",
        "--include-data-dir=resources=resources",
        "--include-data-dir=ffmpeg=ffmpeg",
        "--no-debug",
        "--lto=no",
        "--remove-output",
        str(source_file)
    ]
    
    print("\n[INFO] Building with Nuitka...")
    print("[INFO] This may take 10-15 minutes...")
    sys.stdout.flush()
    
    try:
        # Run Nuitka
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            print(f"  {line.rstrip()}")
            sys.stdout.flush()
        
        process.wait(timeout=3600)
        
        if process.returncode != 0:
            print("\n[ERROR] Nuitka build failed!")
            return None
            
        print("\n[OK] Build completed successfully!")
        
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Build timed out!")
        return None
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        return None
    
    # Find the executable
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        # Check in .dist subfolder
        possible_path = dist_dir / f"{APP_NAME}.dist" / f"{APP_NAME}.exe"
        if possible_path.exists():
            shutil.move(str(possible_path), str(exe_file))
    
    if exe_file.exists():
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        # Create models directory
        models_dir = dist_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Copy models if they exist
        source_models = base_dir / "models"
        if source_models.exists():
            for model_file in source_models.glob("*.pt"):
                shutil.copy2(model_file, models_dir / model_file.name)
                print(f"  Copied model: {model_file.name}")
        
        # Copy ffmpeg folder if not already included
        dest_ffmpeg = dist_dir / "ffmpeg"
        if ffmpeg_dir.exists() and not dest_ffmpeg.exists():
            shutil.copytree(ffmpeg_dir, dest_ffmpeg)
            print("  Copied ffmpeg folder")
        
        # Copy resources if not already included
        dest_resources = dist_dir / "resources"
        if resources_dir.exists() and not dest_resources.exists():
            shutil.copytree(resources_dir, dest_resources)
            print("  Copied resources")
        
        return exe_file
    else:
        print("\n[ERROR] Build failed - executable not found!")
        return None

if __name__ == "__main__":
    result = build_exe()
    if result:
        print(f"\n[SUCCESS] Build successful! Executable: {result}")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)