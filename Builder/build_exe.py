#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v4.5
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_VERSION = "4.5"
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
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    # Create version info for Windows with correct format
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
            StringStruct(u'Comments', u'Caption Generator using OpenAI Whisper')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect ffmpeg files
ffmpeg_datas = {ffmpeg_datas}

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('whisper') + collect_data_files('torch') + ffmpeg_datas + [(r'{icon_path}', '.')],
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
        'torch',
        'torch._C',
        'torch.nn',
        'torch.nn.functional',
        'numpy',
        'numpy.core',
        'numpy.lib',
        'colorama',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        'regex',
        'winreg'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'sklearn',
        'pandas',
        'PIL',
        'tensorboard',
        'torchvision',
        'torchaudio',
        'PyQt5',
        'PyQt6'
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
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build"),
        "--noconfirm",
        "--clean"
    ]
    
    try:
        print("Building executable...")
        subprocess.check_call(cmd, timeout=1800)
        print("\n[OK] Build completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        sys.exit(1)
    
    spec_path.unlink(missing_ok=True)
    version_path.unlink(missing_ok=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    exe_file = dist_dir / f"{APP_NAME}.exe"
    if exe_file.exists():
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Executable built: {exe_file} ({size:.2f} MB)")
        
        models_dir = dist_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        source_models = base_dir / "models"
        if source_models.exists():
            for model_file in source_models.glob("*.pt"):
                shutil.copy2(model_file, models_dir / model_file.name)
                print(f"  Copied model: {model_file.name}")
        
        dest_ffmpeg = dist_dir / "ffmpeg"
        if ffmpeg_dir.exists():
            if dest_ffmpeg.exists():
                shutil.rmtree(dest_ffmpeg)
            shutil.copytree(ffmpeg_dir, dest_ffmpeg)
            print("  Copied ffmpeg folder")
        
        dest_resources = dist_dir / "resources"
        if resources_dir.exists():
            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            shutil.copytree(resources_dir, dest_resources)
            print("  Copied resources")
        
        return exe_file
    else:
        print("\n[ERROR] Build failed - executable not found!")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()