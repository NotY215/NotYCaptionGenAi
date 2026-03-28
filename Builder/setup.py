#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for building NotY Caption Generator AI v4.3
Copyright (c) 2026 NotY215
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_all():
    print("=" * 60)
    print("Building NotY Caption Generator AI v4.3")
    print("Copyright (c) 2026 NotY215")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    temp_dir = base_dir / "temp_build"
    
    # Clean
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    dist_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy main script
    print("\n[1/2] Preparing files...")
    shutil.copy2(base_dir / "noty_caption_gen.py", temp_dir / "noty_caption_gen.py")
    
    # Copy icon if exists
    resources_dir = base_dir / "resources"
    icon_path = resources_dir / "app.ico"
    if icon_path.exists():
        shutil.copy2(icon_path, temp_dir / "app.ico")
    
    # Build with PyInstaller with optimized settings
    print("\n[2/2] Building executable...")
    
    # Create spec file for better control
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{temp_dir / "noty_caption_gen.py"}'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'whisper',
        'whisper.__main__',
        'whisper.audio',
        'whisper.decoding',
        'whisper.model',
        'whisper.tokenizer',
        'whisper.utils',
        'whisper.normalizers',
        'torch',
        'torch.nn',
        'torch.nn.functional',
        'torch.utils.data',
        'numpy',
        'colorama',
        'argparse',
        'webbrowser',
        'subprocess',
        'threading',
        'time',
        'pathlib'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'torch.distributed',
        'torch.testing',
        'torch.jit',
        'torch.onnx',
        'torch.ao',
        'torch.fx',
        'torch._dynamo',
        'torch._inductor',
        'torch._export',
        'torch._functorch',
        'torch._lazy',
        'torch._numpy',
        'torch._prims',
        'torch._subclasses',
        'torch._tensor',
        'torch.backends',
        'torch.contrib',
        'torch.cuda',
        'torch.distributions',
        'torch.fft',
        'torch.futures',
        'torch.linalg',
        'torch.mps',
        'torch.optim',
        'torch.package',
        'torch.profiler',
        'torch.quantization',
        'torch.special',
        'torch.sparse',
        'torch.utils.benchmark',
        'torch.utils.model_dump',
        'torch.utils.tensorboard',
        'torch.utils.viz',
        'numpy.random',
        'numpy.ma',
        'numpy.fft',
        'numpy.linalg',
        'numpy.polynomial',
        'numpy.testing',
        'numpy.distutils',
        'setuptools',
        'pkg_resources',
        'jinja2',
        'markupsafe',
        'tensorboard',
        'tqdm',
        'matplotlib',
        'PIL',
        'sklearn',
        'scipy'
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
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{temp_dir / "app.ico" if icon_path.exists() else ""}'
)
'''
    
    spec_path = builder_dir / "NotYCaptionGenAI.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    # Build with spec file
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build"),
        "--noconfirm"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n[OK] Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed: {e}")
        sys.exit(1)
    
    # Clean up
    spec_path.unlink(missing_ok=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    # Show result
    exe_file = dist_dir / "NotYCaptionGenAI.exe"
    if exe_file.exists():
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n[OK] Executable created: {exe_file}")
        print(f"    Size: {size:.2f} MB")
    else:
        print("\n[ERROR] Executable not found!")
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)

if __name__ == "__main__":
    build_all()