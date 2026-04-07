#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v5.2
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
    
    # Kill any python processes that might lock files
    print("[INFO] Cleaning up processes...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], capture_output=True)
        import time
        time.sleep(2)
    except:
        pass
    
    if dist_dir.exists():
        print("[INFO] Cleaning previous dist directory...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean PyInstaller cache
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
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all necessary data files
whisper_datas = collect_data_files('whisper')
torch_datas = collect_data_files('torch')
torchaudio_datas = collect_data_files('torchaudio')
numpy_datas = collect_data_files('numpy')
ytdl_datas = collect_data_files('yt_dlp')

# FFmpeg data
ffmpeg_datas = {ffmpeg_datas}

# Combine all datas
all_datas = whisper_datas + torch_datas + torchaudio_datas + numpy_datas + ytdl_datas + ffmpeg_datas

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=all_datas + [(r'{icon_path}', '.')],
    hiddenimports=[
        # Whisper and submodules
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
        
        # PyTorch core
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
        'torch.autograd',
        'torch.autograd.function',
        
        # NumPy
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.core.fromnumeric',
        'numpy.core.umath',
        'numpy.core.multiarray',
        'numpy.core.numeric',
        'numpy.core.numerictypes',
        'numpy.lib',
        'numpy.lib.format',
        'numpy.random',
        
        # CLI & UI
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
        'importlib.resources',
        
        # Text processing
        'packaging',
        'packaging.version',
        'packaging.specifiers',
        'regex',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        'more_itertools',
        
        # HTTP requests
        'requests',
        'requests.api',
        'requests.models',
        'requests.sessions',
        'requests.adapters',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        
        # Audio processing
        'torchaudio',
        'torchaudio.functional',
        'torchaudio.transforms',
        
        # YouTube download
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.extractor.youtube',
        'yt_dlp.downloader',
        'yt_dlp.downloader.http',
        'yt_dlp.downloader.hls',
        'yt_dlp.postprocessor',
        'yt_dlp.utils',
        
        # Database
        'sqlite3',
        
        # Windows registry
        'winreg',
        
        # Additional modules
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
        'queue',
        'logging',
        'warnings'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tensorflow', 'keras', 'transformers',
        'PyQt5', 'PyQt6', 'wxPython',
        'matplotlib', 'plotly', 'seaborn',
        'scipy', 'pandas', 'sklearn',
        'PIL', 'opencv', 'imageio',
        'jupyter', 'notebook', 'ipython',
        'torch.distributed',
        'torch.testing',
        'torch.jit',
        'torch.onnx',
        'torchvision', 'torchtext'
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
    
    # Ensure all required packages are installed
    print("\n[INFO] Ensuring required packages are installed...")
    packages = ['openai-whisper', 'torch', 'torchaudio', 'numpy', 'yt-dlp', 'pyinstaller']
    for package in packages:
        print(f"  Installing/upgrading {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], 
                      capture_output=True)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build"),
        "--noconfirm",
        "--clean"
    ]
    
    try:
        print("\n[INFO] Building executable with PyInstaller...")
        print("[INFO] This may take 15-20 minutes...")
        print("[INFO] The build is working, please wait...")
        sys.stdout.flush()
        
        # Run PyInstaller with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(f"  {line.rstrip()}")
            sys.stdout.flush()
        
        # Wait for completion
        return_code = process.wait(timeout=5400)
        
        if return_code != 0:
            print(f"\n[ERROR] PyInstaller failed with code: {return_code}")
            return None
            
        print("\n[OK] Build completed successfully!")
        
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Build timed out after 90 minutes!")
        return None
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        return None
    
    # Clean up spec and version files
    spec_path.unlink(missing_ok=True)
    version_path.unlink(missing_ok=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if exe_file.exists():
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        # Create necessary directories
        models_dir = dist_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Copy models if they exist
        source_models = base_dir / "models"
        if source_models.exists():
            print("[INFO] Copying models...")
            for model_file in source_models.glob("*.pt"):
                shutil.copy2(model_file, models_dir / model_file.name)
                print(f"  Copied: {model_file.name}")
        
        # Copy ffmpeg
        dest_ffmpeg = dist_dir / "ffmpeg"
        if ffmpeg_dir.exists():
            print("[INFO] Copying ffmpeg...")
            if dest_ffmpeg.exists():
                shutil.rmtree(dest_ffmpeg)
            shutil.copytree(ffmpeg_dir, dest_ffmpeg)
            print("  Copied ffmpeg folder")
        
        # Copy resources
        dest_resources = dist_dir / "resources"
        if resources_dir.exists():
            print("[INFO] Copying resources...")
            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            shutil.copytree(resources_dir, dest_resources)
            print("  Copied resources")
        
        # Create run script
        batch_content = f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
start "" "{exe_file.name}" %*
'''
        batch_path = dist_dir / "run_app.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        print("  Created run_app.bat")
        
        return exe_file
    else:
        print("\n[ERROR] Build failed - executable not found!")
        return None

if __name__ == "__main__":
    result = build_exe()
    if result:
        print(f"\n[SUCCESS] Build completed! Executable at: {result}")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)