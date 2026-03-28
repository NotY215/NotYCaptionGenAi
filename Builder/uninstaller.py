#!/usr/bin/env python3
"""
NotY Caption Generator AI Uninstaller
"""

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading

class UninstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NotY Caption Generator AI Uninstaller")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # Set window icon
        try:
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent
            
            icon_path = base_dir / "resources" / "logo.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
                self.root.iconbitmap(default=str(icon_path))
        except:
            pass
        
        # Get install path from registry
        self.install_path = self.get_install_path()
        
        self.setup_ui()
        
    def get_install_path(self):
        """Get install path from registry"""
        try:
            ps_script = '''
$path = Get-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "InstallPath" -ErrorAction SilentlyContinue
if ($path) { Write-Output $path.InstallPath }
'''
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            if result.stdout.strip():
                return Path(result.stdout.strip())
        except:
            pass
        return None
        
    def setup_ui(self):
        """Setup the uninstaller UI with scrolling"""
        # Main container with scrolling
        main_canvas = tk.Canvas(self.root, highlightthickness=0)
        main_canvas.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame inside canvas
        main_frame = ttk.Frame(main_canvas)
        main_canvas.create_window((0, 0), window=main_frame, anchor="nw", width=580)
        
        # Configure scrolling
        def on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        main_frame.bind("<Configure>", on_frame_configure)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        # Logo
        try:
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent
            logo_path = base_dir / "resources" / "logo.ico"
            if logo_path.exists():
                logo_img = tk.PhotoImage(file=str(logo_path))
                logo_label = ttk.Label(header_frame, image=logo_img)
                logo_label.image = logo_img
                logo_label.pack(side="left", padx=10)
        except:
            pass
        
        title_label = ttk.Label(
            header_frame,
            text="NotY Caption Generator AI Uninstaller",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)
        
        # Warning
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ Warning", padding=15)
        warning_frame.pack(fill="x", padx=20, pady=10)
        
        warning_text = "This will completely remove NotY Caption Generator AI and all its components from your computer."
        ttk.Label(warning_frame, text=warning_text, wraplength=540, font=("Segoe UI", 10)).pack()
        
        # Installation info
        info_frame = ttk.LabelFrame(main_frame, text="Installation Information", padding=15)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        if self.install_path and self.install_path.exists():
            ttk.Label(info_frame, text=f"Installation Directory: {self.install_path}", font=("Segoe UI", 10)).pack(anchor="w", pady=5)
            ttk.Label(info_frame, text=f"Size: {self.get_folder_size(self.install_path)}", font=("Segoe UI", 9), foreground="gray").pack(anchor="w")
        else:
            ttk.Label(info_frame, text="Installation directory not found in registry.", font=("Segoe UI", 10)).pack(anchor="w")
        
        # Components to remove
        components_frame = ttk.LabelFrame(main_frame, text="Components to Remove", padding=15)
        components_frame.pack(fill="x", padx=20, pady=10)
        
        components = [
            "• Application files and resources",
            "• Start Menu shortcut",
            "• Desktop shortcut",
            "• Send To menu entry",
            "• Registry entries"
        ]
        
        for comp in components:
            ttk.Label(components_frame, text=comp).pack(anchor="w", pady=2)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", length=540)
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(main_frame, text="Ready to uninstall", anchor="center")
        self.status_label.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        self.uninstall_btn = ttk.Button(button_frame, text="Uninstall", command=self.start_uninstall, width=15)
        self.uninstall_btn.pack(side="right", padx=5)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.root.quit, width=15)
        self.cancel_btn.pack(side="right", padx=5)
        
    def get_folder_size(self, folder):
        """Get folder size in human readable format"""
        total = 0
        try:
            for path in folder.rglob('*'):
                if path.is_file():
                    total += path.stat().st_size
        except:
            pass
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total < 1024.0:
                return f"{total:.1f} {unit}"
            total /= 1024.0
        return f"{total:.1f} TB"
        
    def start_uninstall(self):
        """Start uninstallation"""
        self.uninstall_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")
        threading.Thread(target=self.uninstall, daemon=True).start()
        
    def update_status(self, message):
        """Update status"""
        self.status_label.config(text=message)
        self.progress.start()
        self.root.update()
        
    def uninstall(self):
        """Perform uninstallation"""
        try:
            # Remove installation directory
            if self.install_path and self.install_path.exists():
                self.update_status("Removing application files...")
                shutil.rmtree(self.install_path)
                self.update_status("✓ Application files removed")
                
            # Remove shortcuts
            self.update_status("Removing shortcuts...")
            start_menu = Path(os.environ.get("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAi.lnk"
            desktop = Path(os.environ.get("USERPROFILE")) / "Desktop" / "NotYCaptionGenAi.lnk"
            sendto = Path(os.environ.get("APPDATA")) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAi.lnk"
            
            for shortcut in [start_menu, desktop, sendto]:
                if shortcut.exists():
                    shortcut.unlink()
            self.update_status("✓ Shortcuts removed")
                    
            # Remove registry entries
            self.update_status("Removing registry entries...")
            reg_script = 'Remove-Item -Path "HKCU:\\Software\\NotYCaptionGenAi" -Recurse -Force -ErrorAction SilentlyContinue'
            subprocess.run(["powershell", "-Command", reg_script], capture_output=True)
            self.update_status("✓ Registry entries removed")
            
            # Complete
            self.progress.stop()
            self.status_label.config(text="Uninstallation complete!")
            
            messagebox.showinfo("Uninstall Complete", "NotY Caption Generator AI has been uninstalled successfully!")
            self.root.quit()
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text=f"Uninstallation failed: {e}")
            messagebox.showerror("Uninstall Failed", f"Error during uninstallation: {e}")
            self.uninstall_btn.config(state="normal")
            self.cancel_btn.config(state="normal")

if __name__ == "__main__":
    uninstaller = UninstallerGUI()
    uninstaller.run()