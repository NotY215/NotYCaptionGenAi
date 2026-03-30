#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for building NotY Caption Generator AI v4.4
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_all():
    print("=" * 60)
    print("Building NotY Caption Generator AI v4.4")
    print("Copyright (c) 2026 NotY215")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    if dist_dir.exists():
        print("Cleaning previous build...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Build main executable
    print("\n[1/3] Building main executable...")
    
    build_exe_path = builder_dir / "build_exe.py"
    if not build_exe_path.exists():
        print("[ERROR] build_exe.py not found!")
        sys.exit(1)
    
    try:
        subprocess.run([sys.executable, str(build_exe_path)], check=True, timeout=1800)
    except Exception as e:
        print(f"[ERROR] Build failed: {e}")
        sys.exit(1)
    
    main_exe = dist_dir / "NotYCaptionGenAI.exe"
    if not main_exe.exists():
        print("[ERROR] Main executable not found!")
        sys.exit(1)
    
    print(f"[OK] Main executable: {main_exe} ({main_exe.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # Step 2: Build uninstaller
    print("\n[2/3] Building uninstaller executable...")
    
    uninstaller_py = str(builder_dir / "uninstaller.py")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI_Uninstaller",
        "--onefile",
        "--console",
        "--noconfirm",
        uninstaller_py
    ]
    
    temp_build_dir = base_dir / "temp_build"
    if temp_build_dir.exists():
        shutil.rmtree(temp_build_dir)
    temp_build_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        subprocess.run(cmd, cwd=str(temp_build_dir), check=True, timeout=120)
        uninstaller_exe = temp_build_dir / "dist" / "NotYCaptionGenAI_Uninstaller.exe"
        if uninstaller_exe.exists():
            print(f"[OK] Uninstaller built")
        else:
            print("[ERROR] Uninstaller not found!")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to build uninstaller: {e}")
        sys.exit(1)
    
    # Step 3: Build installer
    print("\n[3/3] Building installer...")
    
    temp_dir = base_dir / "temp_installer"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(main_exe, temp_dir / "NotYCaptionGenAI.exe")
    shutil.copy2(uninstaller_exe, temp_dir / "NotYCaptionGenAI_Uninstaller.exe")
    
    resources_dir = base_dir / "resources"
    if resources_dir.exists():
        shutil.copytree(resources_dir, temp_dir / "resources")
        print("  Copied resources")
    
    models_dir = base_dir / "models"
    if models_dir.exists() and any(models_dir.iterdir()):
        print("  Including models...")
        shutil.copytree(models_dir, temp_dir / "models")
        model_count = len(list((temp_dir / "models").glob("*.pt")))
        print(f"    Added {model_count} models")
    
    installer_py = str(builder_dir / "installer_console.py")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI_Installer_v4.4",
        "--onefile",
        f"--add-data={temp_dir / 'NotYCaptionGenAI.exe'}{os.pathsep}.",
        f"--add-data={temp_dir / 'NotYCaptionGenAI_Uninstaller.exe'}{os.pathsep}.",
        f"--add-data={temp_dir / 'resources'}{os.pathsep}resources",
        "--hidden-import=ctypes",
        "--hidden-import=subprocess",
        "--hidden-import=shutil",
        "--hidden-import=pathlib",
        "--hidden-import=platform",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tempfile",
        "--console",
        "--noconfirm",
        installer_py
    ]
    
    if (temp_dir / "models").exists():
        cmd.insert(4, f"--add-data={temp_dir / 'models'}{os.pathsep}models")
    
    icon_path = temp_dir / "resources" / "app.ico"
    if icon_path.exists():
        cmd.insert(4, f"--icon={icon_path}")
    
    try:
        subprocess.run(cmd, cwd=str(temp_dir), check=True, timeout=300)
        print("\n[OK] Installer built successfully!")
    except Exception as e:
        print(f"\n[ERROR] Installer build failed: {e}")
        sys.exit(1)
    
    installer_exe = temp_dir / "dist" / "NotYCaptionGenAI_Installer_v4.4.exe"
    if installer_exe.exists():
        final_installer = base_dir / "NotYCaptionGenAI_Installer_v4.4.exe"
        shutil.copy2(installer_exe, final_installer)
        size = final_installer.stat().st_size / 1024 / 1024
        print(f"\n[OK] Installer created: {final_installer} ({size:.2f} MB)")
    else:
        print("\n[ERROR] Installer not found!")
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(temp_build_dir, ignore_errors=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"Installer: {base_dir / 'NotYCaptionGenAI_Installer_v4.4.exe'}")
    print("=" * 60)

if __name__ == "__main__":
    build_all()