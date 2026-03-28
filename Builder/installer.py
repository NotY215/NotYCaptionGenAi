#!/usr/bin/env python3
"""
NotY Caption Generator AI Installer v4.2
Copyright © 2026 NotY215
"""

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading

class InstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NotY Caption Generator AI Installer v4.2")
        self.root.geometry("750x700")
        self.root.resizable(False, False)
        
        # Set window icon and taskbar icon
        try:
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent
            
            icon_path = base_dir / "resources" / "logo.ico"
            if icon_path.exists():
                # Set both window icon and taskbar icon
                self.root.iconbitmap(str(icon_path))
                self.root.iconbitmap(default=str(icon_path))
                
                # For Windows taskbar - set after window is created
                self.root.after(100, lambda: self.root.iconbitmap(str(icon_path)))
        except Exception as e:
            print(f"Icon loading warning: {e}")
        
        # Dynamic installation path - user can choose, will append NotYCaptionGenAI
        self.install_base = tk.StringVar(value="C:\\")
        self.install_path = tk.StringVar(value="C:\\NotYCaptionGenAI")
        self.create_shortcut = tk.BooleanVar(value=True)
        self.create_desktop = tk.BooleanVar(value=True)
        self.register_sendto = tk.BooleanVar(value=True)
        
        # Store base directory for resources
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the installer UI with scrolling"""
        # Main container with scrolling
        main_canvas = tk.Canvas(self.root, highlightthickness=0, bg='white')
        main_canvas.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        main_canvas.configure(yscrollcommand=scrollbar.set, bg='white')
        
        # Frame inside canvas
        main_frame = ttk.Frame(main_canvas)
        main_canvas.create_window((0, 0), window=main_frame, anchor="nw", width=730)
        
        # Configure scrolling
        def on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        main_frame.bind("<Configure>", on_frame_configure)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Header Frame
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        # Logo
        try:
            logo_path = self.base_dir / "resources" / "logo.ico"
            if logo_path.exists():
                # Use PIL to resize if available, otherwise use as is
                logo_img = tk.PhotoImage(file=str(logo_path))
                # Resize if needed
                logo_img = logo_img.subsample(2, 2)  # Reduce size
                logo_label = ttk.Label(header_frame, image=logo_img)
                logo_label.image = logo_img
                logo_label.pack(side="left", padx=10)
        except:
            pass
        
        # Title
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
            text="Version 4.2 | Copyright © 2026 NotY215 | LGPL-3.0",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        version_label.pack(anchor="w")
        
        # Separator
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)
        
        # Installation path (user selectable, will create NotYCaptionGenAI subfolder)
        path_frame = ttk.LabelFrame(main_frame, text="Installation Location", padding=15)
        path_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(path_frame, text="Select installation folder (will create NotYCaptionGenAI subfolder):", 
                 font=("Segoe UI", 10)).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        ttk.Label(path_frame, text="Base Directory:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        base_entry = ttk.Entry(path_frame, textvariable=self.install_base, width=50)
        base_entry.grid(row=1, column=1, padx=5, pady=5)
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_install_base)
        browse_btn.grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(path_frame, text="Full installation path:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        path_display = ttk.Entry(path_frame, textvariable=self.install_path, width=50, state="readonly")
        path_display.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(path_frame, text="The application will be installed to: [Selected Path]\\NotYCaptionGenAI", 
                 font=("Segoe UI", 8), foreground="gray").grid(row=3, column=0, columnspan=3, sticky="w", padx=5, pady=2)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding=15)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Checkbutton(
            options_frame, 
            text="Create Start Menu shortcut", 
            variable=self.create_shortcut
        ).grid(row=0, column=0, sticky="w", padx=5, pady=8)
        
        ttk.Checkbutton(
            options_frame, 
            text="Create Desktop shortcut", 
            variable=self.create_desktop
        ).grid(row=1, column=0, sticky="w", padx=5, pady=8)
        
        ttk.Checkbutton(
            options_frame, 
            text="Add to 'Send To' menu (right-click any video/audio file)", 
            variable=self.register_sendto
        ).grid(row=2, column=0, sticky="w", padx=5, pady=8)
        
        # Installation info
        info_frame = ttk.LabelFrame(main_frame, text="Installation Information", padding=15)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_text = """This will install:
