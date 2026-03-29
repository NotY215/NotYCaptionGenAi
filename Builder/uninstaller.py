#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotY Caption Generator AI Uninstaller v4.3
Copyright (c) 2026 NotY215
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
        self.root.title("NotY Caption Generator AI Uninstaller v4.3")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        self.install_path = self.get_install_path()
        self.setup_ui()
        
    def get_install_path(self):
        try:
            ps = 'Get-ItemProperty -Path "HKCU:\\Software\\NotYCaptionGenAi" -Name "InstallPath" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty InstallPath'
            result = subprocess.run(["powershell", "-Command", ps], capture_output=True, text=True)
            if result.stdout.strip():
                return Path(result.stdout.strip())
        except:
            pass
        return None
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        title_label = ttk.Label(
            main_frame,
            text="NotY Caption Generator AI Uninstaller",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        version_label = ttk.Label(
            main_frame,
            text="Version 4.3 | Copyright (c) 2026 NotY215",
            font=("Segoe UI", 9)
        )
        version_label.pack(pady=(0, 20))
        
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ Warning", padding=10)
        warning_frame.pack(fill="x", pady=10)
        
        warning_text = "This will completely remove NotY Caption Generator AI and all its components from your computer."
        ttk.Label(warning_frame, text=warning_text, wraplength=450).pack()
        
        info_frame = ttk.LabelFrame(main_frame, text="Installation Information", padding=10)
        info_frame.pack(fill="x", pady=10)
        
        if self.install_path and self.install_path.exists():
            ttk.Label(info_frame, text=f"Installation Directory: {self.install_path}").pack(anchor="w", pady=5)
        else:
            ttk.Label(info_frame, text="Installation directory not found in registry.").pack(anchor="w", pady=5)
        
        components_frame = ttk.LabelFrame(main_frame, text="Components to Remove", padding=10)
        components_frame.pack(fill="x", pady=10)
        
        components = [
            "• Application files and resources",
            "• Start Menu shortcut",
            "• Desktop shortcut",
            "• Send To menu entry",
            "• Registry entries"
        ]
        for comp in components:
            ttk.Label(components_frame, text=comp).pack(anchor="w", pady=2)
        
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate", length=450)
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(main_frame, text="Ready to uninstall")
        self.status_label.pack(pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.uninstall_btn = ttk.Button(button_frame, text="Uninstall", command=self.start_uninstall, width=15)
        self.uninstall_btn.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Cancel", command=self.root.quit, width=15).pack(side="left", padx=5)
        
    def start_uninstall(self):
        self.uninstall_btn.config(state="disabled")
        threading.Thread(target=self.uninstall, daemon=True).start()
        
    def update_status(self, message):
        self.status_label.config(text=message)
        self.progress.start()
        self.root.update()
        
    def uninstall(self):
        try:
            if self.install_path and self.install_path.exists():
                self.update_status("Removing application files...")
                shutil.rmtree(self.install_path)
                
            self.update_status("Removing shortcuts...")
            shortcuts = [
                Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "NotYCaptionGenAi.lnk",
                Path(os.environ["USERPROFILE"]) / "Desktop" / "NotYCaptionGenAi.lnk",
                Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "SendTo" / "NotYCaptionGenAi.lnk"
            ]
            for shortcut in shortcuts:
                if shortcut.exists():
                    shortcut.unlink()
                    
            self.update_status("Removing registry entries...")
            subprocess.run(["powershell", "-Command", 'Remove-Item -Path "HKCU:\\Software\\NotYCaptionGenAi" -Recurse -Force -ErrorAction SilentlyContinue'], capture_output=True)
            
            self.progress.stop()
            self.status_label.config(text="Uninstallation complete!")
            messagebox.showinfo("Uninstall Complete", "NotY Caption Generator AI has been uninstalled successfully!")
            
            # Self-delete
            self.root.quit()
            time.sleep(1)
            if getattr(sys, 'frozen', False):
                os.remove(sys.executable)
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text=f"Uninstallation failed: {e}")
            messagebox.showerror("Uninstall Failed", str(e))
            self.uninstall_btn.config(state="normal")

if __name__ == "__main__":
    uninstaller = UninstallerGUI()
    uninstaller.run()