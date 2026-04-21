#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Build Orchestrator for NotY Caption Generator AI v7.1
Copyright (c) 2026 NotY215
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "7.1"
INSTALLER_NAME = f"{APP_NAME}_Installer_v{APP_VERSION}.exe"

def clean_all():
    print("Cleaning all build artifacts...")
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    
    dist_dir = base_dir / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("  Removed dist folder")
    
    for build in [builder_dir / "build", base_dir / "build"]:
        if build.exists():
            shutil.rmtree(build)
            print(f"  Removed {build}")
    
    temp_dir = base_dir / "temp_installer"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print("  Removed temp_installer")
    
    for spec in builder_dir.glob("*.spec"):
        spec.unlink()
        print(f"  Removed {spec.name}")
    
    for pycache in base_dir.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
    for pycache in builder_dir.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
    
    print("  Cleanup complete!")

def check_requirements():
    print("Checking build requirements...")
    try:
        subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                       capture_output=True, check=True)
        print("  ✓ PyInstaller installed")
        return True
    except:
        print("  ✗ PyInstaller not installed. Run: pip install pyinstaller")
        return False

def build_all():
    print("=" * 60)
    print(f"Building {APP_NAME} v{APP_VERSION}")
    print("=" * 60)
    
    if not check_requirements():
        print("\n[ERROR] Missing requirements!")
        sys.exit(1)
    
    clean_all()
    
    base_dir = Path(__file__).parent.parent
    dist_dir = base_dir / "dist"
    
    print("\n" + "=" * 60)
    print("[1/2] Building executable...")
    print("=" * 60)
    
    build_exe = base_dir / "Builder" / "build_exe.py"
    
    try:
        subprocess.run([sys.executable, str(build_exe)], check=True, timeout=1800)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Executable build failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] Build cancelled")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("[2/2] Building installer...")
    print("=" * 60)
    
    build_installer = base_dir / "Builder" / "build_installer.py"
    
    try:
        subprocess.run([sys.executable, str(build_installer)], check=True, timeout=1800)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Installer build failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[INFO] Build cancelled")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Executable: {dist_dir / f'{APP_NAME}.exe'}")
    print(f"📦 Installer: {base_dir / INSTALLER_NAME}")
    
    if (dist_dir / f"{APP_NAME}.exe").exists():
        size = (dist_dir / f"{APP_NAME}.exe").stat().st_size / 1024 / 1024
        print(f"\n📊 Executable size: {size:.2f} MB")
    if (base_dir / INSTALLER_NAME).exists():
        size = (base_dir / INSTALLER_NAME).stat().st_size / 1024 / 1024
        print(f"📊 Installer size: {size:.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    build_all()