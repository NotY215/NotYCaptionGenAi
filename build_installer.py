#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI - Complete Installer Builder v5.2
Creates a professional Windows installer with external models folder
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import zipfile
import tempfile
from pathlib import Path

APP_NAME = "NotYCaptionGenAI"
APP_DISPLAY_NAME = "NotY Caption Generator AI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"

def create_portable_zip():
    """Create portable ZIP version"""
    print("\n[1/3] Creating portable ZIP...")
    
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    zip_name = dist_dir / f"{APP_NAME}_Portable_v{APP_VERSION}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        exe_file = dist_dir / f"{APP_NAME}.exe"
        if exe_file.exists():
            zipf.write(exe_file, f"{APP_NAME}.exe")
            print(f"  Added: {APP_NAME}.exe")
        
        # Add folders
        for folder in ['ffmpeg', 'resources']:
            folder_path = dist_dir / folder
            if folder_path.exists():
                for file in folder_path.rglob('*'):
                    if file.is_file():
                        arcname = f"{folder}/{file.relative_to(folder_path)}"
                        zipf.write(file, arcname)
                        print(f"  Added: {arcname}")
        
        # Add README
        readme = dist_dir / "README.txt"
        readme_content = f'''NotY Caption Generator AI v{APP_VERSION}
=====================================

Portable Version - No installation required!

HOW TO USE:
1. Extract all files to any folder
2. Run {APP_NAME}.exe
3. Models will be downloaded automatically when first used

REQUIREMENTS:
- Windows 10 or later
- 4GB RAM (8GB recommended)
- 4GB free disk space

FEATURES:
- YouTube video captioning
- Local video/audio captioning
- 6 languages + auto detect
- Smart line breaking
- Lyrics search

SUPPORT:
Telegram: https://t.me/Noty_215
YouTube: https://www.youtube.com/@NotY215

Copyright (c) {APP_YEAR} {APP_AUTHOR}
'''
        with open(readme, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        zipf.write(readme, "README.txt")
        readme.unlink()
    
    size = zip_name.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Portable ZIP created: {zip_name} ({size:.2f} MB)")
    return zip_name

def create_batch_installer():
    """Create simple batch installer"""
    print("\n[2/3] Creating batch installer...")
    
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    batch_content = f'''@echo off
title {APP_DISPLAY_NAME} v{APP_VERSION} Installer
color 0A

echo ============================================================
echo    {APP_DISPLAY_NAME} v{APP_VERSION} Installer
echo    Copyright (c) {APP_YEAR} {APP_AUTHOR}
echo ============================================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Administrator rights required!
    echo Please run as administrator.
    pause
    exit /b 1
)

:: Set installation path
set /p "INSTALL_PATH=Installation directory [C:\\{APP_DISPLAY_NAME}]: "
if "%INSTALL_PATH%"=="" set INSTALL_PATH=C:\\{APP_DISPLAY_NAME}

echo.
echo Installing to: %INSTALL_PATH%
echo.

:: Create directories
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"
if not exist "%INSTALL_PATH%\\ffmpeg" mkdir "%INSTALL_PATH%\\ffmpeg"
if not exist "%INSTALL_PATH%\\resources" mkdir "%INSTALL_PATH%\\resources"
if not exist "%INSTALL_PATH%\\models" mkdir "%INSTALL_PATH%\\models"

:: Copy files
echo Copying files...
copy /Y "{APP_NAME}.exe" "%INSTALL_PATH%\\" >nul
xcopy /E /I /Y "ffmpeg" "%INSTALL_PATH%\\ffmpeg\\" >nul
xcopy /E /I /Y "resources" "%INSTALL_PATH%\\resources\\" >nul

:: Copy models if they exist
if exist "models\\*.pt" (
    echo Copying models...
    xcopy /E /I /Y "models" "%INSTALL_PATH%\\models\\" >nul
)

:: Create shortcuts
echo Creating shortcuts...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\\Desktop\\{APP_DISPLAY_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $SC.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_DISPLAY_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $SC.Save()"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\SendTo\\{APP_DISPLAY_NAME}.lnk'); $SC.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $SC.Save()"

:: Registry
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "DisplayName" /d "{APP_DISPLAY_NAME} v{APP_VERSION}" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "UninstallString" /d "%INSTALL_PATH%\\Uninstall.bat" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "Publisher" /d "{APP_AUTHOR}" /f
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /v "DisplayVersion" /d "{APP_VERSION}" /f

:: Create uninstaller
echo @echo off > "%INSTALL_PATH%\\Uninstall.bat"
echo title {APP_DISPLAY_NAME} Uninstaller >> "%INSTALL_PATH%\\Uninstall.bat"
echo echo Uninstalling {APP_DISPLAY_NAME}... >> "%INSTALL_PATH%\\Uninstall.bat"
echo rmdir /s /q "%INSTALL_PATH%" >> "%INSTALL_PATH%\\Uninstall.bat"
echo del "%%USERPROFILE%%\\Desktop\\{APP_DISPLAY_NAME}.lnk" >> "%INSTALL_PATH%\\Uninstall.bat"
echo del "%%APPDATA%%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_DISPLAY_NAME}.lnk" >> "%INSTALL_PATH%\\Uninstall.bat"
echo del "%%APPDATA%%\\Microsoft\\Windows\\SendTo\\{APP_DISPLAY_NAME}.lnk" >> "%INSTALL_PATH%\\Uninstall.bat"
echo reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" /f >> "%INSTALL_PATH%\\Uninstall.bat"
echo echo Uninstall complete! >> "%INSTALL_PATH%\\Uninstall.bat"
echo pause >> "%INSTALL_PATH%\\Uninstall.bat"

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Installed to: %INSTALL_PATH%
echo.
echo You can now run {APP_DISPLAY_NAME} from:
echo   - Desktop shortcut
echo   - Start Menu
echo   - Right-click menu "Send To"
echo.
pause
'''
    
    batch_installer = dist_dir / "Install.bat"
    with open(batch_installer, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"[OK] Batch installer created: {batch_installer}")
    return batch_installer

def create_powershell_installer():
    """Create PowerShell installer script"""
    print("\n[3/3] Creating PowerShell installer...")
    
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    ps_content = f'''# {APP_DISPLAY_NAME} v{APP_VERSION} Installer
# Copyright (c) {APP_YEAR} {APP_AUTHOR}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "$([char]0x00A9) {APP_DISPLAY_NAME} v{APP_VERSION} Installer" -ForegroundColor Green
Write-Host "Copyright (c) {APP_YEAR} {APP_AUTHOR}" -ForegroundColor Gray
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check admin rights
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {{
    Write-Host "[ERROR] Administrator rights required!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}}

# Installation path
$defaultPath = "C:\\{APP_DISPLAY_NAME}"
$installPath = Read-Host "Installation directory [$defaultPath]"
if (-not $installPath) {{ $installPath = $defaultPath }}

Write-Host ""
Write-Host "Installing to: $installPath" -ForegroundColor Yellow
Write-Host ""

# Create directories
New-Item -ItemType Directory -Force -Path $installPath | Out-Null
New-Item -ItemType Directory -Force -Path "$installPath\\ffmpeg" | Out-Null
New-Item -ItemType Directory -Force -Path "$installPath\\resources" | Out-Null
New-Item -ItemType Directory -Force -Path "$installPath\\models" | Out-Null

# Copy files
Write-Host "Copying files..." -ForegroundColor Cyan
Copy-Item -Path "{APP_NAME}.exe" -Destination "$installPath\\" -Force
Copy-Item -Path "ffmpeg\\*" -Destination "$installPath\\ffmpeg\\" -Recurse -Force
Copy-Item -Path "resources\\*" -Destination "$installPath\\resources\\" -Recurse -Force

# Copy models if they exist
if (Test-Path "models\\*.pt") {{
    Write-Host "Copying models..." -ForegroundColor Cyan
    Copy-Item -Path "models\\*" -Destination "$installPath\\models\\" -Recurse -Force
}}

# Create shortcuts
Write-Host "Creating shortcuts..." -ForegroundColor Cyan
$WScriptShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$startMenu = [Environment]::GetFolderPath("StartMenu")
$sendTo = [Environment]::GetFolderPath("SendTo")

$shortcut = $WScriptShell.CreateShortcut("$desktop\\{APP_DISPLAY_NAME}.lnk")
$shortcut.TargetPath = "$installPath\\{APP_NAME}.exe"
$shortcut.Save()

$shortcut = $WScriptShell.CreateShortcut("$startMenu\\Programs\\{APP_DISPLAY_NAME}.lnk")
$shortcut.TargetPath = "$installPath\\{APP_NAME}.exe"
$shortcut.Save()

$shortcut = $WScriptShell.CreateShortcut("$sendTo\\{APP_DISPLAY_NAME}.lnk")
$shortcut.TargetPath = "$installPath\\{APP_NAME}.exe"
$shortcut.Save()

# Registry
Write-Host "Registering in Windows..." -ForegroundColor Cyan
$regPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}"
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name "DisplayName" -Value "{APP_DISPLAY_NAME} v{APP_VERSION}"
Set-ItemProperty -Path $regPath -Name "UninstallString" -Value "$installPath\\Uninstall.ps1"
Set-ItemProperty -Path $regPath -Name "Publisher" -Value "{APP_AUTHOR}"
Set-ItemProperty -Path $regPath -Name "DisplayVersion" -Value "{APP_VERSION}"

# Create uninstaller
$uninstallerContent = @"
# {APP_DISPLAY_NAME} Uninstaller
Write-Host "Uninstalling {APP_DISPLAY_NAME}..." -ForegroundColor Yellow
Remove-Item -Path "$installPath" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$desktop\\{APP_DISPLAY_NAME}.lnk" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$startMenu\\Programs\\{APP_DISPLAY_NAME}.lnk" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$sendTo\\{APP_DISPLAY_NAME}.lnk" -Force -ErrorAction SilentlyContinue
Remove-Item -Path $regPath -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Uninstall complete!" -ForegroundColor Green
Read-Host "Press Enter to exit"
"@
Set-Content -Path "$installPath\\Uninstall.ps1" -Value $uninstallerContent

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Installed to: $installPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "You can now run {APP_DISPLAY_NAME} from:" -ForegroundColor Cyan
Write-Host "  - Desktop shortcut"
Write-Host "  - Start Menu"
Write-Host "  - Right-click menu 'Send To'"
Write-Host ""
Read-Host "Press Enter to exit"
'''
    
    ps_installer = dist_dir / "Install.ps1"
    with open(ps_installer, 'w', encoding='utf-8') as f:
        f.write(ps_content)
    
    print(f"[OK] PowerShell installer created: {ps_installer}")
    return ps_installer

def create_inno_setup_installer():
    """Create Inno Setup installer if available"""
    print("\n[Optional] Checking for Inno Setup...")
    
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Check if Inno Setup is installed
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    ]
    
    inno_exe = None
    for path in inno_paths:
        if Path(path).exists():
            inno_exe = path
            break
    
    if not inno_exe:
        print("[SKIP] Inno Setup not found. Install Inno Setup for better installer.")
        return None
    
    # Create Inno Setup script
    iss_content = f'''; {APP_DISPLAY_NAME} Installer
; Inno Setup Script

[Setup]
AppId={{{{{APP_NAME}}}}}
AppName={APP_DISPLAY_NAME}
AppVersion={APP_VERSION}
AppPublisher={APP_AUTHOR}
AppCopyright=Copyright (c) {APP_YEAR} {APP_AUTHOR}
DefaultDirName={{pf}}\\{APP_DISPLAY_NAME}
DefaultGroupName={APP_DISPLAY_NAME}
UninstallDisplayIcon={{app}}\\{APP_NAME}.exe
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=resources\\app.ico
Uninstallable=yes
CreateUninstallRegKey=yes
OutputDir=dist
OutputBaseFilename={APP_NAME}_Installer_v{APP_VERSION}
VersionInfoVersion={APP_VERSION}.0
VersionInfoCompany={APP_AUTHOR}
VersionInfoDescription={APP_DISPLAY_NAME}
VersionInfoProductName={APP_DISPLAY_NAME}
VersionInfoProductVersion={APP_VERSION}
DisableDirPage=no
DisableProgramGroupPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; 
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut";
Name: "sendtoicon"; Description: "Add to &Send To menu";

[Files]
Source: "dist\\{APP_NAME}.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "dist\\ffmpeg\\*"; DestDir: "{{app}}\\ffmpeg"; Flags: ignoreversion recursesubdirs
Source: "dist\\resources\\*"; DestDir: "{{app}}\\resources"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{{group}}\\{APP_DISPLAY_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
Name: "{{group}}\\Uninstall"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\{APP_DISPLAY_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Windows\\SendTo\\{APP_DISPLAY_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"; Tasks: sendtoicon

[Run]
Filename: "{{app}}\\{APP_NAME}.exe"; Description: "Launch {APP_DISPLAY_NAME}"; Flags: postinstall nowait skipifsilent
'''
    
    iss_file = base_dir / "installer.iss"
    with open(iss_file, 'w', encoding='utf-8') as f:
        f.write(iss_content)
    
    try:
        result = subprocess.run([inno_exe, str(iss_file)], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            installer_path = dist_dir / f"{APP_NAME}_Installer_v{APP_VERSION}.exe"
            if installer_path.exists():
                size = installer_path.stat().st_size / (1024 * 1024)
                print(f"[OK] Inno Setup installer created: {installer_path} ({size:.2f} MB)")
                return installer_path
        else:
            print("[WARNING] Inno Setup compilation failed")
    except Exception as e:
        print(f"[WARNING] Inno Setup error: {e}")
    
    iss_file.unlink(missing_ok=True)
    return None

def build_all():
    """Build all installer formats"""
    print("=" * 70)
    print(f"Building {APP_DISPLAY_NAME} v{APP_VERSION} Installers")
    print(f"Copyright (c) {APP_YEAR} {APP_AUTHOR}")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist"
    
    # Ensure dist directory exists
    if not dist_dir.exists():
        print("[ERROR] dist directory not found! Build the executable first.")
        print("Run: python build_exe.py")
        sys.exit(1)
    
    # Change to dist directory for relative paths
    os.chdir(dist_dir)
    
    # Create all installers
    portable_zip = create_portable_zip()
    batch_installer = create_batch_installer()
    ps_installer = create_powershell_installer()
    inno_installer = create_inno_setup_installer()
    
    # Change back
    os.chdir(base_dir)
    
    print("\n" + "=" * 70)
    print("ALL INSTALLERS CREATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\nOutput directory: {dist_dir}")
    print("\nInstallers created:")
    
    if portable_zip:
        size = portable_zip.stat().st_size / (1024 * 1024)
        print(f"  - {portable_zip.name} ({size:.2f} MB) - Portable ZIP")
    
    if batch_installer:
        print(f"  - {batch_installer.name} - Batch Installer")
    
    if ps_installer:
        print(f"  - {ps_installer.name} - PowerShell Installer")
    
    if inno_installer:
        size = inno_installer.stat().st_size / (1024 * 1024)
        print(f"  - {inno_installer.name} ({size:.2f} MB) - Windows Installer")
    
    print("\n" + "=" * 70)
    print("\nTo use the installers:")
    print("  - Portable: Extract ZIP and run the EXE")
    print("  - Batch: Run Install.bat as Administrator")
    print("  - PowerShell: Run Install.ps1 as Administrator")
    print("  - Windows: Run the Setup.exe file")
    print("=" * 70)

if __name__ == "__main__":
    build_all()