#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Installer v4.3
Copyright (c) 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import time
import struct
import zlib

class InstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NotY Caption Generator AI Installer v4.3")
        self.root.geometry("650x650")
        self.root.resizable(False, False)
        
        if getattr(sys, 'frozen', False):
            self.installer_dir = Path(sys.executable).parent
        else:
            self.installer_dir = Path(__file__).parent
        
        # Set icon
        try:
            icon_path = self.installer_dir / "logo.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        self.install_base = tk.StringVar(value="C:\\")
        self.install_path = tk.StringVar(value="C:\\NotYCaptionGenAI")
        self.create_shortcut = tk.BooleanVar(value=True)
        self.create_desktop = tk.BooleanVar(value=True)
        self.register_sendto = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text="NotY Caption Generator AI",
            font=("Segoe UI", 20, "bold")
        )
        title_label.pack(pady=(0, 5))
        
        version_label = ttk.Label(
            main_frame,
            text="Version 4.3 | Copyright (c) 2026 NotY215 | LGPL-3.0",
            font=("Segoe UI", 9)
        )
        version_label.pack(pady=(0, 20))
        
        path_frame = ttk.LabelFrame(main_frame, text="Installation Location", padding=10)
        path_frame.pack(fill="x", pady=10)
        
        ttk.Label(path_frame, text="Select installation folder:").grid(row=0, column=0, sticky="w", pady=5)
        
        base_entry = ttk.Entry(path_frame, textvariable=self.install_base, width=40)
        base_entry.grid(row=1, column=0, padx=(0, 5), pady=5)
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_install_base)
        browse_btn.grid(row=1, column=1, pady=5)
        
        ttk.Label(path_frame, text="Full path:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=(10, 0))
        
        path_display = ttk.Entry(path_frame, textvariable=self.install_path, width=50, state="readonly")
        path_display.grid(row=3, column=0, columnspan=2, pady=5)
        
        ttk.Label(path_frame, text="Will install to: [Selected Path]\\NotYCaptionGenAI", 
                 font=("Segoe UI", 8), foreground="gray").grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding=10)
        options_frame.pack(fill="x", pady=10)
        
        ttk.Checkbutton(options_frame, text="Create Start Menu shortcut", variable=self.create_shortcut).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Create Desktop shortcut", variable=self.create_desktop).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Add to 'Send To' menu", variable=self.register_sendto).pack(anchor="w", pady=2)
        
        self.progress = ttk.Progressbar(main_frame, mode="determinate", length=500)
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(main_frame, text="Ready to install")
        self.status_label.pack(pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.install_btn = ttk.Button(button_frame, text="Install", command=self.start_install, width=15)
        self.install_btn.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Cancel", command=self.root.quit, width=15).pack(side="left", padx=5)
        
    def update_install_path(self):
        base = self.install_base.get().strip()
        if base:
            base = base.rstrip('\\')
            self.install_path.set(f"{base}\\NotYCaptionGenAI")
        else:
            self.install_path.set("C:\\NotYCaptionGenAI")
        
    def browse_install_base(self):
        path = filedialog.askdirectory(title="Select Installation Base Directory")
        if path:
            self.install_base.set(path)
            self.update_install_path()
            
    def start_install(self):
        self.update_install_path()
        self.install_btn.config(state="disabled")
        threading.Thread(target=self.install, daemon=True).start()
        
    def update_progress(self, value, message):
        self.progress['value'] = value
        self.status_label.config(text=message)
        self.root.update()
        
    def install(self):
        try:
            install_dir = Path(self.install_path.get())
            
            self.update_progress(5, "Creating installation directory...")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy main executable
            exe_file = self.installer_dir / "NotYCaptionGenAI.exe"
            if exe_file.exists():
                self.update_progress(10, "Copying executable...")
                shutil.copy2(exe_file, install_dir / "NotYCaptionGenAI.exe")
            
            # Extract models if they exist in compressed form
            models_bin = self.installer_dir / "models.bin"
            if models_bin.exists():
                self.update_progress(20, "Extracting models...")
                self.extract_data(models_bin, install_dir / "models")
            else:
                # Copy models folder if it exists
                models_dir = self.installer_dir / "models"
                if models_dir.exists():
                    self.update_progress(20, "Copying models...")
                    shutil.copytree(models_dir, install_dir / "models")
                else:
                    # Create empty models directory
                    self.update_progress(20, "Creating models directory...")
                    (install_dir / "models").mkdir(parents=True, exist_ok=True)
            
            # Copy files (FFmpeg)
            files_bin = self.installer_dir / "files.bin"
            if files_bin.exists():
                self.update_progress(50, "Extracting FFmpeg files...")
                self.extract_data(files_bin, install_dir / "files")
            else:
                files_dir = self.installer_dir / "files"
                if files_dir.exists():
                    self.update_progress(50, "Copying FFmpeg files...")
                    shutil.copytree(files_dir, install_dir / "files")
            
            # Create uninstaller
            self.update_progress(85, "Creating uninstaller...")
            self.create_uninstaller(install_dir)
            
            # Create shortcuts
            if self.create_shortcut.get():
                self.create_start_menu_shortcut(install_dir)
            if self.create_desktop.get():
                self.create_desktop_shortcut(install_dir)
            if self.register_sendto.get():
                self.register_sendto_menu(install_dir)
            
            # Register application
            self.register_application(install_dir)
            
            self.update_progress(100, "Installation complete!")
            
            messagebox.showinfo(
                "Installation Complete",
                f"NotY Caption Generator AI v4.3 installed to:\n{install_dir}"
            )
            self.root.quit()
            
        except Exception as e:
            self.update_progress(0, f"Installation failed: {e}")
            messagebox.showerror("Installation Failed", str(e))
            self.install_btn.config(state="normal")
            
    def extract_data(self, data_file, dest_dir):
        with open(data_file, 'rb') as f:
            compressed_size = struct.unpack('Q', f.read(8))[0]
            compressed_data = f.read(compressed_size)
            decompressed_data = zlib.decompress(compressed_data)
            
            decompressed_str = decompressed_data.decode('utf-8')
            parts = decompressed_str.split('\n')
            
            file_list = []
            idx = 0
            for line in parts:
                if '|' in line:
                    file_path, size = line.split('|')
                    file_list.append((file_path, int(size)))
                    idx = decompressed_str.find('\n', idx) + 1
                else:
                    break
            
            data_start = idx
            total = len(file_list)
            for i, (file_path, size) in enumerate(file_list):
                full_path = dest_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                file_data = decompressed_data[data_start:data_start + size]
                with open(full_path, 'wb') as out:
                    out.write(file_data)
                data_start += size
                progress = 20 + int((i + 1) / total * 60)
                self.update_progress(progress, f"Extracting {file_path}")
                
    def create_uninstaller(self, install_dir):
        uninstaller_content = f'''@echo off
echo ============================================================
echo   NotY Caption Generator AI Uninstaller v4.3
echo   Copyright (c) 2026 NotY215
echo ============================================================
echo.

echo Removing files...
rmdir /s /q "{install_dir}" 2>nul

echo Removing shortcuts...
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\NotYCaptionGenAi.lnk" 2>nul
del "%USERPROFILE%\\Desktop\\NotYCaptionGenAi.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\SendTo\\NotYCaptionGenAi.lnk" 2>nul

echo Removing registry entries...
reg delete "HKCU\\Software\\NotYCaptionGenAi" /f 2>nul

echo.
echo ============================================================
echo Uninstallation complete!
echo ============================================================
echo.
echo The uninstaller will now delete itself...
timeout /t 2 /nobreak >nul
del "%~f0" 2>nul
exit
'''
        uninstaller_path = install_dir / "uninstall.bat"
        with open(uninstaller_path, 'w', encoding='utf-8') as f:
            f.write(uninstaller_content)
            
    def create_shortcut(self, path, target):
        ps = f'''$s = New-Object -ComObject WScript.Shell
$l = $s.CreateShortcut("{path}")
$l.TargetPath = "{target}"
$l.Save()'''
        subprocess.run(["powershell", "-Command", ps], capture_output=True)
        
    def create_start_menu_shortcut(self, install_dir):
        start = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAi.lnk"
        self.create_shortcut(str(start), str(install_dir / "NotYCaptionGenAI.exe"))
        
    def create_desktop_shortcut(self, install_dir):
        desktop = Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAi.lnk"
        self.create_shortcut(str(desktop), str(install_dir / "NotYCaptionGenAI.exe"))
        
    def register_sendto_menu(self, install_dir):
        sendto = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAi.lnk"
        sendto.parent.mkdir(parents=True, exist_ok=True)
        self.create_shortcut(str(sendto), str(install_dir / "NotYCaptionGenAI.exe"))
        
    def register_application(self, install_dir):
        reg = f'''
New-Item -Path "HKCU:\\Software\\NotYCaptionGenAi" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "InstallPath" -Value "{install_dir}"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "Version" -Value "4.3"
'''
        subprocess.run(["powershell", "-Command", reg], capture_output=True)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    installer = InstallerGUI()
    installer.run()