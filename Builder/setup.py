#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for building all components with optimized compression
NotY Caption Generator AI v4.3
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
    """Compress directory with maximum compression and file metadata"""
    print(f"  Compressing {src_dir}...")
    
    # Collect all files
    files = []
    total_size = 0
    
    for root, dirs, files_in_dir in os.walk(src_dir):
        for file in files_in_dir:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(src_dir)
            files.append((str(rel_path), file_path.stat().st_size))
            total_size += file_path.stat().st_size
    
    print(f"    Found {len(files)} files, total size: {total_size / 1024 / 1024:.2f} MB")
    
    # Create file list header
    header = '\n'.join([f"{f}|{s}" for f, s in files])
    header_bytes = header.encode('utf-8')
    
    # Create compressed data
    compressor = zlib.compressobj(zlib.Z_BEST_COMPRESSION)
    compressed_chunks = []
    
    # Add header
    compressed_chunks.append(compressor.compress(header_bytes))
    
    # Add file contents
    for rel_path, size in files:
        file_path = src_dir / rel_path
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                compressed_chunks.append(compressor.compress(chunk))
    
    compressed_chunks.append(compressor.flush())
    
    # Combine all chunks
    compressed_data = b''.join(compressed_chunks)
    
    # Write compressed file with size header
    with open(output_file, 'wb') as f:
        f.write(struct.pack('Q', len(compressed_data)))
        f.write(compressed_data)
    
    compressed_size = len(compressed_data) + 8
    print(f"    Compressed size: {compressed_size / 1024 / 1024:.2f} MB")
    print(f"    Compression ratio: {(1 - compressed_size / total_size) * 100:.1f}%")
    
    return compressed_size

def build_all():
    """Build all components"""
    print("=" * 60)
    print("Building NotY Caption Generator AI - Complete Package v4.3")
    print("Copyright (c) 2026 NotY215")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    temp_installer_dir = base_dir / "temp_installer"
    
    # Clean all directories
    print("\n[Cleanup] Removing old directories...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if temp_installer_dir.exists():
        shutil.rmtree(temp_installer_dir)
    
    # Create directories
    dist_dir.mkdir(parents=True, exist_ok=True)
    temp_installer_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Build main executable
    print("\n[1/3] Building main executable...")
    try:
        result = subprocess.run(
            [sys.executable, str(builder_dir / "build_exe.py")],
            capture_output=True,
            text=True,
            cwd=str(base_dir)
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to build main executable: {e}")
        sys.exit(1)
    
    # Check if main executable was created
    main_exe = dist_dir / "NotYCaptionGenAI.exe"
    if not main_exe.exists():
        print(f"\n[ERROR] Main executable not found at: {main_exe}")
        sys.exit(1)
    
    print(f"[OK] Main executable found: {main_exe}")
    print(f"   Size: {main_exe.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Step 2: Prepare installer package with maximum compression
    print("\n[2/3] Preparing installer package...")
    
    # Copy main executable
    print("  - Copying main executable...")
    shutil.copy2(main_exe, temp_installer_dir / "NotYCaptionGenAI.exe")
    
    # Copy installer scripts
    print("  - Copying installer scripts...")
    shutil.copy2(str(builder_dir / "installer.py"), str(temp_installer_dir / "installer.py"))
    shutil.copy2(str(builder_dir / "uninstaller.py"), str(temp_installer_dir / "uninstaller.py"))
    
    # Compress resources
    resources_src = base_dir / "resources"
    data_bin = temp_installer_dir / "data.bin"
    
    if resources_src.exists():
        print("  - Compressing resources...")
        compress_directory(resources_src, data_bin)
    else:
        print("  [WARNING] Resources not found")
    
    # Step 3: Build installer executable
    print("\n[3/3] Building installer executable...")
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Change to temp installer directory for building
    original_dir = os.getcwd()
    os.chdir(temp_installer_dir)
    
    # Build installer without UPX
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI_Installer_v4.3",
        "--onefile",
        "--noconfirm",
        f"--add-data={temp_installer_dir / 'NotYCaptionGenAI.exe'}{os.pathsep}.",
        f"--add-data={temp_installer_dir / 'installer.py'}{os.pathsep}.",
        f"--add-data={temp_installer_dir / 'uninstaller.py'}{os.pathsep}.",
        "--hidden-import=tkinter",
        "--hidden-import=threading",
        "--hidden-import=zlib",
        "--hidden-import=struct",
        "--noconsole",
        "installer.py"
    ]
    
    # Add data.bin if it exists
    if data_bin.exists():
        cmd.append(f"--add-data={data_bin}{os.pathsep}.")
    
    try:
        subprocess.check_call(cmd)
        print("  [OK] Installer built successfully")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Error building installer: {e}")
        os.chdir(original_dir)
        sys.exit(1)
    
    # Find the built installer
    installer_exe = None
    possible_paths = [
        temp_installer_dir / "dist" / "NotYCaptionGenAI_Installer_v4.3.exe",
        temp_installer_dir / "NotYCaptionGenAI_Installer_v4.3.exe",
    ]
    
    for path in possible_paths:
        if path.exists():
            installer_exe = path
            break
    
    if installer_exe:
        final_installer = dist_dir / "NotYCaptionGenAI_Installer_v4.3.exe"
        shutil.copy2(installer_exe, final_installer)
        print(f"\n  [OK] Installer created: {final_installer}")
        print(f"     Size: {final_installer.stat().st_size / 1024 / 1024:.2f} MB")
    else:
        print("  [ERROR] Installer executable not created!")
        os.chdir(original_dir)
        sys.exit(1)
    
    # Return to original directory
    os.chdir(original_dir)
    
    # Clean up temp directory
    print("\n[Cleanup] Removing temporary files...")
    shutil.rmtree(temp_installer_dir, ignore_errors=True)
    
    # Copy installer to root
    root_installer = base_dir / "NotYCaptionGenAI_Installer_v4.3.exe"
    final_installer = dist_dir / "NotYCaptionGenAI_Installer_v4.3.exe"
    
    if final_installer.exists():
        shutil.copy2(final_installer, root_installer)
        print(f"\n[OK] Installer copied to: {root_installer}")
    
    # Clean build directories
    build_dir = base_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("[OK] Build complete!")
    print(f"Installer: {root_installer}")
    print(f"Version: 4.3")
    if root_installer.exists():
        print(f"Size: {root_installer.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"Copyright (c) 2026 NotY215")
    print("=" * 60)

if __name__ == "__main__":
    build_all()