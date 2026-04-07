#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v5.2 - FIXED
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"
APP_COPYRIGHT = f"Copyright (c) 2026 {APP_AUTHOR}"

def build_exe():
    print("=" * 60)
    print(f"Building {APP_NAME} Executable v{APP_VERSION}")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    ffmpeg_dir = base_dir / "ffmpeg"
    dist_dir = base_dir / "dist"
    
    # Kill any existing Python/PyInstaller processes that might hold file locks
    print("[INFO] Cleaning up any lingering processes...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # Clean previous builds with retry
    if dist_dir.exists():
        print("[INFO] Cleaning previous dist directory...")
        for attempt in range(3):
            try:
                shutil.rmtree(dist_dir)
                break
            except PermissionError:
                print(f"[WARNING] Permission denied, retrying in 2 seconds... (attempt {attempt+1}/3)")
                time.sleep(2)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean PyInstaller cache
    build_cache = builder_dir / "build"
    if build_cache.exists():
        for attempt in range(3):
            try:
                shutil.rmtree(build_cache)
                break
            except PermissionError:
                time.sleep(1)
    
    source_path = str(base_dir / "noty_caption_gen.py").replace('\\', '/')
    icon_path = str(resources_dir / "app.ico").replace('\\', '/')
    
    # Collect ffmpeg files
    ffmpeg_datas = []
    if ffmpeg_dir.exists():
        for file in ffmpeg_dir.glob("*"):
            if file.is_file():
                ffmpeg_datas.append((str(file), 'ffmpeg'))
    
    # Parse version numbers
    version_parts = [int(x) for x in APP_VERSION.split('.')]
    while len(version_parts) < 4:
        version_parts.append(0)
    
    # Create version info for Windows
    version_info = f'''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    prodvers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'{APP_AUTHOR}'),
            StringStruct(u'FileDescription', u'{APP_NAME}'),
            StringStruct(u'FileVersion', u'{APP_VERSION}'),
            StringStruct(u'InternalName', u'{APP_NAME}'),
            StringStruct(u'LegalCopyright', u'{APP_COPYRIGHT}'),
            StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
            StringStruct(u'ProductName', u'{APP_NAME}'),
            StringStruct(u'ProductVersion', u'{APP_VERSION}'),
            StringStruct(u'Comments', u'AI-Powered Subtitle & Lyrics Generator with YouTube Support')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    # Simplified spec file without COLLECT to avoid permission issues
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect whisper data
whisper_datas = collect_data_files('whisper')

# FFmpeg data
ffmpeg_datas = {ffmpeg_datas}

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=whisper_datas + ffmpeg_datas + [(r'{icon_path}', '.')],
    hiddenimports=[
        'whisper',
        'whisper.__main__',
        'whisper.audio',
        'whisper.decoding',
        'whisper.model',
        'whisper.tokenizer',
        'whisper.utils',
        'whisper.normalizers',
        'whisper.transcribe',
        'whisper.timing',
        'torch',
        'torch._C',
        'torch._ops',
        'torch._utils',
        'torch.nn',
        'torch.nn.functional',
        'torch.serialization',
        'torch.storage',
        'torch.types',
        'torch.version',
        'numpy',
        'numpy.core',
        'numpy.lib',
        'colorama',
        'argparse',
        'webbrowser',
        'subprocess',
        'threading',
        'time',
        'pathlib',
        'platform',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'ctypes',
        'importlib',
        'importlib.metadata',
        'packaging',
        'packaging.version',
        'regex',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        'more_itertools',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'torchaudio',
        'torchaudio.functional',
        'torchaudio.transforms',
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        'yt_dlp.postprocessor',
        'sqlite3',
        'winreg',
        'json',
        'hashlib',
        'tempfile',
        'shutil',
        'enum',
        'dataclasses',
        'typing',
        'datetime',
        'urllib',
        'urllib.parse',
        'urllib.request',
        're',
        'io',
        'queue'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tensorflow', 'keras', 'transformers', 'datasets',
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wxPython',
        'matplotlib', 'plotly', 'seaborn', 'bokeh',
        'scipy', 'pandas', 'sklearn', 'statsmodels',
        'PIL', 'opencv', 'imageio',
        'jupyter', 'notebook', 'ipython',
        'numba', 'llvmlite',
        'setuptools', 'pkg_resources',
        'torchvision', 'torchtext',
        'torch.distributed',
        'torch.testing',
        'torch.jit',
        'torch.onnx'
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='{APP_NAME}',
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
    icon=r'{icon_path}',
    version='version_info.txt'
)
'''
    
    spec_path = builder_dir / f"{APP_NAME}.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    # Write version info
    version_path = builder_dir / "version_info.txt"
    with open(version_path, 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    # Install/update required packages
    print("\n[INFO] Ensuring required packages are installed...")
    packages = ['pyinstaller', 'openai-whisper', 'torch', 'torchaudio', 'numpy', 'yt-dlp']
    for package in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], 
                      capture_output=True)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build"),
        "--noconfirm",
        "--clean",
        "--log-level=INFO"
    ]
    
    try:
        print("\n[INFO] Building executable...")
        print("[INFO] This may take 10-15 minutes...")
        subprocess.check_call(cmd, timeout=5400)
        print("\n[OK] Build completed successfully!")
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Build timed out!")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[WARNING] Build interrupted!")
        sys.exit(1)
    
    # Clean up spec and version files
    try:
        spec_path.unlink(missing_ok=True)
        version_path.unlink(missing_ok=True)
        shutil.rmtree(builder_dir / "build", ignore_errors=True)
    except:
        pass
    
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if exe_file.exists():
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        # Create directories
        models_dir = dist_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Copy models if they exist
        source_models = base_dir / "models"
        if source_models.exists():
            for model_file in source_models.glob("*.pt"):
                shutil.copy2(model_file, models_dir / model_file.name)
                print(f"  Copied model: {model_file.name}")
        
        # Copy ffmpeg folder
        dest_ffmpeg = dist_dir / "ffmpeg"
        if ffmpeg_dir.exists():
            if dest_ffmpeg.exists():
                try:
                    shutil.rmtree(dest_ffmpeg)
                except:
                    pass
            shutil.copytree(ffmpeg_dir, dest_ffmpeg)
            print("  Copied ffmpeg folder")
        
        # Copy resources
        dest_resources = dist_dir / "resources"
        if resources_dir.exists():
            if dest_resources.exists():
                try:
                    shutil.rmtree(dest_resources)
                except:
                    pass
            shutil.copytree(resources_dir, dest_resources)
            print("  Copied resources")
        
        # Create a batch file to run the app with proper environment
        batch_content = f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
"{exe_file.name}" %*
'''
        batch_path = dist_dir / "run_app.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        print(f"  Created run script: run_app.bat")
        
        return exe_file
    else:
        print("\n[ERROR] Build failed - executable not found!")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()