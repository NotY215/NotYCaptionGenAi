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
    
    # Convert paths to use forward slashes for the spec file
    source_path = str(base_dir / "noty_caption_gen.py").replace('\\', '/')
    icon_path = str(resources_dir / "app.ico").replace('\\', '/')
    
    # Collect ffmpeg files as strings with forward slashes
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
            StringStruct(u'LegalCopyright', u'Copyright (c) 2026 {APP_AUTHOR}'),
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
    
    # Create the spec file with properly escaped paths
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# FFmpeg data
ffmpeg_datas = {ffmpeg_datas}

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=ffmpeg_datas + [(r'{icon_path}', '.')],
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
        'torch.autograd',
        'torch.autograd.function',
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
        'torch.distributed', 'torch.testing', 'torch.jit', 'torch.onnx',
        'torchvision', 'torchtext'
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
    icon=r'{icon_path}',
    version='version_info.txt'
)

app = EXE(
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
    icon=r'{icon_path}',
    version='version_info.txt'
)
'''
    
    spec_path = builder_dir / f"{APP_NAME}.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
        print(f"\n[INFO] Spec file created: {spec_path}")
    
    # Write version info
    version_path = builder_dir / "version_info.txt"
    with open(version_path, 'w', encoding='utf-8') as f:
        f.write(version_info)
        print(f"[INFO] Version file created: {version_path}")
    
    print("\n[4/4] Running PyInstaller...")
    print("This will take 15-20 minutes...")
    sys.stdout.flush()
    
    # Change to builder directory
    os.chdir(builder_dir)
    
    # Run PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"{APP_NAME}.spec",
        "--distpath", str(dist_dir).replace('\\', '/'),
        "--workpath", "build",
        "--noconfirm",
        "--clean"
    ]
    
    try:
        # Run with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            print(f"  {line.rstrip()}")
            sys.stdout.flush()
        
        process.wait(timeout=3600)
        
        if process.returncode != 0:
            print("\n[ERROR] PyInstaller failed!")
            return None
        
        print("\n[SUCCESS] Build completed!")
        
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Build timed out!")
        return None
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return None
    
    # Cleanup
    try:
        spec_path.unlink(missing_ok=True)
        version_path.unlink(missing_ok=True)
        shutil.rmtree(builder_dir / "build", ignore_errors=True)
    except:
        pass
    
    # Find the executable
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        # Check in subfolder
        possible_path = dist_dir / APP_NAME / f"{APP_NAME}.exe"
        if possible_path.exists():
            exe_file = possible_path
            # Move it up
            shutil.move(str(possible_path), str(dist_dir / f"{APP_NAME}.exe"))
            exe_file = dist_dir / f"{APP_NAME}.exe"
    
    if exe_file.exists():
        size = exe_file.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        # Copy necessary folders
        for folder_name in ['models', 'ffmpeg', 'resources']:
            src = base_dir / folder_name
            dst = dist_dir / folder_name
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"  Copied {folder_name}")
        
        # Create run script
        run_script = dist_dir / "Run_App.bat"
        with open(run_script, 'w') as f:
            f.write(f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
echo Starting NotY Caption Generator AI v{APP_VERSION}...
echo.
"{exe_file.name}"
pause
''')
        print(f"  Created Run_App.bat")
        
        return exe_file
    
    print("\n[ERROR] Executable not found!")
    return None

if __name__ == "__main__":
    result = build_exe()
    if result:
        print(f"\n[SUCCESS] Build successful! Run: {result}")
        print("\nYou can now run the app using:")
        print(f"  cd dist")
        print(f"  Run_App.bat")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)