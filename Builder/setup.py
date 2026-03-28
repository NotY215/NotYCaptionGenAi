#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for building NotY Caption Generator AI v4.3
Copyright (c) 2026 NotY215
"""

import os
import sys
import subprocess
import shutil
import struct
import zlib
from pathlib import Path

def build_all():
    print("=" * 60)
    print("Building NotY Caption Generator AI v4.3")
    print("Copyright (c) 2026 NotY215")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    temp_dir = base_dir / "temp_build"
    
    # Clean
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    dist_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy main script
    print("\n[1/2] Preparing files...")
    shutil.copy2(base_dir / "noty_caption_gen.py", temp_dir / "noty_caption_gen.py")
    
    # Copy icon
    resources_dir = base_dir / "resources"
    if resources_dir.exists():
        shutil.copytree(resources_dir, temp_dir / "resources")
    
    # Build with PyInstaller
    print("\n[2/2] Building executable...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI",
        "--onefile",
        "--noconfirm",
        "--strip",
        f"--add-data={temp_dir / 'noty_caption_gen.py'}{os.pathsep}.",
        "--hidden-import=whisper",
        "--hidden-import=torch",
        "--hidden-import=numpy",
        "--collect-all=whisper",
        "--collect-all=torch",
        "--console",
        str(temp_dir / "noty_caption_gen.py")
    ]
    
    # Add icon if exists
    icon_path = temp_dir / "resources" / "app.ico"
    if icon_path.exists():
        cmd.insert(4, f"--icon={icon_path}")
    
    subprocess.check_call(cmd)
    
    # Copy output
    exe_file = Path("dist") / "NotYCaptionGenAI.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, dist_dir / "NotYCaptionGenAI.exe")
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Built: NotYCaptionGenAI.exe ({size:.2f} MB)")
    
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("[OK] Build complete!")

if __name__ == "__main__":
    build_all()