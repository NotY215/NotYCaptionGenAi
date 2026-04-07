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
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"
INSTALLER_NAME = f"NotYCaptionGenAI_Installer_v{APP_VERSION}.exe"

def build_all():
    print("=" * 60)
    print(f"Building {APP_NAME} v{APP_VERSION}")
    print(f"Copyright (c) 2026 {APP_AUTHOR}")
    print("=" * 60)
    sys.stdout.flush()
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Clean previous builds
    if dist_dir.exists():
        print("Cleaning previous build...")
        sys.stdout.flush()
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print(f"Warning: {e}")
            sys.stdout.flush()
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Build main executable
    print("\n[1/3] Building main executable...")
    print("[INFO] This may take 10-15 minutes...")
    sys.stdout.flush()
    
    build_exe_path = builder_dir / "build_exe.py"
    if not build_exe_path.exists():
        print("[ERROR] build_exe.py not found!")
        sys.exit(1)
    
    # Run build_exe directly in this process
    try:
        # Import and run build_exe directly
        sys.path.insert(0, str(builder_dir))
        from build_exe import build_exe
        result = build_exe()
        if result is None:
            print("[ERROR] Main executable build failed!")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    main_exe = dist_dir / f"{APP_NAME}.exe"
    if not main_exe.exists():
        print("[ERROR] Main executable not found!")
        sys.exit(1)
    
    size_mb = main_exe.stat().st_size / 1024 / 1024
    print(f"\n[OK] Main executable: {main_exe} ({size_mb:.2f} MB)")
    sys.stdout.flush()
    
    # Step 2: Build uninstaller
    print("\n[2/3] Building uninstaller...")
    sys.stdout.flush()
    
    uninstaller_py = builder_dir / "uninstaller.py"
    if not uninstaller_py.exists():
        print("[ERROR] uninstaller.py not found!")
        sys.exit(1)
    
    temp_dir = base_dir / "temp_build"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Build uninstaller with PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI_Uninstaller",
        "--onefile",
        "--console",
        "--noconfirm",
        "--clean",
        "--distpath", str(temp_dir / "dist"),
        "--workpath", str(temp_dir / "build"),
        str(uninstaller_py)
    ]
    
    print(f"[INFO] Running: {' '.join(cmd)}")
    sys.stdout.flush()
    
    try:
        subprocess.run(cmd, check=True, timeout=300)
        uninstaller_exe = temp_dir / "dist" / "NotYCaptionGenAI_Uninstaller.exe"
        if uninstaller_exe.exists():
            size_kb = uninstaller_exe.stat().st_size / 1024
            print(f"[OK] Uninstaller built: {size_kb:.2f} KB")
        else:
            print("[ERROR] Uninstaller not found!")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to build uninstaller: {e}")
        sys.exit(1)
    
    # Step 3: Create installer
    print("\n[3/3] Creating installer...")
    sys.stdout.flush()
    
    installer_dir = base_dir / "installer_temp"
    if installer_dir.exists():
        shutil.rmtree(installer_dir)
    installer_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    print("Copying files...")
    shutil.copy2(main_exe, installer_dir / f"{APP_NAME}.exe")
    shutil.copy2(uninstaller_exe, installer_dir / "NotYCaptionGenAI_Uninstaller.exe")
    
    # Copy resources
    resources_dir = base_dir / "resources"
    if resources_dir.exists():
        shutil.copytree(resources_dir, installer_dir / "resources")
    
    # Copy ffmpeg
    ffmpeg_dir = base_dir / "ffmpeg"
    if ffmpeg_dir.exists():
        shutil.copytree(ffmpeg_dir, installer_dir / "ffmpeg")
    
    # Copy models
    models_dir = base_dir / "models"
    if models_dir.exists():
        shutil.copytree(models_dir, installer_dir / "models")
    
    # Create installer script
    installer_script = installer_dir / "install.py"
    installer_content = '''import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "NotY Caption Generator AI"
EXE_NAME = "NotYCaptionGenAI.exe"

def install():
    print("=" * 60)
    print(f"Installing {APP_NAME} v5.2")
    print("=" * 60)
    
    # Default install path
    install_path = Path("C:\\\\NotYCaptionGenAI")
    install_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Installing to: {install_path}")
    
    # Copy files
    shutil.copy2(Path(sys.executable).parent / EXE_NAME, install_path / EXE_NAME)
    shutil.copy2(Path(sys.executable).parent / "NotYCaptionGenAI_Uninstaller.exe", install_path / "NotYCaptionGenAI_Uninstaller.exe")
    
    # Copy directories
    for dir_name in ["resources", "ffmpeg", "models"]:
        src = Path(sys.executable).parent / dir_name
        if src.exists():
            dst = install_path / dir_name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    
    # Create desktop shortcut
    desktop = Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAI.lnk"
    with open(desktop, 'w') as f:
        f.write("Shortcut to NotYCaptionGenAI")
    
    print("Installation complete!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    install()
'''
    
    with open(installer_script, 'w') as f:
        f.write(installer_content)
    
    # Create simple installer using IExpress or just copy
    print("Creating installer package...")
    
    # Create a self-extracting archive using 7zip if available
    final_installer = base_dir / INSTALLER_NAME
    
    # Simple copy for now
    import zipfile
    with zipfile.ZipFile(final_installer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(installer_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, installer_dir)
                zipf.write(file_path, arcname)
    
    if final_installer.exists():
        size_mb = final_installer.stat().st_size / 1024 / 1024
        print(f"\n[OK] Installer created: {final_installer} ({size_mb:.2f} MB)")
    else:
        print("[ERROR] Installer creation failed!")
        sys.exit(1)
    
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(installer_dir, ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"Installer: {final_installer}")
    print("=" * 60)
    sys.stdout.flush()

if __name__ == "__main__":
    build_all()