#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v7.1 - PURE CODE ONLY
ABSOLUTELY NO packages - Just the application code (5-10 MB)
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "7.1"

def clean_build_artifacts(builder_dir):
    """Clean build artifacts but NOT the final executable"""
    # Remove build folder
    build_dir = builder_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("  Removed build folder")
    
    # Remove spec files
    for spec_file in builder_dir.glob("*.spec"):
        spec_file.unlink()
        print(f"  Removed {spec_file.name}")
    
    # Remove __pycache__
    for pycache in builder_dir.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
        print(f"  Removed {pycache}")

def build_exe():
    print("=" * 60)
    print(f"Building {APP_NAME} Executable v{APP_VERSION}")
    print("PURE CODE ONLY - 5-10 MB (NO PACKAGES)")
    print("=" * 60)

    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    dist_dir = base_dir / "dist"
    src_dir = base_dir / "src"

    # Create dist directory
    dist_dir.mkdir(parents=True, exist_ok=True)

    source_file = base_dir / "noty_caption_gen.py"
    icon_file = resources_dir / "app.ico"

    # PURE CODE ONLY - NO hidden imports, NO collect-all
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        f"--name={APP_NAME}",
        f"--icon={icon_file}",
        "--add-data", f"{src_dir}{os.pathsep}src",
        "--add-data", f"{resources_dir}{os.pathsep}resources",
        "--exclude-module=torch",
        "--exclude-module=torchaudio",
        "--exclude-module=whisper",
        "--exclude-module=numpy",
        "--exclude-module=yt_dlp",
        "--exclude-module=tensorflow",
        "--exclude-module=spleeter",
        "--exclude-module=librosa",
        "--exclude-module=soundfile",
        "--exclude-module=scipy",
        "--exclude-module=numba",
        "--exclude-module=llvmlite",
        "--exclude-module=pandas",
        "--exclude-module=matplotlib",
        "--noconfirm",
        "--clean",
        "--log-level=ERROR",
        str(source_file)
    ]

    print("\n[INFO] Building with PyInstaller (NO packages bundled)...")
    print("[INFO] Expected size: 5-10 MB")
    print("[INFO] This may take 1-2 minutes...")
    sys.stdout.flush()

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(builder_dir)
        )

        for line in process.stdout:
            if "ERROR" in line or "WARNING" in line:
                print(f"  {line.rstrip()}")
            sys.stdout.flush()

        process.wait(timeout=1800)

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

    # Find the executable (PyInstaller puts it in builder_dir/dist)
    exe_file = builder_dir / "dist" / f"{APP_NAME}.exe"
    if not exe_file.exists():
        exe_file = dist_dir / f"{APP_NAME}.exe"
    
    if exe_file.exists():
        final_exe = dist_dir / f"{APP_NAME}.exe"
        if exe_file != final_exe:
            shutil.move(str(exe_file), str(final_exe))
            exe_file = final_exe
        
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        if size > 20:
            print(f"[WARNING] Executable is {size:.2f} MB - should be under 20 MB!")
        else:
            print("[OK] Size is good! (Under 20 MB)")
        
        # Clean up build artifacts (but keep the executable)
        print("\n[INFO] Cleaning build artifacts...")
        clean_build_artifacts(builder_dir)
        
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