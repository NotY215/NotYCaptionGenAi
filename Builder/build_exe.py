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
    
    # Clean
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Create spec file with minimal PyTorch
    source_path = str(base_dir / "noty_caption_gen.py").replace('\\', '/')
    icon_path = str(resources_dir / "app.ico").replace('\\', '/')
    
    # Minimal PyTorch spec file
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Only collect essential PyTorch components
torch_datas = []
try:
    # Only collect essential torch data
    import torch
    torch_path = os.path.dirname(torch.__file__)
    
    # Add torch/lib directory
    lib_dir = os.path.join(torch_path, 'lib')
    if os.path.exists(lib_dir):
        for file in os.listdir(lib_dir):
            if file.endswith('.dll'):
                torch_datas.append((os.path.join(lib_dir, file), 'torch/lib'))
except:
    pass

# Collect whisper data files
whisper_datas = []
try:
    whisper_datas = collect_data_files('whisper')
except:
    pass

a = Analysis(
    [r'{source_path}'],
    pathex=[],
    binaries=[],
    datas=torch_datas + whisper_datas + [
        (r'{icon_path}', '.'),
    ],
    hiddenimports=[
        # Core whisper
        'whisper',
        'whisper.__main__',
        'whisper.audio',
        'whisper.decoding',
        'whisper.model',
        'whisper.tokenizer',
        'whisper.utils',
        'whisper.normalizers',
        
        # Minimal PyTorch - ONLY what's needed for inference
        'torch',
        'torch._C',
        'torch._ops',
        'torch._utils',
        'torch.nn',
        'torch.nn.functional',
        'torch.serialization',
        'torch.storage',
        'torch.types',
        
        # Numpy (required)
        'numpy',
        'numpy.core',
        'numpy.core._methods',
        'numpy.core.fromnumeric',
        'numpy.core.umath',
        'numpy.lib',
        'numpy.lib.format',
        
        # Other dependencies
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
        'ctypes',
        'importlib',
        'importlib.metadata',
        'packaging',
        'packaging.version',
        'regex',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'more_itertools',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # Exclude everything CUDA/GPU related
        'torch.cuda',
        'torch.cuda.amp',
        'torch.cuda._utils',
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
        'torch.utils.checkpoint',
        'torch.utils.cpp_extension',
        'torch.utils.data',
        'torch.utils.dlpack',
        'torch.utils.hooks',
        'torch.utils.model_zoo',
        'torch.utils.tensorboard',
        
        # Exclude numpy heavy modules
        'numpy.random',
        'numpy.ma',
        'numpy.fft',
        'numpy.linalg',
        'numpy.polynomial',
        'numpy.testing',
        'numpy.distutils',
        
        # Exclude other large packages
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
        'torchaudio',
        'torchvision',
        'torchtext'
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
    
    # Build with UPX compression disabled for faster builds
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build"),
        "--noconfirm",
        "--clean",
        "--log-level=INFO"
    ]
    
    try:
        print("Building executable (this will take 2-5 minutes)...")
        print("Please wait, DO NOT interrupt...")
        subprocess.check_call(cmd, timeout=1800)  # 30 minutes timeout
        print("\n✅ Build completed successfully!")
    except subprocess.TimeoutExpired:
        print("\n❌ Build timed out after 30 minutes!")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Build interrupted by user!")
        sys.exit(1)
    
    # Clean up
    spec_path.unlink(missing_ok=True)
    
    exe_file = dist_dir / "NotYCaptionGenAI.exe"
    if exe_file.exists():
        size = exe_file.stat().st_size / 1024 / 1024
        print(f"\n✅ Executable built: {exe_file} ({size:.2f} MB)")
        
        # Create models directory in dist
        models_dir = dist_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Copy models if they exist
        source_models = base_dir / "models"
        if source_models.exists():
            for model_file in source_models.glob("*.pt"):
                shutil.copy2(model_file, models_dir / model_file.name)
                print(f"  Copied model: {model_file.name}")
        
        # Copy resources
        dest_resources = dist_dir / "resources"
        if resources_dir.exists():
            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            shutil.copytree(resources_dir, dest_resources)
            print("  Copied resources")
        
        print(f"\n✅ Executable is ready: {exe_file}")
        print(f"📁 Models directory: {models_dir}")
        print(f"📁 Resources directory: {dest_resources}")
        return exe_file
    else:
        print("\n❌ Build failed - executable not found!")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()