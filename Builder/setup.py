#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for building NotY Caption Generator AI v4.4
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
from pathlib import Path

def build_all():
    print("=" * 60)
    print("Building NotY Caption Generator AI v4.4")
    print("Copyright (c) 2026 NotY215")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Clean
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Build main executable
    print("\n[1/3] Building main executable...")
    
    # Import and run build_exe directly instead of subprocess
    sys.path.insert(0, str(builder_dir))
    from build_exe import build_exe
    
    try:
        main_exe = build_exe()
        if not main_exe or not main_exe.exists():
            print("\n❌ Main executable not found!")
            sys.exit(1)
        print(f"✅ Main executable: {main_exe} ({main_exe.stat().st_size / 1024 / 1024:.2f} MB)")
    except Exception as e:
        print(f"\n❌ Failed to build main executable: {e}")
        sys.exit(1)
    
    # Step 2: Build uninstaller executable
    print("\n[2/3] Building uninstaller executable...")
    temp_build_dir = base_dir / "temp_build"
    if temp_build_dir.exists():
        shutil.rmtree(temp_build_dir)
    temp_build_dir.mkdir(parents=True, exist_ok=True)
    
    # Import and run uninstaller build
    try:
        # Change to temp directory to avoid running the script
        original_dir = os.getcwd()
        os.chdir(temp_build_dir)
        
        import PyInstaller.__main__
        
        uninstaller_py = str(builder_dir / "uninstaller.py")
        
        PyInstaller.__main__.run([
            '--name=NotYCaptionGenAI_Uninstaller',
            '--onefile',
            '--console',
            '--noconfirm',
            uninstaller_py
        ])
        
        uninstaller_exe = temp_build_dir / "dist" / "NotYCaptionGenAI_Uninstaller.exe"
        if uninstaller_exe.exists():
            print(f"    ✅ Uninstaller built: {uninstaller_exe.name}")
            print(f"✅ Uninstaller: {uninstaller_exe} ({uninstaller_exe.stat().st_size / 1024 / 1024:.2f} MB)")
        else:
            print("    ❌ Uninstaller not found!")
            sys.exit(1)
            
    except Exception as e:
        print(f"    ❌ Failed to build uninstaller: {e}")
        sys.exit(1)
    finally:
        os.chdir(original_dir)
    
    # Step 3: Build installer with both executables
    print("\n[3/3] Building console installer with models and uninstaller...")
    
    # Create temp directory for installer files
    temp_dir = base_dir / "temp_installer"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy main executable
    shutil.copy2(main_exe, temp_dir / "NotYCaptionGenAI.exe")
    
    # Copy uninstaller executable
    shutil.copy2(uninstaller_exe, temp_dir / "NotYCaptionGenAI_Uninstaller.exe")
    
    # Copy resources (FFmpeg files and icons)
    resources_dir = base_dir / "resources"
    if resources_dir.exists():
        shutil.copytree(resources_dir, temp_dir / "resources")
    
    # Copy models to temp
    models_dir = base_dir / "models"
    if models_dir.exists() and any(models_dir.iterdir()):
        print("  Including models from:", models_dir)
        dest_models = temp_dir / "models"
        shutil.copytree(models_dir, dest_models)
        model_count = len(list(dest_models.glob("*.pt")))
        total_size = sum(f.stat().st_size for f in dest_models.glob("*.pt")) / (1024 * 1024)
        print(f"    Added {model_count} models ({total_size:.2f} MB)")
    
    # Build installer using pyinstaller
    print("\nBuilding installer with PyInstaller...")
    
    installer_py = str(builder_dir / "installer_console.py")
    
    # Build command with all data files
    cmd = [
        '--name=NotYCaptionGenAI_Installer_v4.4',
        '--onefile',
        f'--add-data={temp_dir / "NotYCaptionGenAI.exe"}{os.pathsep}.',
        f'--add-data={temp_dir / "NotYCaptionGenAI_Uninstaller.exe"}{os.pathsep}.',
        f'--add-data={temp_dir / "resources"}{os.pathsep}resources',
        '--hidden-import=ctypes',
        '--hidden-import=struct',
        '--hidden-import=subprocess',
        '--hidden-import=shutil',
        '--hidden-import=pathlib',
        '--hidden-import=platform',
        '--hidden-import=tkinter',
        '--hidden-import=filedialog',
        '--console',
        '--noconfirm',
        installer_py
    ]
    
    # Add models if they exist
    models_path = temp_dir / "models"
    if models_path.exists():
        for model_file in models_path.glob("*.pt"):
            cmd.insert(4, f'--add-data={model_file}{os.pathsep}models')
            print(f"    Adding model: {model_file.name}")
    
    # Add icon if exists
    icon_path = temp_dir / "resources" / "logo.ico"
    if icon_path.exists():
        cmd.insert(4, f'--icon={icon_path}')
    
    # Run PyInstaller
    try:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        PyInstaller.__main__.run(cmd)
        print("\n✅ Installer built successfully!")
    except Exception as e:
        print(f"\n❌ Installer build failed: {e}")
        sys.exit(1)
    finally:
        os.chdir(original_dir)
    
    # Find and copy installer to root
    installer_exe = temp_dir / "dist" / "NotYCaptionGenAI_Installer_v4.4.exe"
    if not installer_exe.exists():
        installer_exe = temp_dir / "NotYCaptionGenAI_Installer_v4.4.exe"
    
    if installer_exe.exists():
        final_installer = base_dir / "NotYCaptionGenAI_Installer_v4.4.exe"
        shutil.copy2(installer_exe, final_installer)
        size = final_installer.stat().st_size / 1024 / 1024
        print(f"\n✅ Installer created: {final_installer} ({size:.2f} MB)")
    else:
        print("\n❌ Installer not found!")
    
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(temp_build_dir, ignore_errors=True)
    
    # Clean up dist folder - only keep installer
    print("\n[Cleanup] Cleaning dist folder...")
    for item in dist_dir.iterdir():
        if item.name != "NotYCaptionGenAI_Installer_v4.4.exe":
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
    
    # Clean build directories
    build_dir = base_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
    
    builder_build = builder_dir / "build"
    if builder_build.exists():
        shutil.rmtree(builder_build, ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"Installer: {base_dir / 'NotYCaptionGenAI_Installer_v4.4.exe'}")
    print("=" * 60)

if __name__ == "__main__":
    build_all()