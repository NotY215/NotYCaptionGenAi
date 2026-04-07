#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Uninstaller v5.2 (Console)
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import time
import platform
import ctypes
from pathlib import Path
import winreg

# Application metadata
APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "5.2"
APP_AUTHOR = "NotY215"

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'

if platform.system() == "Windows":
    os.system('color')

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the script as administrator"""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return True
    except:
        return False

def print_header():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("+" + "=" * 58 + "+")
    print("|" + f"{APP_NAME} Uninstaller v{APP_VERSION}".center(58) + "|")
    print("|" + f"Copyright (c) 2026 {APP_AUTHOR}".center(58) + "|")
    print("+" + "=" * 58 + "+")
    print(f"{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}[ERROR] {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.CYAN}[INFO] {message}{Colors.RESET}")

def get_install_path():
    """Get install path from registry"""
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
        install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
        winreg.CloseKey(key)
        return Path(install_path)
    except:
        return None

def remove_registry():
    """Remove registry entries"""
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\NotYCaptionGenAI"
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        print_success("Registry entries removed")
        return True
    except FileNotFoundError:
        print_info("Registry entries not found")
        return True
    except PermissionError:
        print_error("Permission denied - run as administrator")
        return False
    except Exception as e:
        print_error(f"Failed to remove registry: {e}")
        return False

def get_directory_size(path):
    """Get directory size in MB"""
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except:
        pass
    return total / (1024 * 1024)

def kill_processes(install_path):
    """Kill any running instances of the app"""
    try:
        subprocess.run(['taskkill', '/f', '/im', 'NotYCaptionGenAI.exe'], capture_output=True)
        time.sleep(1)
    except:
        pass

def remove_shortcuts():
    """Remove all shortcuts"""
    shortcuts = [
        Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAI.lnk",
        Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAI.lnk",
        Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAI.lnk"
    ]
    removed = 0
    for shortcut in shortcuts:
        if shortcut.exists():
            try:
                shortcut.unlink()
                print(f"  Removed: {shortcut.name}")
                removed += 1
            except:
                pass
    return removed

def create_self_delete_bat(install_path, uninstaller_path):
    """Create a batch file that will delete the entire installation folder including the uninstaller"""
    bat_path = Path(os.environ["TEMP"]) / f"delete_noty_{int(time.time())}.bat"
    
    bat_content = f'''@echo off
timeout /t 3 /nobreak >nul
echo Deleting NotYCaptionGenAI installation...

:: Kill any remaining processes
taskkill /f /im NotYCaptionGenAI.exe 2>nul

:: Remove the entire installation directory
cd /d "C:\\"
rmdir /s /q "{install_path}" 2>nul

:: Remove shortcuts again if any remain
del /f /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\NotYCaptionGenAI.lnk" 2>nul
del /f /q "%USERPROFILE%\\Desktop\\NotYCaptionGenAI.lnk" 2>nul
del /f /q "%APPDATA%\\Microsoft\\Windows\\SendTo\\NotYCaptionGenAI.lnk" 2>nul

:: Clear cache directories
rmdir /s /q "%TEMP%\\NotYCaptionGenAI" 2>nul
rmdir /s /q "%LOCALAPPDATA%\\NotYCaptionGenAI" 2>nul

echo Cleanup completed.

:: Delete this batch file
del "%~f0" 2>nul
exit
'''
    
    try:
        with open(bat_path, 'w') as f:
            f.write(bat_content)
        return bat_path
    except Exception as e:
        print_error(f"Failed to create cleanup script: {e}")
        return None

def uninstall():
    # Check for admin privileges
    if not is_admin():
        print_warning = lambda x: print(f"{Colors.YELLOW}[WARNING] {x}{Colors.RESET}")
        print_warning("Administrator privileges required for complete uninstallation!")
        print_info("The uninstaller will now restart with administrator privileges...")
        time.sleep(2)
        if run_as_admin():
            sys.exit(0)
        else:
            print_error("Failed to elevate privileges. Uninstallation will continue but registry may not be removed.")
    
    print_header()
    print_info("Starting uninstallation process...")
    print()
    
    install_path = get_install_path()
    
    if not install_path or not install_path.exists():
        print_error("Installation not found in registry!")
        print_info("If the application was installed manually, please delete the folder manually.")
        return False
    
    print_info(f"Found installation at: {install_path}")
    print_info(f"Installation size: {get_directory_size(install_path):.2f} MB")
    print()
    
    print(f"{Colors.YELLOW}[WARNING] This will permanently remove {APP_NAME}{Colors.RESET}")
    print(f"{Colors.YELLOW}   and all its components from your computer.{Colors.RESET}")
    print()
    
    response = input(f"{Colors.CYAN}Are you sure you want to uninstall? (y/n): {Colors.RESET}").lower()
    if response not in ['y', 'yes']:
        print_info("Uninstallation cancelled.")
        return False
    
    print()
    
    try:
        # Kill running processes
        print_info("Stopping running instances...")
        kill_processes(install_path)
        print_success("Processes stopped")
        
        # Remove shortcuts
        print_info("Removing shortcuts...")
        removed = remove_shortcuts()
        print_success(f"Removed {removed} shortcuts")
        
        # Remove registry entries
        print_info("Removing registry entries...")
        remove_registry()
        
        # Get current uninstaller path before it's deleted
        current_uninstaller = Path(sys.executable) if getattr(sys, 'frozen', False) else None
        
        print_info("Preparing cleanup script...")
        
        # Create self-deleting batch file
        bat_file = create_self_delete_bat(install_path, current_uninstaller)
        
        if bat_file and bat_file.exists():
            print_success("Cleanup script created")
            print_info("The cleanup script will run in the background to complete removal...")
            
            # Run the batch file in background
            subprocess.Popen([str(bat_file)], shell=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS)
            
            # Wait a moment for the batch file to start
            time.sleep(2)
            
            # Exit the uninstaller - the batch file will delete everything including this
            print_success("Uninstallation complete!")
            print_info("The application will be fully removed in a few moments...")
            return True
        else:
            # Fallback: try to delete manually
            print_info("Performing manual cleanup...")
            try:
                # Try to delete the installation directory
                shutil.rmtree(install_path, ignore_errors=True)
                print_success("Installation directory removed")
            except Exception as e:
                print_error(f"Could not remove installation directory: {e}")
                print_info("Please delete the folder manually: " + str(install_path))
            
            # Clear cache directories
            cache_dirs = [
                Path(os.environ.get('TEMP', '.')) / "NotYCaptionGenAI",
                Path(os.environ.get('LOCALAPPDATA', '.')) / "NotYCaptionGenAI",
            ]
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    try:
                        shutil.rmtree(cache_dir, ignore_errors=True)
                        print(f"  Removed cache: {cache_dir}")
                    except:
                        pass
            
            print_success("Uninstallation complete!")
            return True
        
    except Exception as e:
        print_error(f"Uninstallation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = uninstall()
    
    if success:
        print_success("\nUninstallation completed successfully!")
        if getattr(sys, 'frozen', False):
            print_info("The uninstaller will close now...")
            time.sleep(3)
    else:
        print_error("\nUninstallation failed!")
        input("\nPress Enter to exit...")