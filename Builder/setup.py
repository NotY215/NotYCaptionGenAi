#!/usr/bin/env python3
"""
Setup script for building all components
NotY Caption Generator AI v4.2
Copyright © 2026 NotY215
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_all():
    """Build all components"""
    print("=" * 60)
    print("Building NotY Caption Generator AI - Complete Package v4.2")
    print("Copyright © 2026 NotY215")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    installer_dir = dist_dir / "NotYCaptionGenAi_Installer"
    
    # Clean dist directory
    if dist_dir.exists():
        print("\nCleaning old dist directory...")
        shutil.rmtree(dist_dir)
    
    # Create dist directory
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Build main executable
    print("\n[1/3] Building main executable...")
    subprocess.check_call([sys.executable, str(builder_dir / "build_exe.py")])
    
    # Create installer directory
    print("\n[2/3] Creating installer package...")
    installer_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy installer files
    print("  - Copying installer scripts...")
    shutil.copy2(str(builder_dir / "installer.py"), str(installer_dir / "installer.py"))
    shutil.copy2(str(builder_dir / "uninstaller.py"), str(installer_dir / "uninstaller.py"))
    
    # Copy resources
    print("  - Copying resources...")
    resources_src = base_dir / "resources"
    resources_dest = installer_dir / "resources"
    
    if resources_dest.exists():
        shutil.rmtree(resources_dest)
    shutil.copytree(resources_src, resources_dest)
    
    # Copy main executable
    print("  - Copying main executable...")
    exe_src = base_dir / "dist" / "NotYCaptionGenAI.exe"
    if exe_src.exists():
        shutil.copy2(exe_src, installer_dir / "NotYCaptionGenAI.exe")
    else:
        print("  - ERROR: Main executable not found!")
        sys.exit(1)
    
    # Build installer executable
    print("\n[3/3] Building installer executable...")
    try:
        import PyInstaller
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Change to installer directory for building
    original_dir = os.getcwd()
    os.chdir(installer_dir)
    
    # Build installer
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI_Installer_v4.2",
        "--onefile",
        f"--icon={resources_dest / 'logo.ico'}",
        f"--add-data={resources_dest}{os.pathsep}resources",
        "--hidden-import=tkinter",
        "--hidden-import=colorama",
        "--hidden-import=threading",
        "--noconsole",
        "installer.py"
    ]
    
    try:
        subprocess.check_call(cmd)
    except Exception as e:
        print(f"  - Error building installer: {e}")
        os.chdir(original_dir)
        sys.exit(1)
    
    # Move installer to dist directory
    installer_exe = installer_dir / "dist" / "NotYCaptionGenAI_Installer_v4.2.exe"
    if installer_exe.exists():
        final_installer = dist_dir / "NotYCaptionGenAI_Installer_v4.2.exe"
        shutil.move(str(installer_exe), str(final_installer))
        print(f"\n  ✅ Installer created: {final_installer}")
    else:
        print("  - ERROR: Installer executable not created!")
    
    # Return to original directory
    os.chdir(original_dir)
    
    # Clean up build directories
    print("\n[Cleanup] Removing temporary files...")
    
    # Clean installer build files
    installer_build = installer_dir / "build"
    installer_dist = installer_dir / "dist"
    installer_spec = installer_dir / "NotYCaptionGenAI_Installer_v4.2.spec"
    
    shutil.rmtree(installer_build, ignore_errors=True)
    shutil.rmtree(installer_dist, ignore_errors=True)
    if installer_spec.exists():
        installer_spec.unlink()
    
    # Clean main build files
    main_build = builder_dir / "build"
    main_dist = builder_dir / "dist"
    main_spec = builder_dir / "NotYCaptionGenAI.spec"
    
    shutil.rmtree(main_build, ignore_errors=True)
    shutil.rmtree(main_dist, ignore_errors=True)
    if main_spec.exists():
        main_spec.unlink()
    
    # Remove installer directory
    shutil.rmtree(installer_dir, ignore_errors=True)
    
    # Move installer to root
    final_installer = dist_dir / "NotYCaptionGenAI_Installer_v4.2.exe"
    root_installer = base_dir / "NotYCaptionGenAI_Installer_v4.2.exe"
    
    if final_installer.exists():
        shutil.copy2(final_installer, root_installer)
        print(f"\n✅ Installer copied to: {root_installer}")
    
    print("\n" + "=" * 60)
    print("✅ Build complete!")
    print(f"Installer: {root_installer}")
    print("Version: 4.2")
    print("Copyright © 2026 NotY215")
    print("=" * 60)

if __name__ == "__main__":
    build_all()