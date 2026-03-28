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

class InstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NotY Caption Generator AI Installer v4.3")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # Get installer directory
        if getattr(sys, 'frozen', False):
            self.installer_dir = Path(sys.executable).parent
        else:
            self.installer_dir = Path(__file__).parent
        
        # Set icon
        try:
            icon_path = self.installer_dir / "resources" / "logo.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Variables
        self.install_base = tk.StringVar(value="C:\\")
        self.install_path = tk.StringVar(value="C:\\NotYCaptionGenAI")
        self.create_shortcut = tk.BooleanVar(value=True)
        self.create_desktop = tk.BooleanVar(value=True)
        self.register_sendto = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
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
        
        # Installation path
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
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding=10)
        options_frame.pack(fill="x", pady=10)
        
        ttk.Checkbutton(options_frame, text="Create Start Menu shortcut", variable=self.create_shortcut).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Create Desktop shortcut", variable=self.create_desktop).pack(anchor="w", pady=2)
        ttk.Checkbutton(options_frame, text="Add to 'Send To' menu", variable=self.register_sendto).pack(anchor="w", pady=2)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", length=500)
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(main_frame, text="Ready to install")
        self.status_label.pack(pady=5)
        
        # Buttons
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
        
    def install(self):
        try:
            install_dir = Path(self.install_path.get())
            
            self.update_status("Creating installation directory...")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Find executable
            exe_source = None
            for loc in [self.installer_dir / "NotYCaptionGenAI.exe", Path.cwd() / "NotYCaptionGenAI.exe"]:
                if loc.exists():
                    exe_source = loc
                    break
            
            if not exe_source:
                raise Exception("Main executable not found")
            
            self.update_status("Copying files...")
            shutil.copy2(exe_source, install_dir / "NotYCaptionGenAI.exe")
            
            # Create uninstaller
            self.update_status("Creating uninstaller...")
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
            
            self.update_status("Installation complete!")
            self.progress.stop()
            
            messagebox.showinfo(
                "Installation Complete",
                f"NotY Caption Generator AI v4.3 installed to:\n{install_dir}"
            )
            self.root.quit()
            
        except Exception as e:
            self.update_status(f"Installation failed: {e}")
            messagebox.showerror("Installation Failed", str(e))
            self.install_btn.config(state="normal")
            
    def update_status(self, message):
        self.status_label.config(text=message)
        self.progress.start()
        self.root.update()
        
    def create_uninstaller(self, install_dir):
        content = f'''@echo off
echo Removing NotY Caption Generator AI...
rmdir /s /q "{install_dir}" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\NotYCaptionGenAi.lnk" 2>nul
del "%USERPROFILE%\\Desktop\\NotYCaptionGenAi.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\SendTo\\NotYCaptionGenAi.lnk" 2>nul
reg delete "HKCU\\Software\\NotYCaptionGenAi" /f 2>nul
echo Uninstall complete!
pause
'''
        (install_dir / "uninstall.bat").write_text(content, encoding='utf-8')
        
    def create_shortcut(self, path, target):
        ps = f'''$s = New-Object -ComObject WScript.Shell
$l = $s.CreateShortcut("{path}")
$l.TargetPath = "{target}"
$l.Save()'''
        subprocess.run(["powershell", "-Command", ps], capture_output=True)
        
    def create_start_menu_shortcut(self, install_dir):
        start = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAi.lnk"
        self.create_shortcut(start, install_dir / "NotYCaptionGenAI.exe")
        
    def create_desktop_shortcut(self, install_dir):
        desktop = Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAi.lnk"
        self.create_shortcut(desktop, install_dir / "NotYCaptionGenAI.exe")
        
    def register_sendto_menu(self, install_dir):
        sendto = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAi.lnk"
        sendto.parent.mkdir(parents=True, exist_ok=True)
        self.create_shortcut(sendto, install_dir / "NotYCaptionGenAI.exe")
        
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