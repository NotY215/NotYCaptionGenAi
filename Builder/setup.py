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
from pathlib import Path

def build_all():
    print("=" * 60)
    print("Building NotY Caption Generator AI v4.3")
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
    print("\n[1/2] Building main executable...")
    try:
        subprocess.check_call([sys.executable, str(builder_dir / "build_exe.py")])
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to build main executable: {e}")
        sys.exit(1)
    
    main_exe = dist_dir / "NotYCaptionGenAI.exe"
    if not main_exe.exists():
        print("\n❌ Main executable not found!")
        sys.exit(1)
    
    print(f"✅ Main executable: {main_exe} ({main_exe.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # Step 2: Build installer
    print("\n[2/2] Building console installer...")
    
    # Create spec for installer
    installer_py = str(builder_dir / "installer_console.py").replace('\\', '/')
    main_exe_path = str(main_exe).replace('\\', '/')
    
    # Copy resources to temp
    temp_dir = base_dir / "temp_resources"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy resources
    resources_dir = base_dir / "resources"
    if resources_dir.exists():
        shutil.copytree(resources_dir, temp_dir / "resources")
    
    # Copy models if they exist
    models_dir = base_dir / "models"
    if models_dir.exists() and any(models_dir.iterdir()):
        shutil.copytree(models_dir, temp_dir / "models")
    
    # Create spec file
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    [r'{installer_py}'],
    pathex=[],
    binaries=[],
    datas=[
        (r'{main_exe_path}', '.'),
        (r'{temp_dir / "resources"}', 'resources'),
    ],
    hiddenimports=['ctypes', 'struct', 'subprocess', 'shutil', 'pathlib', 'zipfile'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Add models if they exist
models_dir = r'{temp_dir / "models"}'
if os.path.exists(models_dir):
    a.datas += Tree(models_dir, prefix='models')

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NotYCaptionGenAI_Installer_v4.3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{temp_dir / "resources/logo.ico"}'
)
'''
    
    spec_path = builder_dir / "Installer.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    # Build installer
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build_installer"),
        "--noconfirm"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n✅ Installer built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installer build failed: {e}")
        sys.exit(1)
    
    # Clean up
    spec_path.unlink(missing_ok=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(builder_dir / "build_installer", ignore_errors=True)
    
    # Copy installer to root
    installer_exe = dist_dir / "NotYCaptionGenAI_Installer_v4.3.exe"
    if installer_exe.exists():
        final_installer = base_dir / "NotYCaptionGenAI_Installer_v4.3.exe"
        shutil.copy2(installer_exe, final_installer)
        size = final_installer.stat().st_size / 1024 / 1024
        print(f"\n✅ Installer created: {final_installer} ({size:.2f} MB)")
    else:
        print("\n❌ Installer not found!")
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)

if __name__ == "__main__":
    build_all()