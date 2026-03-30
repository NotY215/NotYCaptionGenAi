#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build NotY Caption Generator AI Executable v4.4
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
    
    # Clean
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Create spec file with proper path escaping
    source_path = str(base_dir / "noty_caption_gen.py").replace('\\', '/')
    icon_path = str(resources_dir / "app.ico").replace('\\', '/')
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=[
        (r'{icon_path}', '.'),
    ],
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
        'numpy',
        'colorama',
        'argparse',
        'webbrowser',
        'subprocess',
        'threading',
        'time',
        'pathlib',
        'platform'
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
        'torch.utils',
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
        'scipy',
        'numba',
        'llvmlite',
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
    upx=False,
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
    
    # Build
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build"),
        "--noconfirm"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\n✅ Build completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)
    
    # Clean up
    spec_path.unlink(missing_ok=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    exe_file = dist_dir / "NotYCaptionGenAI.exe"
    if exe_file.exists():
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n✅ Executable built: {exe_file} ({size:.2f} MB)")
        return exe_file
    else:
        # Try to find in other locations
        alt_exe = dist_dir / "NotYCaptionGenAI" / "NotYCaptionGenAI.exe"
        if alt_exe.exists():
            shutil.copy2(alt_exe, dist_dir / "NotYCaptionGenAI.exe")
            size = alt_exe.stat().st_size / 1024 / 1024
            print(f"\n✅ Executable built: {dist_dir / 'NotYCaptionGenAI.exe'} ({size:.2f} MB)")
            return dist_dir / "NotYCaptionGenAI.exe"
        
        print("\n❌ Build failed - executable not found!")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()