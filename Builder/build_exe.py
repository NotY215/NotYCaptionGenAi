#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable
Version 4.3
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Set console encoding to UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def build_exe():
    """Build the main executable using PyInstaller"""
    print("=" * 60)
    print("Building NotY Caption Generator AI Executable v4.3")
    print("=" * 60)
    
    # Get paths
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    
    # Set output directories
    dist_dir = base_dir / "dist"
    build_dir = base_dir / "build"
    
    # Clean previous builds
    if dist_dir.exists():
        print("\nCleaning old dist directory...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        print("Cleaning old build directory...")
        shutil.rmtree(build_dir)
    
    # Create dist directory
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("[OK] PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check if source file exists
    source_file = base_dir / "noty_caption_gen.py"
    if not source_file.exists():
        print(f"[ERROR] Source file not found: {source_file}")
        sys.exit(1)
    else:
        print(f"[OK] Source file found: {source_file}")
    
    # Check if icon exists
    icon_file = resources_dir / "app.ico"
    if not icon_file.exists():
        print(f"[WARNING] Icon not found: {icon_file}, building without icon")
        icon_arg = []
    else:
        print(f"[OK] Icon found: {icon_file}")
        icon_arg = [f"--icon={icon_file}"]
    
    # Build the executable
    print("\nBuilding main executable...")
    print("This may take a few minutes...")
    
    # Build command with explicit paths
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI",
        "--onefile",
        *icon_arg,
        f"--add-data={resources_dir}{os.pathsep}resources",
        "--hidden-import=colorama",
        "--hidden-import=argparse",
        "--hidden-import=webbrowser",
        "--hidden-import=subprocess",
        "--hidden-import=pathlib",
        "--hidden-import=threading",
        "--hidden-import=queue",
        "--console",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        "--noconfirm",
        str(source_file)
    ]
    
    try:
        subprocess.check_call(cmd, cwd=str(base_dir))
        print("\n[OK] PyInstaller completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] PyInstaller failed: {e}")
        sys.exit(1)
    
    # Verify the executable was created
    exe_file = dist_dir / "NotYCaptionGenAI.exe"
    if not exe_file.exists():
        print(f"\n[ERROR] Executable not found at expected location: {exe_file}")
        # Check alternative locations
        alt_locations = [
            dist_dir / "NotYCaptionGenAI.exe",
            base_dir / "dist" / "NotYCaptionGenAI.exe",
            Path.cwd() / "dist" / "NotYCaptionGenAI.exe",
        ]
        for alt in alt_locations:
            if alt.exists():
                exe_file = alt
                break
    
    if exe_file.exists():
        file_size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Main executable built successfully!")
        print(f"   Location: {exe_file}")
        print(f"   Size: {file_size:.2f} MB")
        return exe_file
    else:
        print("\n[ERROR] Failed to build executable!")
        print("Checked locations:")
        for alt in alt_locations:
            print(f"   {alt}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()