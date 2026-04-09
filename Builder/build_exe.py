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

def build_exe():
    print("=" * 60)
    print(f"Building {APP_NAME} Executable v{APP_VERSION}")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    ffmpeg_dir = base_dir / "ffmpeg"
    dist_dir = base_dir / "dist"
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    source_file = base_dir / "noty_caption_gen.py"
    source_path = str(source_file).replace('\\', '/')
    icon_path = str(resources_dir / "app.ico").replace('\\', '/') if (resources_dir / "app.ico").exists() else ""
    
    # Collect ffmpeg files as strings with forward slashes
    ffmpeg_datas = []
    if ffmpeg_dir.exists():
        for file in ffmpeg_dir.glob("*"):
            if file.is_file():
                ffmpeg_datas.append(f"('{str(file).replace('\\', '/')}', 'ffmpeg')")
    
    ffmpeg_datas_str = ", ".join(ffmpeg_datas) if ffmpeg_datas else ""
    
    # Create spec file with proper escaping
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=[{ffmpeg_datas_str}] + ([('{icon_path}', '.')] if '{icon_path}' else []),
    hiddenimports=[
        'whisper', 'whisper.__main__', 'whisper.audio', 'whisper.decoding',
        'whisper.model', 'whisper.tokenizer', 'whisper.utils', 'whisper.normalizers',
        'whisper.transcribe', 'whisper.timing',
        'torch', 'torch._C', 'torch.nn', 'torch.nn.functional', 'torch.serialization',
        'torch.storage', 'torch.types', 'torch.version', 'torch.autograd',
        'numpy', 'numpy.core', 'numpy.lib',
        'colorama', 'argparse', 'webbrowser', 'subprocess', 'threading', 'time',
        'pathlib', 'platform', 'tkinter', 'tkinter.filedialog', 'tkinter.messagebox',
        'ctypes', 'importlib', 'importlib.metadata',
        'packaging', 'packaging.version', 'regex', 'tiktoken', 'tiktoken_ext',
        'tiktoken_ext.openai_public', 'more_itertools',
        'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna',
        'torchaudio', 'torchaudio.functional', 'torchaudio.transforms',
        'yt_dlp', 'yt_dlp.extractor', 'yt_dlp.downloader', 'yt_dlp.postprocessor',
        'sqlite3', 'winreg', 'json', 'hashlib', 'tempfile', 'shutil',
        'enum', 'dataclasses', 'typing', 'datetime', 'urllib', 'urllib.parse',
        'urllib.request', 're', 'io', 'queue'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tensorflow', 'keras', 'transformers', 'PyQt5', 'PyQt6', 'wxPython',
        'matplotlib', 'plotly', 'seaborn', 'scipy', 'pandas', 'sklearn',
        'PIL', 'opencv', 'imageio', 'jupyter', 'notebook', 'ipython',
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
    
    print("\n[INFO] Building... This may take 5-10 minutes.")
    sys.stdout.flush()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode != 0:
            print(f"[ERROR] Build failed!")
            if result.stderr:
                print(result.stderr[:500])
            return None
        print("[SUCCESS] Build completed!")
    except Exception as e:
        print(f"[ERROR] {e}")
        return None
    
    # Cleanup
    spec_path.unlink(missing_ok=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    # Find executable
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if not exe_file.exists():
        possible = dist_dir / APP_NAME / f"{APP_NAME}.exe"
        if possible.exists():
            shutil.move(str(possible), str(exe_file))
    
    if exe_file.exists():
        size = exe_file.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Executable: {exe_file} ({size:.2f} MB)")
        
        # Copy folders
        for folder in ['models', 'ffmpeg', 'resources']:
            src = base_dir / folder
            dst = dist_dir / folder
            if src.exists() and not dst.exists():
                shutil.copytree(src, dst)
                print(f"  Copied {folder}")
        
        return exe_file
    
    return None

if __name__ == "__main__":
    result = build_exe()
    if result:
        print(f"\n[SUCCESS] Build successful!")
    else:
        print("\n[FAILED] Build failed!")
        sys.exit(1)