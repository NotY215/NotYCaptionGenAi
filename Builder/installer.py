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
        self.root.geometry("750x700")
        self.root.resizable(False, False)
        
        # Get the directory where the installer is running from
        if getattr(sys, 'frozen', False):
            self.installer_dir = Path(sys.executable).parent
        else:
            self.installer_dir = Path(__file__).parent
        
        # Set window icon
        try:
            icon_path = self.installer_dir / "resources" / "logo.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Dynamic installation path
        self.install_base = tk.StringVar(value="C:\\")
        self.install_path = tk.StringVar(value="C:\\NotYCaptionGenAI")
        self.create_shortcut = tk.BooleanVar(value=True)
        self.create_desktop = tk.BooleanVar(value=True)
        self.register_sendto = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the installer UI with scrolling"""
        main_canvas = tk.Canvas(self.root, highlightthickness=0, bg='white')
        main_canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        main_canvas.configure(yscrollcommand=scrollbar.set, bg='white')
        
        main_frame = ttk.Frame(main_canvas)
        main_canvas.create_window((0, 0), window=main_frame, anchor="nw", width=730)
        
        def on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        main_frame.bind("<Configure>", on_frame_configure)
        
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left", padx=10)
        
        title_label = ttk.Label(
            title_frame,
            text="NotY Caption Generator AI",
            font=("Segoe UI", 22, "bold")
        )
        title_label.pack(anchor="w")
        
        version_label = ttk.Label(
            title_frame,
            text="Version 4.3 | Copyright (c) 2026 NotY215 | LGPL-3.0",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        version_label.pack(anchor="w")
        
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)
        
        # Installation path
        path_frame = ttk.LabelFrame(main_frame, text="Installation Location", padding=15)
        path_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(path_frame, text="Select installation folder (will create NotYCaptionGenAI subfolder):", 
                 font=("Segoe UI", 10)).grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(path_frame, text="Base Directory:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        base_entry = ttk.Entry(path_frame, textvariable=self.install_base, width=45)
        base_entry.grid(row=1, column=1, padx=5, pady=5)
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_install_base)
        browse_btn.grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(path_frame, text="Full installation path:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        path_display = ttk.Entry(path_frame, textvariable=self.install_path, width=45, state="readonly")
        path_display.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding=15)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Checkbutton(options_frame, text="Create Start Menu shortcut", variable=self.create_shortcut).grid(row=0, column=0, sticky="w", padx=5, pady=8)
        ttk.Checkbutton(options_frame, text="Create Desktop shortcut", variable=self.create_desktop).grid(row=1, column=0, sticky="w", padx=5, pady=8)
        ttk.Checkbutton(options_frame, text="Add to 'Send To' menu (right-click any video/audio file)", variable=self.register_sendto).grid(row=2, column=0, sticky="w", padx=5, pady=8)
        
        # Progress
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress = ttk.Progressbar(self.progress_frame, mode="determinate", length=670)
        self.progress.pack(pady=5)
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready to install", anchor="center")
        self.status_label.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.install_btn = ttk.Button(button_frame, text="Install", command=self.start_install, width=15)
        self.install_btn.pack(side="right", padx=5)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.root.quit, width=15)
        self.cancel_btn.pack(side="right", padx=5)
        
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
        self.cancel_btn.config(state="disabled")
        threading.Thread(target=self.install, daemon=True).start()
        
    def update_progress(self, value, max_value, message):
        percent = int((value / max_value) * 100)
        self.progress['value'] = percent
        self.status_label.config(text=f"{message}... {percent}%")
        self.root.update()
        
    def extract_archive_to_ram(self, archive_path, dest_dir):
        """Extract compressed archive to RAM first then write to disk (faster)"""
        self.update_progress(0, 100, "Loading compressed data into RAM")
        
        with open(archive_path, 'rb') as f:
            # Read compressed data size
            compressed_size = struct.unpack('Q', f.read(8))[0]
            self.update_progress(10, 100, f"Reading {compressed_size / 1024 / 1024:.1f} MB to RAM")
            
            # Read all compressed data into RAM
            compressed_data = f.read(compressed_size)
            self.update_progress(30, 100, "Decompressing in RAM")
            
            # Decompress everything in RAM
            decompressed_data = zlib.decompress(compressed_data)
            self.update_progress(60, 100, "Writing files to disk")
            
            # Parse file list and write files
            decompressed_str = decompressed_data.decode('utf-8')
            parts = decompressed_str.split('\n')
            
            # First line is the file list
            file_list = []
            idx = 0
            for line in parts:
                if '|' in line:
                    file_path, size = line.split('|')
                    file_list.append((file_path, int(size)))
                    idx = decompressed_str.find('\n', idx) + 1
                else:
                    break
            
            # Write files
            data_start = idx
            for i, (file_path, size) in enumerate(file_list):
                full_path = dest_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract file data
                file_data = decompressed_data[data_start:data_start + size]
                with open(full_path, 'wb') as out:
                    out.write(file_data)
                
                data_start += size
                
                # Update progress
                progress = 60 + int((i + 1) / len(file_list) * 40)
                self.update_progress(progress, 100, f"Writing {file_path}")
        
        self.update_progress(100, 100, "Extraction complete")
        
    def install(self):
        try:
            start_time = time.time()
            install_dir = Path(self.install_path.get())
            
            self.update_progress(0, 100, "Creating installation directory")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if we have compressed archive or direct files
            archive_path = self.installer_dir / "data.bin"
            resources_source = self.installer_dir / "resources"
            exe_source = self.installer_dir / "NotYCaptionGenAI.exe"
            
            if archive_path.exists():
                # Extract from compressed archive using RAM for speed
                self.update_progress(5, 100, "Using compressed installer")
                self.extract_archive_to_ram(archive_path, install_dir)
            else:
                # Copy main executable
                self.update_progress(20, 100, "Copying main executable")
                if exe_source.exists():
                    shutil.copy2(exe_source, install_dir / "NotYCaptionGenAI.exe")
                else:
                    raise Exception("Main executable not found")
                
                # Copy resources
                self.update_progress(30, 100, "Copying resources")
                if resources_source.exists():
                    dest_resources = install_dir / "resources"
                    if dest_resources.exists():
                        shutil.rmtree(dest_resources)
                    shutil.copytree(resources_source, dest_resources)
            
            # Create uninstaller
            self.update_progress(85, 100, "Creating uninstaller")
            self.create_uninstaller(install_dir)
            
            # Create shortcuts
            if self.create_shortcut.get():
                self.update_progress(88, 100, "Creating Start Menu shortcut")
                self.create_start_menu_shortcut(install_dir)
                
            if self.create_desktop.get():
                self.update_progress(91, 100, "Creating Desktop shortcut")
                self.create_desktop_shortcut(install_dir)
                
            if self.register_sendto.get():
                self.update_progress(94, 100, "Adding to Send To menu")
                self.register_sendto_menu(install_dir)
            
            # Create registry entries
            self.update_progress(97, 100, "Registering application")
            self.register_application(install_dir)
            
            elapsed = time.time() - start_time
            self.update_progress(100, 100, "Installation complete!")
            
            messagebox.showinfo(
                "Installation Complete", 
                f"NotY Caption Generator AI v4.3 has been installed to:\n{install_dir}\n\n"
                f"Installation time: {elapsed:.1f} seconds\n\n"
                f"Start Menu shortcut: {'Created' if self.create_shortcut.get() else 'Skipped'}\n"
                f"Desktop shortcut: {'Created' if self.create_desktop.get() else 'Skipped'}\n"
                f"Send To menu: {'Added' if self.register_sendto.get() else 'Skipped'}\n\n"
                f"Tip: Right-click any video/audio file and select 'Send To' > 'NotYCaptionGenAi'"
            )
            self.root.quit()
            
        except Exception as e:
            self.status_label.config(text=f"Installation failed: {e}")
            messagebox.showerror("Installation Failed", str(e))
            self.install_btn.config(state="normal")
            self.cancel_btn.config(state="normal")
            
    def create_uninstaller(self, install_dir):
        uninstaller_content = f'''@echo off
title NotY Caption Generator AI Uninstaller v4.3
color 0C
echo ============================================================
echo   NotY Caption Generator AI Uninstaller
echo   Version 4.3 | Copyright (c) 2026 NotY215
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
echo Uninstallation complete!
echo.
pause
'''
        uninstaller_path = install_dir / "uninstall.bat"
        with open(uninstaller_path, "w", encoding='utf-8') as f:
            f.write(uninstaller_content)
            
    def create_shortcut_file(self, shortcut_path, target_path):
        ps_script = f'''
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target_path}"
$Shortcut.WorkingDirectory = "{target_path.parent}"
$Shortcut.IconLocation = "{target_path}"
$Shortcut.Save()
'''
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        
    def create_start_menu_shortcut(self, install_dir):
        start_menu = Path(os.environ.get("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        shortcut_path = start_menu / "NotYCaptionGenAi.lnk"
        self.create_shortcut_file(shortcut_path, install_dir / "NotYCaptionGenAI.exe")
        
    def create_desktop_shortcut(self, install_dir):
        desktop = Path(os.environ.get("USERPROFILE")) / "Desktop"
        shortcut_path = desktop / "NotYCaptionGenAi.lnk"
        self.create_shortcut_file(shortcut_path, install_dir / "NotYCaptionGenAI.exe")
        
    def register_sendto_menu(self, install_dir):
        sendto_dir = Path(os.environ.get("APPDATA")) / "Microsoft" / "Windows" / "SendTo"
        sendto_dir.mkdir(parents=True, exist_ok=True)
        shortcut_path = sendto_dir / "NotYCaptionGenAi.lnk"
        self.create_shortcut_file(shortcut_path, install_dir / "NotYCaptionGenAI.exe")
        
    def register_application(self, install_dir):
        reg_script = f'''
New-Item -Path "HKCU:\\Software\\NotYCaptionGenAi" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "InstallPath" -Value "{install_dir}"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "Version" -Value "4.3"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "DisplayName" -Value "NotY Caption Generator AI"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "Publisher" -Value "NotY215"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "Copyright" -Value "Copyright (c) 2026 NotY215"
'''
        subprocess.run(["powershell", "-Command", reg_script], capture_output=True)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    installer = InstallerGUI()
    installer.run()