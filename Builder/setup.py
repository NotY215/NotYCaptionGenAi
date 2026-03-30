#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for building NotY Caption Generator AI v4.4
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_all():
    print("=" * 60)
    print("Building NotY Caption Generator AI v4.4")
    print("Copyright (c) 2026 NotY215")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.parent
    builder_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Clean
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Build main executable (simplified)
    print("\n[1/3] Building main executable...")
    
    # Create a simplified spec file for main executable
    source_path = str(base_dir / "noty_caption_gen.py").replace('\\', '/')
    icon_path = str(base_dir / "resources" / "app.ico").replace('\\', '/')
    
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
        'torch._C',
        'numpy',
        'colorama',
        'argparse',
        'webbrowser',
        'subprocess',
        'threading',
        'time',
        'pathlib',
        'platform',
        'tkinter'
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
        'llvmlite'
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
    
    # Build main executable
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(dist_dir),
        "--workpath", str(builder_dir / "build"),
        "--noconfirm"
    ]
    
    try:
        subprocess.run(cmd, check=True, timeout=600)
        print("\n✅ Main executable built successfully!")
    except subprocess.TimeoutExpired:
        print("\n⚠️ Build timed out, but may have completed. Checking...")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)
    
    main_exe = dist_dir / "NotYCaptionGenAI.exe"
    if not main_exe.exists():
        print("\n❌ Main executable not found!")
        sys.exit(1)
    
    print(f"✅ Main executable: {main_exe} ({main_exe.stat().st_size / 1024 / 1024:.2f} MB)")
    
    # Step 2: Build uninstaller executable
    print("\n[2/3] Building uninstaller executable...")
    
    uninstaller_py = str(builder_dir / "uninstaller.py")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI_Uninstaller",
        "--onefile",
        "--console",
        "--noconfirm",
        uninstaller_py
    ]
    
    temp_build_dir = base_dir / "temp_build"
    if temp_build_dir.exists():
        shutil.rmtree(temp_build_dir)
    temp_build_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        subprocess.run(cmd, cwd=str(temp_build_dir), check=True, timeout=120)
        uninstaller_exe = temp_build_dir / "dist" / "NotYCaptionGenAI_Uninstaller.exe"
        if uninstaller_exe.exists():
            print(f"✅ Uninstaller built: {uninstaller_exe} ({uninstaller_exe.stat().st_size / 1024 / 1024:.2f} MB)")
        else:
            print("❌ Uninstaller not found!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to build uninstaller: {e}")
        sys.exit(1)
    
    # Step 3: Build installer
    print("\n[3/3] Building installer...")
    
    # Create temp directory for installer files
    temp_dir = base_dir / "temp_installer"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executables
    shutil.copy2(main_exe, temp_dir / "NotYCaptionGenAI.exe")
    shutil.copy2(uninstaller_exe, temp_dir / "NotYCaptionGenAI_Uninstaller.exe")
    
    # Copy resources
    resources_dir = base_dir / "resources"
    if resources_dir.exists():
        shutil.copytree(resources_dir, temp_dir / "resources")
    
    # Copy models if they exist
    models_dir = base_dir / "models"
    if models_dir.exists() and any(models_dir.iterdir()):
        print("  Including models...")
        shutil.copytree(models_dir, temp_dir / "models")
        model_count = len(list((temp_dir / "models").glob("*.pt")))
        total_size = sum(f.stat().st_size for f in (temp_dir / "models").glob("*.pt")) / (1024 * 1024)
        print(f"    Added {model_count} models ({total_size:.2f} MB)")
    
    # Build installer
    installer_py = str(builder_dir / "installer_console.py")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=NotYCaptionGenAI_Installer_v4.4",
        "--onefile",
        f"--add-data={temp_dir / 'NotYCaptionGenAI.exe'}{os.pathsep}.",
        f"--add-data={temp_dir / 'NotYCaptionGenAI_Uninstaller.exe'}{os.pathsep}.",
        f"--add-data={temp_dir / 'resources'}{os.pathsep}resources",
        "--hidden-import=ctypes",
        "--hidden-import=subprocess",
        "--hidden-import=shutil",
        "--hidden-import=pathlib",
        "--hidden-import=platform",
        "--hidden-import=tkinter",
        "--console",
        "--noconfirm",
        installer_py
    ]
    
    # Add models
    if (temp_dir / "models").exists():
        for model_file in (temp_dir / "models").glob("*.pt"):
            cmd.insert(4, f"--add-data={model_file}{os.pathsep}models")
    
    # Add icon
    icon_path = temp_dir / "resources" / "logo.ico"
    if icon_path.exists():
        cmd.insert(4, f"--icon={icon_path}")
    
    try:
        subprocess.run(cmd, cwd=str(temp_dir), check=True, timeout=300)
        print("\n✅ Installer built successfully!")
    except Exception as e:
        print(f"\n❌ Installer build failed: {e}")
        sys.exit(1)
    
    # Copy installer to root
    installer_exe = temp_dir / "dist" / "NotYCaptionGenAI_Installer_v4.4.exe"
    if installer_exe.exists():
        final_installer = base_dir / "NotYCaptionGenAI_Installer_v4.4.exe"
        shutil.copy2(installer_exe, final_installer)
        size = final_installer.stat().st_size / 1024 / 1024
        print(f"\n✅ Installer created: {final_installer} ({size:.2f} MB)")
    else:
        print("\n❌ Installer not found!")
    
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(temp_build_dir, ignore_errors=True)
    shutil.rmtree(builder_dir / "build", ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print(f"Installer: {base_dir / 'NotYCaptionGenAI_Installer_v4.4.exe'}")
    print("=" * 60)

if __name__ == "__main__":
    build_all()