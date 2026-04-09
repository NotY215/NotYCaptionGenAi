#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v5.2 - PATH FIXED
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

def build_exe():
    print("=" * 60)
    print(f"Building {APP_NAME} Executable v{APP_VERSION}")
    print("=" * 60)
    
    # Get the correct paths
    builder_dir = Path(__file__).parent.absolute()  # Builder folder
    base_dir = builder_dir.parent.absolute()  # Parent folder (NotYCaptionGenAi)
    resources_dir = base_dir / "resources"
    ffmpeg_dir = base_dir / "ffmpeg"
    dist_dir = base_dir / "dist"
    
    print(f"[INFO] Builder directory: {builder_dir}")
    print(f"[INFO] Base directory: {base_dir}")
    
    # Clean previous builds
    if dist_dir.exists():
        print("[INFO] Cleaning previous dist directory...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean PyInstaller cache
    build_cache = builder_dir / "build"
    if build_cache.exists():
        shutil.rmtree(build_cache)
    
    # Source file path - IMPORTANT: Use absolute path
    source_file = base_dir / "noty_caption_gen.py"
    if not source_file.exists():
        print(f"[ERROR] Source file not found: {source_file}")
        print(f"[INFO] Please ensure noty_caption_gen.py is in: {base_dir}")
        return None
    
    source_path = str(source_file)
    icon_path = str(resources_dir / "app.ico") if (resources_dir / "app.ico").exists() else ""
    
    print(f"[INFO] Source: {source_path}")
    print(f"[INFO] Source exists: {source_file.exists()}")
    
    # Collect ffmpeg files
    ffmpeg_datas = []
    if ffmpeg_dir.exists():
        for file in ffmpeg_dir.glob("*"):
            if file.is_file():
                ffmpeg_datas.append((str(file), 'ffmpeg'))
    
    # Create spec file content
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Use absolute path for source
source_path = r'{source_path}'

a = Analysis(
    [source_path],
    pathex=[],
    binaries=[],
    datas={ffmpeg_datas} + ([('{icon_path}', '.')] if '{icon_path}' else []),
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
        'torch.nn',
        'torch.nn.functional',
        'torch.serialization',
        'torch.storage',
        'torch.types',
        'torch.version',
        'torch.autograd',
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
        'tensorflow', 'keras', 'transformers',
        'PyQt5', 'PyQt6', 'wxPython',
        'matplotlib', 'plotly', 'seaborn',
        'scipy', 'pandas', 'sklearn',
        'PIL', 'opencv', 'imageio',
        'jupyter', 'notebook', 'ipython',
        'torch.distributed', 'torch.testing', 'torch.jit', 'torch.onnx',
        'torchvision', 'torchtext', 'numba', 'llvmlite'
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
    icon='{icon_path}' if '{icon_path}' else None,
)
'''
    
    spec_path = builder_dir / f"{APP_NAME}.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
        print(f"[INFO] Spec file created: {spec_path}")
    
    # Change to builder directory
    os.chdir(builder_dir)
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"{APP_NAME}.spec",
        "--distpath", str(dist_dir),
        "--workpath", "build",
        "--noconfirm",
        "--clean",
        "--log-level=INFO"
    ]
    
    print("\n[INFO] Building executable with PyInstaller...")
    print("[INFO] This may take 5-10 minutes...")
    sys.stdout.flush()
    
    try:
        # Run PyInstaller with real-time output
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
        
        process.wait(timeout=1800)
        
        if process.returncode != 0:
            print(f"\n[ERROR] PyInstaller failed with code: {process.returncode}")
            return None
        
        print("\n[SUCCESS] Build completed!")
        
    except subprocess.TimeoutExpired:
        print("\n[ERROR] Build timed out after 30 minutes!")
        return None
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        return None
    
    # Clean up spec file
    try:
        spec_path.unlink(missing_ok=True)
        shutil.rmtree(builder_dir / "build", ignore_errors=True)
    except:
        pass
    
    # Find the executable
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        # Check in subfolder
        possible_path = dist_dir / APP_NAME / f"{APP_NAME}.exe"
        if possible_path.exists():
            shutil.move(str(possible_path), str(exe_file))
            exe_file = dist_dir / f"{APP_NAME}.exe"
    
    if exe_file.exists():
        size = exe_file.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        # Copy necessary folders
        for folder_name in ['models', 'ffmpeg', 'resources']:
            src = base_dir / folder_name
            dst = dist_dir / folder_name
            if src.exists() and not dst.exists():
                try:
                    shutil.copytree(src, dst)
                    print(f"  Copied {folder_name}")
                except Exception as e:
                    print(f"  Warning: Could not copy {folder_name}: {e}")
        
        # Create run script
        run_script = dist_dir / "Run_App.bat"
        with open(run_script, 'w') as f:
            f.write(f'''@echo off
cd /d "%~dp0"
set TORCH_USE_RTLD_GLOBAL=1
set CUDA_VISIBLE_DEVICES=-1
echo Starting NotY Caption Generator AI v{APP_VERSION}...
echo.
"{APP_NAME}.exe"
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
        print("  cd dist")
        print("  Run_App.bat")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)