• NotYCaptionGenAI.exe (main application v4.2)
• Whisper.cpp binaries (speech recognition)
• FFmpeg binaries (audio processing)
• Required models (optional, will be downloaded on first use)

Total size: ~50 MB (without models)
Models will be downloaded separately when needed (75 MB to 2.9 GB)"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify="left", wraplength=670)
        info_label.pack(anchor="w")
        
        # License info
        license_frame = ttk.LabelFrame(main_frame, text="License", padding=15)
        license_frame.pack(fill="x", padx=20, pady=10)
        
        license_text = """NotY Caption Generator AI v4.2
Copyright © 2026 NotY215

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details."""
        
        license_label = ttk.Label(license_frame, text=license_text, justify="left", wraplength=670, font=("Segoe UI", 8))
        license_label.pack(anchor="w")
        
        # System Requirements
        sys_frame = ttk.LabelFrame(main_frame, text="System Requirements", padding=15)
        sys_frame.pack(fill="x", padx=20, pady=10)
        
        sys_text = """• Windows 10 or later (64-bit)
• 4 GB RAM minimum (8 GB recommended)
• 500 MB free disk space (without models)
• Internet connection for model downloads"""
        
        sys_label = ttk.Label(sys_frame, text=sys_text, justify="left", wraplength=670)
        sys_label.pack(anchor="w")
        
        # Progress bar
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress = ttk.Progressbar(self.progress_frame, mode="indeterminate", length=670)
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
        """Update full install path based on base directory"""
        base = self.install_base.get().strip()
        if base:
            # Remove trailing backslash
            base = base.rstrip('\\')
            self.install_path.set(f"{base}\\NotYCaptionGenAI")
        else:
            self.install_path.set("C:\\NotYCaptionGenAI")
        
    def browse_install_base(self):
        """Browse for base installation directory"""
        path = filedialog.askdirectory(title="Select Installation Base Directory")
        if path:
            self.install_base.set(path)
            self.update_install_path()
            
    def start_install(self):
        """Start the installation process"""
        self.update_install_path()
        self.install_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")
        threading.Thread(target=self.install, daemon=True).start()
        
    def update_status(self, message):
        """Update status label and progress bar"""
        self.status_label.config(text=message)
        self.progress.start()
        self.root.update()
        
    def install(self):
        """Perform the installation"""
        try:
            install_dir = Path(self.install_path.get())
            
            self.update_status("Creating installation directory...")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy main executable
            self.update_status("Copying main executable...")
            exe_source = self.base_dir / "NotYCaptionGenAI.exe"
            if not exe_source.exists():
                exe_source = Path(sys.executable).parent / "NotYCaptionGenAI.exe"
            
            if not exe_source.exists():
                raise Exception("Main executable not found")
            
            shutil.copy2(exe_source, install_dir / "NotYCaptionGenAI.exe")
            self.update_status("✓ Main executable copied")
            
            # Copy resources
            self.update_status("Copying resources...")
            resources_source = self.base_dir / "resources"
            if not resources_source.exists():
                resources_source = Path(sys.executable).parent / "resources"
            
            if not resources_source.exists():
                raise Exception("Resources not found")
            
            dest_resources = install_dir / "resources"
            if dest_resources.exists():
                shutil.rmtree(dest_resources)
            shutil.copytree(resources_source, dest_resources)
            self.update_status("✓ Resources copied")
            
            # Create uninstaller
            self.update_status("Creating uninstaller...")
            self.create_uninstaller(install_dir)
            self.update_status("✓ Uninstaller created")
            
            # Create shortcuts
            if self.create_shortcut.get():
                self.update_status("Creating Start Menu shortcut...")
                self.create_start_menu_shortcut(install_dir)
                self.update_status("✓ Start Menu shortcut created")
                
            if self.create_desktop.get():
                self.update_status("Creating Desktop shortcut...")
                self.create_desktop_shortcut(install_dir)
                self.update_status("✓ Desktop shortcut created")
                
            if self.register_sendto.get():
                self.update_status("Adding to Send To menu...")
                self.register_sendto_menu(install_dir)
                self.update_status("✓ Send To menu entry added")
                
            # Create registry entries
            self.update_status("Registering application...")
            self.register_application(install_dir)
            self.update_status("✓ Application registered")
            
            # Complete
            self.progress.stop()
            self.status_label.config(text="Installation complete!")
            
            messagebox.showinfo(
                "Installation Complete", 
                f"NotY Caption Generator AI v4.2 has been installed to:\n{install_dir}\n\n"
                f"✓ Start Menu shortcut: {'Created' if self.create_shortcut.get() else 'Skipped'}\n"
                f"✓ Desktop shortcut: {'Created' if self.create_desktop.get() else 'Skipped'}\n"
                f"✓ Send To menu: {'Added' if self.register_sendto.get() else 'Skipped'}\n\n"
                f"Tip: Right-click any video/audio file and select 'Send To' > 'NotYCaptionGenAi'\n\n"
                f"Copyright © 2026 NotY215 - Licensed under LGPL-3.0"
            )
            self.root.quit()
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text=f"Installation failed: {e}")
            messagebox.showerror("Installation Failed", str(e))
            self.install_btn.config(state="normal")
            self.cancel_btn.config(state="normal")
            
    def create_uninstaller(self, install_dir):
        """Create uninstaller script"""
        uninstaller_content = f'''@echo off
title NotY Caption Generator AI Uninstaller v4.2
color 0C
echo ╔═══════════════════════════════════════════╗
echo ║  NotY Caption Generator AI Uninstaller    ║
echo ║  Version 4.2 | Copyright © 2026 NotY215  ║
echo ║  Licensed under LGPL-3.0                 ║
echo ╚═══════════════════════════════════════════╝
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
echo ✅ Uninstallation complete!
echo.
pause
'''
        
        uninstaller_path = install_dir / "uninstall.bat"
        with open(uninstaller_path, "w", encoding='utf-8') as f:
            f.write(uninstaller_content)
            
    def create_shortcut_file(self, shortcut_path, target_path):
        """Create a shortcut using PowerShell"""
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
        """Create Start Menu shortcut"""
        start_menu = Path(os.environ.get("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        shortcut_path = start_menu / "NotYCaptionGenAi.lnk"
        self.create_shortcut_file(shortcut_path, install_dir / "NotYCaptionGenAI.exe")
        
    def create_desktop_shortcut(self, install_dir):
        """Create Desktop shortcut"""
        desktop = Path(os.environ.get("USERPROFILE")) / "Desktop"
        shortcut_path = desktop / "NotYCaptionGenAi.lnk"
        self.create_shortcut_file(shortcut_path, install_dir / "NotYCaptionGenAI.exe")
        
    def register_sendto_menu(self, install_dir):
        """Register to Send To menu"""
        sendto_dir = Path(os.environ.get("APPDATA")) / "Microsoft" / "Windows" / "SendTo"
        sendto_dir.mkdir(parents=True, exist_ok=True)
        shortcut_path = sendto_dir / "NotYCaptionGenAi.lnk"
        self.create_shortcut_file(shortcut_path, install_dir / "NotYCaptionGenAI.exe")
        
    def register_application(self, install_dir):
        """Register application in Windows registry"""
        reg_script = f'''
New-Item -Path "HKCU:\\Software\\NotYCaptionGenAi" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "InstallPath" -Value "{install_dir}"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "Version" -Value "4.2"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "DisplayName" -Value "NotY Caption Generator AI"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "Publisher" -Value "NotY215"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "Copyright" -Value "Copyright © 2026 NotY215"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "License" -Value "LGPL-3.0"
Set-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "URLInfoAbout" -Value "https://www.youtube.com/@NotY215"
'''
        subprocess.run(["powershell", "-Command", reg_script], capture_output=True)
        
    def run(self):
        """Run the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    installer = InstallerGUI()
    installer.run()