#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v5.2 - PyInstaller Fixed
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

def build_exe():
    print("=" * 60)
    print(f"Building {APP_NAME} Executable v{APP_VERSION}")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    ffmpeg_dir = base_dir / "ffmpeg"
    dist_dir = base_dir / "dist"
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    source_file = base_dir / "noty_caption_gen.py"
    icon_file = resources_dir / "app.ico"
    
    # Simple PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        f"--name={APP_NAME}",
        f"--icon={icon_file}",
        "--add-data", f"{ffmpeg_dir}{os.pathsep}ffmpeg",
        "--add-data", f"{resources_dir}{os.pathsep}resources",
        "--hidden-import=torch",
        "--hidden-import=torch.nn",
        "--hidden-import=torch._C",
        "--hidden-import=whisper",
        "--hidden-import=whisper.transcribe",
        "--hidden-import=whisper.decoding",
        "--hidden-import=whisper.audio",
        "--hidden-import=numpy",
        "--hidden-import=yt_dlp",
        "--hidden-import=colorama",
        "--hidden-import=tqdm",
        "--hidden-import=regex",
        "--hidden-import=tiktoken",
        "--hidden-import=requests",
        "--hidden-import=torchaudio",
        "--collect-all=torch",
        "--collect-all=whisper",
        "--collect-all=numpy",
        "--collect-all=yt_dlp",
        "--paths", str(base_dir),
        "--paths", str(base_dir / ".venv" / "Lib" / "site-packages"),
        "--noconfirm",
        "--clean",
        str(source_file)
    ]
    
    print("\n[INFO] Building with PyInstaller...")
    print("[INFO] This may take 10-15 minutes...")
    sys.stdout.flush()
    
    try:
        # Run PyInstaller
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(builder_dir)
        )
        
        for line in process.stdout:
            print(f"  {line.rstrip()}")
            sys.stdout.flush()
        
        process.wait(timeout=3600)
        
        if process.returncode != 0:
            print("\n[ERROR] PyInstaller build failed!")
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
        possible_path = builder_dir / "dist" / f"{APP_NAME}.exe"
        if possible_path.exists():
            shutil.move(str(possible_path), str(exe_file))
    
    if exe_file.exists():
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        # Copy models directory if exists
        models_dir = base_dir / "models"
        dest_models = dist_dir / "models"
        if models_dir.exists():
            if dest_models.exists():
                shutil.rmtree(dest_models)
            shutil.copytree(models_dir, dest_models)
            print("  Copied models folder")
        
        # Create run script
        run_script = dist_dir / "Run_App.bat"
        with open(run_script, 'w') as f:
            f.write(f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
echo Starting NotY Caption Generator AI v{APP_VERSION}...
echo.
"{APP_NAME}.exe"
pause
''')
        print("  Created Run_App.bat")
        
        return exe_file
    else:
        print("\n[ERROR] Executable not found!")
        return None

if __name__ == "__main__":
    result = build_exe()
    if result:
        print(f"\n[SUCCESS] Build successful! Run: {result}")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)