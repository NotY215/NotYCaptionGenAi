#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v5.2 - OPTIMIZED
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
    
    # Clean previous builds
    if dist_dir.exists():
        print("[INFO] Cleaning previous dist directory...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean build cache
    build_cache = builder_dir / "build"
    if build_cache.exists():
        shutil.rmtree(build_cache)
    
    source_path = str(base_dir / "noty_caption_gen.py").replace('\\', '/')
    icon_path = str(resources_dir / "app.ico").replace('\\', '/')
    
    # Collect ffmpeg files
    ffmpeg_datas = []
    if ffmpeg_dir.exists():
        for file in ffmpeg_dir.glob("*"):
            if file.is_file():
                ffmpeg_datas.append((str(file).replace('\\', '/'), 'ffmpeg'))
    
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
    
    # Optimized spec file for faster build
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# FFmpeg data
ffmpeg_datas = {ffmpeg_datas}

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('whisper') + ffmpeg_datas + [(r'{icon_path}', '.')],
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
        'torch.nn',
        'torch.nn.functional',
        'torch.serialization',
        'torch.storage',
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.core.fromnumeric',
        'numpy.core.umath',
        'numpy.lib',
        'numpy.lib.format',
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
        'PyQt5', 'PyQt6', 'wxPython',
        'matplotlib', 'plotly', 'seaborn',
        'scipy', 'pandas', 'sklearn',
        'PIL', 'opencv', 'imageio',
        'jupyter', 'notebook', 'ipython',
        'torch.distributed', 'torch.testing', 'torch.jit', 'torch.onnx',
        'torchvision', 'torchtext',
        'numpy.random', 'numpy.ma', 'numpy.fft',
        'numpy.linalg', 'numpy.polynomial'
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
    upx=True,
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
    
    # Fast build command - using UPX compression
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build"),
        "--noconfirm",
        "--clean",
        "--log-level=WARN"
    ]
    
    try:
        print("\n[INFO] Building executable...")
        print("[INFO] Using optimized settings for faster build...")
        print("[INFO] This may take 5-10 minutes...")
        sys.stdout.flush()
        
        # Run with minimal output for speed
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode != 0:
            print("\n[ERROR] PyInstaller failed!")
            if result.stderr:
                print(result.stderr[:500])
            return None
            
        print("\n[OK] Build completed successfully!")
        
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Build timed out after 30 minutes!")
        return None
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        return None
    
    # Clean up spec and version files
    spec_path.unlink(missing_ok=True)
    version_path.unlink(missing_ok=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    # Find the executable
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        # Check in subfolder
        possible_path = dist_dir / APP_NAME / f"{APP_NAME}.exe"
        if possible_path.exists():
            shutil.move(str(possible_path), str(dist_dir / f"{APP_NAME}.exe"))
            exe_file = dist_dir / f"{APP_NAME}.exe"
    
    if exe_file.exists():
        size = exe_file.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        # Copy ffmpeg folder
        dest_ffmpeg = dist_dir / "ffmpeg"
        if ffmpeg_dir.exists():
            if dest_ffmpeg.exists():
                shutil.rmtree(dest_ffmpeg)
            shutil.copytree(ffmpeg_dir, dest_ffmpeg)
            print("  Copied ffmpeg folder")
        
        # Copy resources
        dest_resources = dist_dir / "resources"
        if resources_dir.exists():
            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            shutil.copytree(resources_dir, dest_resources)
            print("  Copied resources")
        
        # Create run script
        run_script = dist_dir / "Run_App.bat"
        with open(run_script, 'w') as f:
            f.write(f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
title {APP_NAME} v{APP_VERSION}
echo ============================================================
echo {APP_NAME} v{APP_VERSION}
echo Copyright (c) 2026 {APP_AUTHOR}
echo ============================================================
echo.
echo Starting application...
echo.
"{exe_file.name}"
pause
''')
        print("  Created Run_App.bat")
        
        # Create models folder (empty, for user to add models)
        models_dir = dist_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Create README for models
        readme = models_dir / "README.txt"
        with open(readme, 'w') as f:
            f.write('''Place Whisper model files here (.pt files)

Models will be downloaded automatically when first used.
Or download manually from:
https://github.com/openai/whisper

Available models:
- tiny.pt (75 MB)
- base.pt (150 MB)  
- small.pt (500 MB)
- medium.pt (1.5 GB)
- large.pt (2.9 GB)
''')
        
        return exe_file
    
    print("\n[ERROR] Executable not found!")
    return None

if __name__ == "__main__":
    result = build_exe()
    if result:
        print(f"\n[SUCCESS] Build successful! Run: {result}")
        print("\nNext steps:")
        print("1. Run 'python build_installer.py' to create installers")
        print("2. Or use the portable version in 'dist' folder")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)