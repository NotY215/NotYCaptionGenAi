#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI - Build Orchestrator v7.1
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def clean_all():
    """Clean all build artifacts"""
    print(f"{Colors.CYAN}Cleaning build artifacts...{Colors.ENDC}")
    
    dirs_to_clean = ['build', 'dist', 'temp_installer', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Cleaned: {dir_path}")
    
    for pattern in files_to_clean:
        for file in Path('.').glob(pattern):
            file.unlink()
            print(f"  Cleaned: {file}")
    
    # Clean Builder directory
    builder_dir = Path('Builder')
    if builder_dir.exists():
        for dir_name in dirs_to_clean:
            dir_path = builder_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  Cleaned: {dir_path}")
        
        for pattern in files_to_clean:
            for file in builder_dir.glob(pattern):
                file.unlink()
                print(f"  Cleaned: {file}")
    
    print(f"{Colors.GREEN}Clean complete!{Colors.ENDC}\n")


def check_requirements():
    """Check if required tools are installed"""
    print(f"{Colors.CYAN}Checking requirements...{Colors.ENDC}")
    
    # Check PyInstaller
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                       capture_output=True, check=True)
        print(f"  {Colors.GREEN}✓ PyInstaller installed{Colors.ENDC}")
    except:
        print(f"  {Colors.WARNING}✗ PyInstaller not installed. Installing...{Colors.ENDC}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print(f"  {Colors.GREEN}✓ PyInstaller installed{Colors.ENDC}")
    
    # Check FFmpeg
    ffmpeg_dir = Path('ffmpeg')
    if ffmpeg_dir.exists() and (ffmpeg_dir / 'ffmpeg.exe').exists():
        print(f"  {Colors.GREEN}✓ FFmpeg found{Colors.ENDC}")
    else:
        print(f"  {Colors.WARNING}✗ FFmpeg not found in ffmpeg/ directory{Colors.ENDC}")
        print(f"  {Colors.WARNING}  Please place ffmpeg.exe, ffprobe.exe, ffplay.exe in ffmpeg/ folder{Colors.ENDC}")
    
    # Check resources
    resources_dir = Path('resources')
    if resources_dir.exists():
        if (resources_dir / 'app.ico').exists():
            print(f"  {Colors.GREEN}✓ app.ico found{Colors.ENDC}")
        else:
            print(f"  {Colors.WARNING}✗ app.ico not found{Colors.ENDC}")
        
        if (resources_dir / 'logo.ico').exists():
            print(f"  {Colors.GREEN}✓ logo.ico found{Colors.ENDC}")
        else:
            print(f"  {Colors.WARNING}✗ logo.ico not found{Colors.ENDC}")
    else:
        print(f"  {Colors.WARNING}✗ resources/ directory not found{Colors.ENDC}")
    
    print()


def build_pure_exe():
    """Build the pure code executable"""
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}  Step 1: Building Pure Code Executable{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
    
    builder_path = Path('Builder/build_exe.py')
    if not builder_path.exists():
        print(f"{Colors.FAIL}Error: Builder/build_exe.py not found!{Colors.ENDC}")
        return False
    
    result = subprocess.run([sys.executable, str(builder_path)])
    if result.returncode != 0:
        print(f"{Colors.FAIL}Failed to build pure executable!{Colors.ENDC}")
        return False
    
    # Check output
    exe_path = Path('dist/NotYCaptionGenAI.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n{Colors.GREEN}✓ Pure executable built: {size_mb:.2f} MB{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}Output file not found!{Colors.ENDC}")
        return False


def build_installer():
    """Build the full installer"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}  Step 2: Building Full Installer{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
    
    builder_path = Path('Builder/build_installer.py')
    if not builder_path.exists():
        print(f"{Colors.FAIL}Error: Builder/build_installer.py not found!{Colors.ENDC}")
        return False
    
    result = subprocess.run([sys.executable, str(builder_path)])
    if result.returncode != 0:
        print(f"{Colors.FAIL}Failed to build installer!{Colors.ENDC}")
        return False
    
    # Check output
    installer_pattern = "NotYCaptionGenAI_Installer_v*.exe"
    import glob
    installers = glob.glob(installer_pattern)
    
    if installers:
        latest = max(installers, key=os.path.getctime)
        size_mb = Path(latest).stat().st_size / (1024 * 1024)
        print(f"\n{Colors.GREEN}✓ Installer built: {latest} ({size_mb:.2f} MB){Colors.ENDC}")
        return True
    else:
        print(f"{Colors.FAIL}Installer not found!{Colors.ENDC}")
        return False


def show_summary():
    """Show build summary"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}  Build Complete!{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
    
    # Find files
    import glob
    
    pure_exe = Path('dist/NotYCaptionGenAI.exe')
    if pure_exe.exists():
        size_mb = pure_exe.stat().st_size / (1024 * 1024)
        print(f"\n{Colors.GREEN}Pure Executable:{Colors.ENDC}")
        print(f"  File: {pure_exe}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Usage: Run directly - no Python required")
    
    installers = glob.glob("NotYCaptionGenAI_Installer_v*.exe")
    if installers:
        latest = max(installers, key=os.path.getctime)
        size_mb = Path(latest).stat().st_size / (1024 * 1024)
        print(f"\n{Colors.GREEN}Installer:{Colors.ENDC}")
        print(f"  File: {latest}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Usage: Double-click to install")
    
    print(f"\n{Colors.CYAN}Next Steps:{Colors.ENDC}")
    print(f"  1. Distribute the installer to users")
    print(f"  2. Or use the pure executable for development/testing")
    print(f"  3. Ensure ffmpeg/ directory contains ffmpeg.exe, ffprobe.exe, ffplay.exe")
    print(f"  4. Place Whisper models in models/ folder for faster first run")
    
    print(f"\n{Colors.GREEN}Build successful!{Colors.ENDC}")


def main():
    """Main build orchestrator"""
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}  NotY Caption Generator AI v7.1 - Build System{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    # Change to project root directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Clean previous builds
    clean_all()
    
    # Check requirements
    check_requirements()
    
    # Confirm before building
    print(f"{Colors.WARNING}This will build both the pure executable and the full installer.{Colors.ENDC}")
    print(f"{Colors.WARNING}The full installer may take several minutes and require ~2GB of disk space.{Colors.ENDC}")
    
    confirm = input(f"\n{Colors.BOLD}Continue with build? (y/n): {Colors.ENDC}").lower()
    if confirm != 'y':
        print("Build cancelled.")
        sys.exit(0)
    
    # Build pure executable
    if not build_pure_exe():
        print(f"{Colors.FAIL}Build failed at step 1!{Colors.ENDC}")
        sys.exit(1)
    
    # Build installer
    if not build_installer():
        print(f"{Colors.FAIL}Build failed at step 2!{Colors.ENDC}")
        sys.exit(1)
    
    # Show summary
    show_summary()


if __name__ == "__main__":
    main()