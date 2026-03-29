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

def compress_directory(src_dir, output_file):
    """Compress directory with maximum compression"""
    if not src_dir.exists() or not any(src_dir.iterdir()):
        print(f"  Skipping {src_dir} - empty or not found")
        return None
    
    print(f"  Compressing {src_dir}...")
    
    files = []
    total_size = 0
    
    for root, dirs, files_in_dir in os.walk(src_dir):
        for file in files_in_dir:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(src_dir)
            files.append((str(rel_path), file_path.stat().st_size))
            total_size += file_path.stat().st_size
    
    if not files:
        print(f"    No files found in {src_dir}")
        return None
    
    print(f"    Found {len(files)} files, total size: {total_size / 1024 / 1024:.2f} MB")
    
    # Create header
    header = '\n'.join([f"{f}|{s}" for f, s in files])
    header_bytes = header.encode('utf-8')
    
    # Compress
    compressor = zlib.compressobj(zlib.Z_BEST_COMPRESSION)
    compressed_chunks = [compressor.compress(header_bytes)]
    
    for rel_path, size in files:
        file_path = src_dir / rel_path
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                compressed_chunks.append(compressor.compress(chunk))
    
    compressed_chunks.append(compressor.flush())
    compressed_data = b''.join(compressed_chunks)
    
    with open(output_file, 'wb') as f:
        f.write(struct.pack('Q', len(compressed_data)))
        f.write(compressed_data)
    
    compressed_size = len(compressed_data) + 8
    print(f"    Compressed size: {compressed_size / 1024 / 1024:.2f} MB")
    print(f"    Compression ratio: {(1 - compressed_size / total_size) * 100:.1f}%")
    
    return compressed_size

def build_all():
    print("=" * 60)
    print("Building NotY Caption Generator AI v4.3")
    print("Copyright (c) 2026 NotY215")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    temp_installer = base_dir / "temp_installer"
    
    # Clean
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if temp_installer.exists():
        shutil.rmtree(temp_installer)
    
    dist_dir.mkdir(parents=True, exist_ok=True)
    temp_installer.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Build main executable
    print("\n[1/3] Building main executable...")
    try:
        subprocess.check_call([sys.executable, str(builder_dir / "build_exe.py")])
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to build main executable: {e}")
        sys.exit(1)
    
    main_exe = dist_dir / "NotYCaptionGenAI.exe"
    if not main_exe.exists():
        print("\n❌ Main executable not found!")
        sys.exit(1)
    
    # Step 2: Prepare installer files
    print("\n[2/3] Preparing installer files...")
    
    # Copy main executable
    shutil.copy2(main_exe, temp_installer / "NotYCaptionGenAI.exe")
    
    # Copy icon
    resources_dir = base_dir / "resources"
    logo_icon = resources_dir / "logo.ico"
    if logo_icon.exists():
        shutil.copy2(logo_icon, temp_installer / "logo.ico")
    
    # Compress models directory
    models_dir = base_dir / "models"
    if models_dir.exists() and any(models_dir.iterdir()):
        compress_directory(models_dir, temp_installer / "models.bin")
    else:
        print("  No models found to compress")
    
    # Compress files directory (FFmpeg)
    files_dir = resources_dir / "Files"
    if files_dir.exists() and any(files_dir.iterdir()):
        compress_directory(files_dir, temp_installer / "files.bin")
    else:
        print("  No files found to compress")
    
    # Step 3: Build installer
    print("\n[3/3] Building installer executable...")
    
    # Create spec for installer
    installer_py = str(builder_dir / "installer.py").replace('\\', '/')
    main_exe_path = str(temp_installer / "NotYCaptionGenAI.exe").replace('\\', '/')
    logo_path = str(temp_installer / "logo.ico").replace('\\', '/')
    
    datas = [f"(r'{main_exe_path}', '.'), (r'{logo_path}', '.')"]
    
    if (temp_installer / "models.bin").exists():
        models_path = str(temp_installer / "models.bin").replace('\\', '/')
        datas.append(f"(r'{models_path}', '.')")
    
    if (temp_installer / "files.bin").exists():
        files_path = str(temp_installer / "files.bin").replace('\\', '/')
        datas.append(f"(r'{files_path}', '.')")
    
    datas_str = ",\n        ".join(datas)
    
    installer_spec = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    [r'{installer_py}'],
    pathex=[],
    binaries=[],
    datas=[
        {datas_str}
    ],
    hiddenimports=['tkinter', 'threading', 'zlib', 'struct'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{logo_path}'
)
'''
    
    spec_path = builder_dir / "Installer.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(installer_spec)
    
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
    shutil.rmtree(temp_installer, ignore_errors=True)
    shutil.rmtree(builder_dir / "build_installer", ignore_errors=True)
    
    # Find the installer
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