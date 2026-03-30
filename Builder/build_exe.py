#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v4.4
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_exe():
    print("=" * 60)
    print("Building NotY Caption Generator AI Executable v4.4")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    resources_dir = base_dir / "resources"
    dist_dir = base_dir / "dist"
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    source_path = str(base_dir / "noty_caption_gen.py").replace('\\', '/')
    icon_path = str(resources_dir / "app.ico").replace('\\', '/')
    
    # Create spec file
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('whisper') + collect_data_files('torch') + [(r'{icon_path}', '.')],
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
        'regex'
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
        'torchaudio'
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
    name='NotYCaptionGenAI',
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
    icon=r'{icon_path}'
)
'''
    
    spec_path = builder_dir / "NotYCaptionGenAI.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
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
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    exe_file = dist_dir / "NotYCaptionGenAI.exe"
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