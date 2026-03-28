#!/usr/bin/env python3
"""
Build NotY Caption Generator AI Executable
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_exe():
    """Build the main executable using PyInstaller"""
    print("=" * 60)
    print("Building NotY Caption Generator AI Executable v4.2")
    print("=" * 60)
    
    # Get paths
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    dist_dir = builder_dir / "dist"
    build_dir = builder_dir / "build"
    
    # Clean previous builds
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Create dist directory
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build the executable
    print("\nBuilding main executable...")
    
    # Build command with proper icon embedding
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI",
        "--onefile",
        f"--icon={resources_dir / 'app.ico'}",
        f"--add-data={resources_dir}{os.pathsep}resources",
        "--hidden-import=colorama",
        "--hidden-import=argparse",
        "--hidden-import=webbrowser",
        "--hidden-import=subprocess",
        "--hidden-import=pathlib",
        "--hidden-import=threading",
        "--hidden-import=queue",
        "--console",
        str(base_dir / "noty_caption_gen.py")
    ]
    
    # Run PyInstaller
    subprocess.check_call(cmd)
    
    # Move executable to base dist folder
    base_dist_dir = base_dir / "dist"
    base_dist_dir.mkdir(parents=True, exist_ok=True)
    
    exe_source = dist_dir / "NotYCaptionGenAI.exe"
    if exe_source.exists():
        # Copy the executable
        shutil.copy2(exe_source, base_dist_dir / "NotYCaptionGenAI.exe")
        print(f"\n✅ Main executable built successfully: {base_dist_dir / 'NotYCaptionGenAI.exe'}")
    else:
        print("\n❌ Failed to build executable!")
        # Check for alternative location
        alt_exe = dist_dir / "NotYCaptionGenAI" / "NotYCaptionGenAI.exe"
        if alt_exe.exists():
            shutil.copy2(alt_exe, base_dist_dir / "NotYCaptionGenAI.exe")
            print(f"\n✅ Main executable found at alternative location: {base_dist_dir / 'NotYCaptionGenAI.exe'}")
        else:
            sys.exit(1)
    
    # Clean up build files
    shutil.rmtree(dist_dir, ignore_errors=True)
    shutil.rmtree(build_dir, ignore_errors=True)
    spec_file = builder_dir / "NotYCaptionGenAI.spec"
    if spec_file.exists():
        spec_file.unlink()
    
    return base_dist_dir / "NotYCaptionGenAI.exe"

if __name__ == "__main__":
    build_exe()