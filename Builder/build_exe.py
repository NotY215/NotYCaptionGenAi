#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v5.2 - WORKING VERSION
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import site
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"

def get_python_paths():
    """Get all Python paths"""
    paths = []
    
    # Get site-packages
    for path in site.getsitepackages():
        if os.path.exists(path):
            paths.append(path)
    
    # Get user site-packages
    user_site = site.getusersitepackages()
    if os.path.exists(user_site):
        paths.append(user_site)
    
    # Get venv site-packages
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        venv_site = os.path.join(venv_path, 'Lib', 'site-packages')
        if os.path.exists(venv_site):
            paths.append(venv_site)
    
    return paths

def build_exe():
    print("=" * 70)
    print(f"Building {APP_NAME} Executable v{APP_VERSION}")
    print("=" * 70)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    ffmpeg_dir = base_dir / "ffmpeg"
    dist_dir = base_dir / "dist"
    
    # Clean previous builds
    if dist_dir.exists():
        print("\n[1/4] Cleaning previous builds...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Get Python paths
    python_paths = get_python_paths()
    print(f"\n[2/4] Found Python paths:")
    for p in python_paths:
        print(f"    - {p}")
    
    # Find torch and whisper
    torch_path = None
    whisper_path = None
    
    for path in python_paths:
        torch_check = Path(path) / "torch"
        whisper_check = Path(path) / "whisper"
        if torch_check.exists():
            torch_path = str(torch_check)
        if whisper_check.exists():
            whisper_path = str(whisper_check)
    
    if not torch_path:
        print("\n[ERROR] torch not found! Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchaudio"], check=True)
        for path in python_paths:
            torch_check = Path(path) / "torch"
            if torch_check.exists():
                torch_path = str(torch_check)
                break
    
    if not whisper_path:
        print("\n[ERROR] whisper not found! Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper"], check=True)
        for path in python_paths:
            whisper_check = Path(path) / "whisper"
            if whisper_check.exists():
                whisper_path = str(whisper_check)
                break
    
    print(f"\n[3/4] Found torch at: {torch_path}")
    print(f"    Found whisper at: {whisper_path}")
    
    # Collect all data files
    datas = []
    
    # Add torch
    if torch_path:
        for root, dirs, files in os.walk(torch_path):
            for file in files:
                if file.endswith(('.dll', '.pyd', '.so', '.py')):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, os.path.dirname(torch_path))
                    datas.append((full_path, rel_path))
    
    # Add whisper
    if whisper_path:
        for root, dirs, files in os.walk(whisper_path):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, os.path.dirname(whisper_path))
                    datas.append((full_path, rel_path))
    
    # Add ffmpeg
    if ffmpeg_dir.exists():
        for file in ffmpeg_dir.glob("*"):
            if file.is_file():
                datas.append((str(file), 'ffmpeg'))
    
    # Add icon
    icon_path = resources_dir / "app.ico"
    if icon_path.exists():
        datas.append((str(icon_path), '.'))
    
    # Create the spec file
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# All collected data files
datas = {datas}

a = Analysis(
    ['{base_dir / "noty_caption_gen.py"}'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'whisper',
        'whisper._cli',
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
        'torch.autograd',
        'torch.autograd.function',
        'torch.cuda',
        'torch.cuda.amp',
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
        'requests.api',
        'requests.models',
        'requests.sessions',
        'requests.adapters',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'torchaudio',
        'torchaudio.functional',
        'torchaudio.transforms',
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.extractor.youtube',
        'yt_dlp.downloader',
        'yt_dlp.downloader.http',
        'yt_dlp.downloader.hls',
        'yt_dlp.postprocessor',
        'yt_dlp.utils',
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
        'queue',
        'logging',
        'warnings',
        'abc',
        'weakref',
        'copy',
        'math',
        'random',
        'string',
        'socket',
        'ssl',
        'hashlib',
        'hmac',
        'secrets'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tensorflow',
        'keras',
        'matplotlib',
        'scipy',
        'pandas',
        'sklearn',
        'PIL',
        'cv2',
        'PyQt5',
        'PyQt6',
        'wxPython'
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    a.zipfiles,
    a.zipped_data,
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
    icon='{icon_path}' if {icon_path.exists()} else None,
    version='version_info.txt'
)

# COLLECT all files
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    a.zipfiles,
    a.zipped_data,
    a.scripts,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='{APP_NAME}'
)
'''
    
    # Write spec file
    spec_path = builder_dir / f"{APP_NAME}.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    # Create version info
    version_info = f'''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({APP_VERSION.replace('.', ',')}, 0),
    prodvers=({APP_VERSION.replace('.', ',')}, 0),
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
            StringStruct(u'LegalCopyright', u'Copyright (c) 2026 {APP_AUTHOR}'),
            StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
            StringStruct(u'ProductName', u'{APP_NAME}'),
            StringStruct(u'ProductVersion', u'{APP_VERSION}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    version_path = builder_dir / "version_info.txt"
    with open(version_path, 'w') as f:
        f.write(version_info)
    
    print("\n[4/4] Running PyInstaller...")
    print("This will take 15-20 minutes...")
    sys.stdout.flush()
    
    # Run PyInstaller
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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode != 0:
            print("\n[ERROR] PyInstaller failed!")
            print(result.stderr)
            return None
        
        print("\n[SUCCESS] Build completed!")
        
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Build timed out!")
        return None
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return None
    
    # Cleanup
    spec_path.unlink(missing_ok=True)
    version_path.unlink(missing_ok=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    # Check if executable was created
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        exe_file = dist_dir / APP_NAME / f"{APP_NAME}.exe"
    
    if exe_file.exists():
        size = exe_file.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Executable: {exe_file} ({size:.2f} MB)")
        
        # Copy necessary folders
        for folder in ['models', 'ffmpeg', 'resources']:
            src = base_dir / folder
            dst = dist_dir / folder
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"  Copied {folder}")
        
        # Create run script
        run_script = dist_dir / "run.bat"
        with open(run_script, 'w') as f:
            f.write(f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
"{exe_file.name}" %*
pause
''')
        
        return exe_file
    
    print("\n[ERROR] Executable not found!")
    return None

if __name__ == "__main__":
    result = build_exe()
    if result:
        print(f"\n[SUCCESS] Build successful! Run: {result}")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)