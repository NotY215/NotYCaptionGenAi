#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI - Build Installer v7.1
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import site
from pathlib import Path


VERSION = "7.1"
APP_NAME = "NotYCaptionGenAI"
INSTALLER_NAME = f"NotYCaptionGenAI_Installer_v{VERSION}"


def clean_build_artifacts():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', 'temp_installer', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Cleaned: {dir_path}")
            
    for pattern in files_to_clean:
        for file in Path('.').glob(pattern):
            file.unlink()
            print(f"Cleaned: {file}")


def get_site_packages():
    """Get the site-packages directory"""
    for path in site.getsitepackages():
        if 'site-packages' in path:
            return Path(path)
    
    # Fallback
    for path in sys.path:
        if 'site-packages' in path:
            return Path(path)
    
    raise RuntimeError("Could not find site-packages directory")


def copy_packages():
    """Copy all required packages to _pythonPackages_ folder"""
    print("\nCopying Python packages...")
    
    packages_dir = Path('temp_installer/_pythonPackages_')
    packages_dir.mkdir(parents=True, exist_ok=True)
    
    # Packages to include
    packages = [
        'PyQt5', 'whisper', 'torch', 'torchaudio', 'tensorflow',
        'spleeter', 'numpy', 'numba', 'llvmlite', 'librosa',
        'soundfile', 'moviepy', 'pysrt', 'pysubs2', 'yt_dlp',
        'tqdm', 'regex', 'tiktoken', 'requests', 'colorama'
    ]
    
    site_packages = get_site_packages()
    copied_count = 0
    
    for package in packages:
        src = site_packages / package
        dst = packages_dir / package
        
        if src.exists():
            try:
                if src.is_dir():
                    shutil.copytree(src, dst, ignore_dangling_symlinks=True)
                else:
                    shutil.copy2(src, dst)
                copied_count += 1
                print(f"  Copied: {package}")
            except Exception as e:
                print(f"  Warning: Could not copy {package}: {e}")
        else:
            # Try with hyphens instead of underscores
            alt_name = package.replace('_', '-')
            src = site_packages / alt_name
            if src.exists():
                shutil.copytree(src, dst, ignore_dangling_symlinks=True)
                copied_count += 1
                print(f"  Copied: {alt_name}")
            else:
                print(f"  Warning: {package} not found")
    
    print(f"\nCopied {copied_count} packages to {packages_dir}")
    return packages_dir


def build_installer():
    """Build the full installer with all packages"""
    print("=" * 60)
    print(f"  NotY Caption Generator AI - Build Installer v{VERSION}")
    print("=" * 60)
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Create temp directory
    temp_dir = Path('temp_installer')
    temp_dir.mkdir(exist_ok=True)
    
    # Copy required files
    print("\nCopying files...")
    
    # Copy executable
    exe_src = Path('dist/NotYCaptionGenAI.exe')
    if not exe_src.exists():
        print("Error: NotYCaptionGenAI.exe not found. Run build_exe.py first.")
        sys.exit(1)
    
    exe_dst = temp_dir / 'NotYCaptionGenAI.exe'
    shutil.copy2(exe_src, exe_dst)
    print(f"  Copied: {exe_src.name}")
    
    # Copy FFmpeg
    ffmpeg_src = Path('ffmpeg')
    if ffmpeg_src.exists():
        ffmpeg_dst = temp_dir / 'ffmpeg'
        shutil.copytree(ffmpeg_src, ffmpeg_dst)
        print(f"  Copied: ffmpeg/")
    
    # Copy models
    models_src = Path('models')
    if models_src.exists():
        models_dst = temp_dir / 'models'
        shutil.copytree(models_src, models_dst)
        print(f"  Copied: models/")
    
    # Copy pretrained models
    pretrained_src = Path('pretrained_models')
    if pretrained_src.exists():
        pretrained_dst = temp_dir / 'pretrained_models'
        shutil.copytree(pretrained_src, pretrained_dst)
        print(f"  Copied: pretrained_models/")
    
    # Copy resources
    resources_src = Path('resources')
    if resources_src.exists():
        resources_dst = temp_dir / 'resources'
        shutil.copytree(resources_src, resources_dst)
        print(f"  Copied: resources/")
    
    # Copy Python packages
    copy_packages()
    
    # Copy installer script
    installer_src = Path('Builder/installer_console.py')
    installer_dst = temp_dir / 'installer.py'
    shutil.copy2(installer_src, installer_dst)
    print(f"  Copied: installer_console.py")
    
    # Copy uninstaller
    uninstaller_src = Path('Builder/uninstaller.py')
    uninstaller_dst = temp_dir / 'uninstaller.py'
    shutil.copy2(uninstaller_src, uninstaller_dst)
    print(f"  Copied: uninstaller.py")
    
    # Build final installer using PyInstaller
    print("\nBuilding final installer...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--name', INSTALLER_NAME,
        '--icon', 'resources/logo.ico',
        '--add-data', f'temp_installer;.',
        '--hidden-import', 'winreg',
        '--hidden-import', 'ctypes',
        'Builder/installer_console.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        # Move installer to root directory
        installer_exe = Path(f'dist/{INSTALLER_NAME}.exe')
        if installer_exe.exists():
            final_path = Path(f'{INSTALLER_NAME}.exe')
            shutil.move(str(installer_exe), str(final_path))
            print(f"\n{Colors.GREEN}Installer built successfully!{Colors.ENDC}")
            
            size_mb = final_path.stat().st_size / (1024 * 1024)
            print(f"\nOutput: {final_path}")
            print(f"Size: {size_mb:.2f} MB")
            
    except subprocess.CalledProcessError as e:
        print(f"\n{Colors.FAIL}Build failed: {e}{Colors.ENDC}")
        sys.exit(1)
    
    # Cleanup temp directory
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("\nCleaned up temporary files")


class Colors:
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


if __name__ == "__main__":
    build_installer()