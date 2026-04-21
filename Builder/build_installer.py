#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Installer v7.1
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "7.1"
INSTALLER_NAME = f"{APP_NAME}_Installer_v{APP_VERSION}.exe"
UNINSTALLER_NAME = "Uninstaller.exe"
PACKAGES_FOLDER = "_pythonPackages_"

def clean_build_artifacts(builder_dir):
    for item in builder_dir.glob("build"):
        if item.is_dir():
            shutil.rmtree(item)
    for item in builder_dir.glob("dist"):
        if item.is_dir():
            shutil.rmtree(item)
    for spec in builder_dir.glob("*.spec"):
        spec.unlink()

def get_site_packages():
    result = subprocess.run(
        [sys.executable, "-c", "import site; print(site.getsitepackages()[0])"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        path = result.stdout.strip()
        if os.path.exists(path):
            return Path(path)
    return Path(sys.prefix) / "Lib" / "site-packages"

def copy_package(src, dst, name):
    if not src.exists():
        return False
    try:
        if src.is_dir():
            shutil.copytree(src, dst, ignore_dangling_symlinks=True,
                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo', 'tests', 'test', 'docs'))
        else:
            shutil.copy2(src, dst)
        return True
    except:
        return False

def build_installer():
    print("=" * 60)
    print(f"Building {APP_NAME} Installer v{APP_VERSION}")
    print("=" * 60)

    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    temp_dir = base_dir / "temp_installer"
    resources_dir = base_dir / "resources"

    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        print("[ERROR] Main executable not found! Run build_exe.py first.")
        return None

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    print("\n[1/7] Preparing installer files...")
    shutil.copy2(exe_file, temp_dir / f"{APP_NAME}.exe")
    print("  Copied main executable")

    print("\n[2/7] Building uninstaller...")
    uninstaller_py = builder_dir / "uninstaller.py"
    logo_ico = resources_dir / "logo.ico"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={UNINSTALLER_NAME.replace('.exe', '')}",
        "--onefile",
        "--console",
        "--noconfirm",
        "--clean",
        "--log-level=WARN",
        str(uninstaller_py)
    ]

    if logo_ico.exists():
        cmd.insert(4, f"--icon={logo_ico}")

    try:
        subprocess.run(cmd, cwd=str(builder_dir), check=True, timeout=180)
        uninstaller_exe = builder_dir / "dist" / UNINSTALLER_NAME
        if uninstaller_exe.exists():
            shutil.copy2(uninstaller_exe, temp_dir / UNINSTALLER_NAME)
            print("  Copied uninstaller")
    except Exception as e:
        print(f"[ERROR] Uninstaller build failed: {e}")
        return None

    print("\n[3/7] Copying Python packages...")
    site_packages = get_site_packages()
    print(f"  Source: {site_packages}")
    
    packages_dir = temp_dir / PACKAGES_FOLDER
    packages_dir.mkdir(exist_ok=True)
    
    packages_to_copy = [
        "whisper", "torch", "torchaudio", "numpy", "yt_dlp",
        "colorama", "tqdm", "regex", "tiktoken", "requests",
        "urllib3", "certifi", "charset_normalizer", "idna",
        "packaging", "setuptools", "wheel", "six", "typing_extensions",
        "filelock", "sympy", "networkx", "jinja2", "markupsafe"
    ]
    
    copied = 0
    for pkg in packages_to_copy:
        src = site_packages / pkg
        if src.exists():
            dest = packages_dir / pkg
            if copy_package(src, dest, pkg):
                copied += 1
                print(f"  Copied: {pkg}")
        else:
            alt_name = pkg.replace('-', '_')
            src = site_packages / alt_name
            if src.exists():
                dest = packages_dir / alt_name
                if copy_package(src, dest, alt_name):
                    copied += 1
                    print(f"  Copied: {alt_name}")
    
    for pyd in site_packages.glob("*.pyd"):
        try:
            shutil.copy2(pyd, packages_dir / pyd.name)
            copied += 1
        except:
            pass
    
    print(f"  Total packages copied: {copied}")

    print("\n[4/7] Copying resources...")
    if resources_dir.exists():
        dest_resources = temp_dir / "resources"
        if dest_resources.exists():
            shutil.rmtree(dest_resources)
        shutil.copytree(resources_dir, dest_resources)
        print("  Copied resources")

    print("\n[5/7] Copying ffmpeg...")
    ffmpeg_dir = base_dir / "ffmpeg"
    if ffmpeg_dir.exists():
        dest_ffmpeg = temp_dir / "ffmpeg"
        if dest_ffmpeg.exists():
            shutil.rmtree(dest_ffmpeg)
        shutil.copytree(ffmpeg_dir, dest_ffmpeg)
        print("  Copied ffmpeg")

    print("\n[6/7] Copying models...")
    models_dir = base_dir / "models"
    if models_dir.exists():
        dest_models = temp_dir / "models"
        if dest_models.exists():
            shutil.rmtree(dest_models)
        shutil.copytree(models_dir, dest_models)
        print("  Copied Whisper models")

    pretrained_dir = base_dir / "pretrained_models"
    if pretrained_dir.exists():
        dest_pretrained = temp_dir / "pretrained_models"
        if dest_pretrained.exists():
            shutil.rmtree(dest_pretrained)
        shutil.copytree(pretrained_dir, dest_pretrained)
        print("  Copied Spleeter models")

    print("\n[7/7] Building installer executable...")
    installer_script = builder_dir / "installer_console.py"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={APP_NAME}_Installer_v{APP_VERSION}",
        "--onefile",
        "--console",
        f"--add-data={temp_dir / f'{APP_NAME}.exe'}{os.pathsep}.",
        f"--add-data={temp_dir / UNINSTALLER_NAME}{os.pathsep}.",
        f"--add-data={temp_dir / PACKAGES_FOLDER}{os.pathsep}{PACKAGES_FOLDER}",
        f"--add-data={temp_dir / 'resources'}{os.pathsep}resources",
        f"--add-data={temp_dir / 'ffmpeg'}{os.pathsep}ffmpeg",
        f"--add-data={temp_dir / 'models'}{os.pathsep}models",
        f"--add-data={temp_dir / 'pretrained_models'}{os.pathsep}pretrained_models",
        "--hidden-import=ctypes",
        "--hidden-import=winreg",
        "--hidden-import=tkinter",
        "--noconfirm",
        "--clean",
        "--log-level=WARN",
        str(installer_script)
    ]

    if logo_ico.exists():
        cmd.insert(4, f"--icon={logo_ico}")

    try:
        subprocess.run(cmd, cwd=str(builder_dir), check=True, timeout=600)
        
        installer_exe = builder_dir / "dist" / f"{APP_NAME}_Installer_v{APP_VERSION}.exe"
        if installer_exe.exists():
            final_installer = base_dir / INSTALLER_NAME
            shutil.copy2(installer_exe, final_installer)
            size = final_installer.stat().st_size / 1024 / 1024
            print(f"\n[OK] Installer created: {final_installer} ({size:.2f} MB)")
            return final_installer
        else:
            print("[ERROR] Installer not found!")
            return None
    except Exception as e:
        print(f"[ERROR] Installer build failed: {e}")
        return None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        clean_build_artifacts(builder_dir)

if __name__ == "__main__":
    result = build_installer()
    if result:
        print(f"\n[SUCCESS] Installer built: {result}")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)