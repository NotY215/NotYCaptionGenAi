#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NotY Caption Generator AI v7.1 - Graphical Version
Professional AI-powered subtitle generator using OpenAI Whisper
Copyright (c) 2026 NotY215
"""

import sys
import os
import signal
import subprocess
import tempfile
import shutil
import json
import base64
import hashlib
import time
import threading
import re
from datetime import timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QSpinBox, QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QLineEdit, QScrollArea, QSlider, QProgressBar, QDialog, QFormLayout,
    QSizePolicy, QStyleFactory, QDesktopWidget, QGroupBox, QRadioButton,
    QFrame, QSpacerItem, QCheckBox, QTabWidget, QSplitter
)
from PyQt5.QtGui import QIcon, QColor, QTextCursor, QFont, QPalette, QCloseEvent
from PyQt5.QtCore import Qt, QUrl, QCoreApplication, QDir, pyqtSignal, QThread, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Third-party imports
import whisper
import torch
from moviepy.editor import VideoFileClip
import pysrt
import pysubs2

# ============================================================================
# Constants and Configuration
# ============================================================================
APP_NAME = "NotY Caption Generator AI"
APP_VERSION = "7.1"
APP_AUTHOR = "NotY215"
APP_YEAR = "2026"
APP_LICENSE = "LGPL-3.0"
APP_TELEGRAM = "https://t.me/Noty_215"
APP_YOUTUBE = "https://www.youtube.com/@NotY215"

# Language tiers
LANGUAGE_TIERS = {
    "high": {
        "name": "High Accuracy (90-95%)",
        "languages": [
            ("English", "en"), ("Spanish", "es"), ("Italian", "it"),
            ("Portuguese", "pt"), ("German", "de"), ("Japanese", "ja"),
            ("French", "fr"), ("Catalan", "ca")
        ]
    },
    "medium": {
        "name": "Medium Accuracy (70-85%)",
        "languages": [
            ("Swedish", "sv"), ("Russian", "ru"), ("Polish", "pl"), ("Dutch", "nl")
        ]
    },
    "low": {
        "name": "Lower Accuracy (50-70%)",
        "languages": [
            ("Hindi", "hi"), ("Tamil", "ta"), ("Telugu", "te"), ("Punjabi", "pa"),
            ("Bengali", "bn"), ("Urdu", "ur"), ("Marathi", "mr"), ("Gujarati", "gu"),
            ("Kannada", "kn"), ("Malayalam", "ml")
        ]
    }
}

# Whisper models
WHISPER_MODELS = [
    ("tiny", "75 MB", "Fastest"), ("base", "150 MB", "Balanced"),
    ("small", "500 MB", "Good"), ("medium", "1.5 GB", "Accurate"),
    ("large", "2.9 GB", "Best")
]

# Vocal separation options
VOCAL_OPTIONS = [
    ("No vocal separation", "none", "Fastest"),
    ("2 Stems (Fast)", "2stems", "Vocals + Accompaniment"),
    ("4 Stems (Better)", "4stems", "Vocals + Drums + Bass + Other"),
    ("5 Stems (Best)", "5stems", "Vocals + Drums + Bass + Piano + Other")
]

SUPPORTED_EXTENSIONS = {
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.m4v', '.mpg', '.mpeg', '.webm'],
    'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'],
}

# ============================================================================
# Worker Thread for Transcription
# ============================================================================
class TranscriptionWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, audio_path: str, model_name: str, language: str, mode: str,
                 vocal_separation: str, ffmpeg_exe: str = None):
        super().__init__()
        self.audio_path = audio_path
        self.model_name = model_name
        self.language = language
        self.mode = mode
        self.vocal_separation = vocal_separation
        self.ffmpeg_exe = ffmpeg_exe
        self._is_cancelled = False
        
    def cancel(self):
        self._is_cancelled = True
        
    def run(self):
        try:
            # Load model
            self.progress.emit(10, f"Loading {self.model_name} model...")
            model = whisper.load_model(self.model_name)
            
            # Apply vocal separation if needed
            audio_path = self.audio_path
            if self.vocal_separation != "none":
                self.progress.emit(25, f"Applying vocal separation ({self.vocal_separation})...")
                # For now, use FFmpeg for vocal separation
                if self.ffmpeg_exe and os.path.exists(self.ffmpeg_exe):
                    vocal_path = self._separate_vocals_ffmpeg(audio_path)
                    if vocal_path:
                        audio_path = vocal_path
            
            # Transcribe
            self.progress.emit(50, "Transcribing...")
            task = "translate" if self.mode == "translate" else "transcribe"
            lang = None if self.language == "auto" else self.language
            
            result = model.transcribe(
                audio_path, language=lang, task=task, verbose=False,
                word_timestamps=True, fp16=False
            )
            
            # Clean up temporary vocal file
            if audio_path != self.audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except:
                    pass
            
            self.progress.emit(90, "Processing results...")
            
            if self._is_cancelled:
                self.error.emit("Cancelled by user")
                return
                
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _separate_vocals_ffmpeg(self, audio_path: str) -> Optional[str]:
        """Separate vocals using FFmpeg"""
        temp_dir = tempfile.gettempdir()
        vocal_path = os.path.join(temp_dir, f"vocals_{int(time.time())}.wav")
        
        cmd = [
            self.ffmpeg_exe, '-i', audio_path,
            '-af', 'highpass=f=100, lowpass=f=10000, volume=2.0',
            '-y', vocal_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, timeout=180)
            if os.path.exists(vocal_path) and os.path.getsize(vocal_path) > 0:
                return vocal_path
        except:
            pass
        return None

# ============================================================================
# Settings Dialog
# ============================================================================
class SettingsDialog(QDialog):
    settingsChanged = pyqtSignal(dict)
    
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(300, 200, 500, 450)
        self.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Preferences")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Theme
        theme_group = QGroupBox("Appearance")
        theme_group.setStyleSheet("QGroupBox { color: #a0a0ff; font-weight: bold; border: 1px solid #444; border-radius: 6px; padding: 10px; }")
        theme_layout = QVBoxLayout()
        theme_group.setLayout(theme_layout)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System Default"])
        self.theme_combo.setCurrentText(current_settings.get("theme", "Dark"))
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme_combo)
        layout.addWidget(theme_group)
        
        layout.addSpacing(15)
        
        # Model directory
        model_group = QGroupBox("Model Settings")
        model_group.setStyleSheet("QGroupBox { color: #a0a0ff; font-weight: bold; border: 1px solid #444; border-radius: 6px; padding: 10px; }")
        model_layout = QVBoxLayout()
        model_group.setLayout(model_layout)
        
        model_dir_layout = QHBoxLayout()
        self.model_dir_line = QLineEdit(current_settings.get("models_dir", ""))
        self.model_dir_browse = QPushButton("Browse")
        self.model_dir_browse.clicked.connect(self.browse_models_dir)
        model_dir_layout.addWidget(QLabel("Models Folder:"))
        model_dir_layout.addWidget(self.model_dir_line)
        model_dir_layout.addWidget(self.model_dir_browse)
        model_layout.addLayout(model_dir_layout)
        
        layout.addWidget(model_group)
        
        layout.addSpacing(15)
        
        # Temp directory
        temp_group = QGroupBox("Temporary Files")
        temp_group.setStyleSheet("QGroupBox { color: #a0a0ff; font-weight: bold; border: 1px solid #444; border-radius: 6px; padding: 10px; }")
        temp_layout = QVBoxLayout()
        temp_group.setLayout(temp_layout)
        
        temp_dir_layout = QHBoxLayout()
        self.temp_dir_line = QLineEdit(current_settings.get("temp_dir", tempfile.gettempdir()))
        self.temp_dir_browse = QPushButton("Browse")
        self.temp_dir_browse.clicked.connect(self.browse_temp_dir)
        temp_dir_layout.addWidget(QLabel("Temp Folder:"))
        temp_dir_layout.addWidget(self.temp_dir_line)
        temp_dir_layout.addWidget(self.temp_dir_browse)
        temp_layout.addLayout(temp_dir_layout)
        
        layout.addWidget(temp_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("background-color: #0a84ff; color: white; padding: 8px; border-radius: 6px;")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #3c3c3c; color: white; padding: 8px; border-radius: 6px;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def browse_models_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Models Folder")
        if folder:
            self.model_dir_line.setText(folder)
    
    def browse_temp_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Temporary Files Folder")
        if folder:
            self.temp_dir_line.setText(folder)
    
    def save_settings(self):
        settings = {
            "theme": self.theme_combo.currentText(),
            "models_dir": self.model_dir_line.text(),
            "temp_dir": self.temp_dir_line.text(),
        }
        self.settingsChanged.emit(settings)
        self.accept()

# ============================================================================
# Main Window
# ============================================================================
class NotyCaptionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setWindowIcon(QIcon('App.ico') if os.path.exists('App.ico') else QIcon())
        self.setGeometry(100, 100, 1200, 800)
        
        # Settings
        self.settings = {
            "theme": "Dark",
            "models_dir": "",
            "temp_dir": tempfile.gettempdir()
        }
        
        # State variables
        self.input_file = None
        self.audio_file = None
        self.output_folder = None
        self.subtitles = []
        self.player = QMediaPlayer()
        self.worker = None
        self.current_media_path = None
        self.captions_generated = False
        self.duration = 0
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
        # Timer for slider update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slider)
        self.timer.start(100)
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Caption Editor
        left_panel = QWidget()
        left_panel.setMinimumWidth(500)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # Caption editor title
        editor_title = QLabel("Caption Editor")
        editor_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        left_layout.addWidget(editor_title)
        
        # Caption text edit
        self.caption_edit = QTextEdit()
        self.caption_edit.setReadOnly(True)
        self.caption_edit.setFont(QFont("Consolas", 12))
        self.caption_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        left_layout.addWidget(self.caption_edit, 1)
        
        # Edit button
        self.edit_btn = QPushButton("Edit Captions")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setMinimumHeight(40)
        left_layout.addWidget(self.edit_btn)
        
        # Right panel - Controls
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_panel.setMinimumWidth(350)
        right_panel.setStyleSheet("QScrollArea { border: none; }")
        
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()
        controls_widget.setLayout(controls_layout)
        
        # File selection
        file_group = QGroupBox("File Selection")
        file_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        file_layout = QVBoxLayout()
        file_group.setLayout(file_layout)
        
        self.import_btn = QPushButton("Import Media File")
        self.import_btn.setMinimumHeight(50)
        self.import_btn.setStyleSheet("background-color: #0a84ff; color: white; font-size: 14px; border-radius: 8px;")
        file_layout.addWidget(self.import_btn)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        file_layout.addWidget(self.file_label)
        
        controls_layout.addWidget(file_group)
        
        # Model selection
        model_group = QGroupBox("Whisper Model")
        model_layout = QVBoxLayout()
        model_group.setLayout(model_layout)
        
        self.model_combo = QComboBox()
        for name, size, desc in WHISPER_MODELS:
            self.model_combo.addItem(f"{name.upper()} ({size}) - {desc}")
        model_layout.addWidget(self.model_combo)
        
        controls_layout.addWidget(model_group)
        
        # Language selection
        lang_group = QGroupBox("Language")
        lang_layout = QVBoxLayout()
        lang_group.setLayout(lang_layout)
        
        self.lang_tier_combo = QComboBox()
        self.lang_tier_combo.addItems(["High Accuracy (90-95%)", "Medium Accuracy (70-85%)", "Lower Accuracy (50-70%)"])
        lang_layout.addWidget(self.lang_tier_combo)
        
        self.lang_combo = QComboBox()
        self.update_language_list()
        self.lang_tier_combo.currentTextChanged.connect(self.update_language_list)
        lang_layout.addWidget(self.lang_combo)
        
        controls_layout.addWidget(lang_group)
        
        # Mode selection
        mode_group = QGroupBox("Mode")
        mode_layout = QVBoxLayout()
        mode_group.setLayout(mode_layout)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Normal Mode (Transcribe)", "Translate Mode (Translate to English)"])
        mode_layout.addWidget(self.mode_combo)
        
        controls_layout.addWidget(mode_group)
        
        # Vocal separation
        vocal_group = QGroupBox("Vocal Separation")
        vocal_layout = QVBoxLayout()
        vocal_group.setLayout(vocal_layout)
        
        self.vocal_combo = QComboBox()
        for name, key, desc in VOCAL_OPTIONS:
            self.vocal_combo.addItem(f"{name} - {desc}")
        vocal_layout.addWidget(self.vocal_combo)
        
        controls_layout.addWidget(vocal_group)
        
        # Line break settings
        line_group = QGroupBox("Line Break Settings")
        line_layout = QVBoxLayout()
        line_group.setLayout(line_layout)
        
        self.line_type_combo = QComboBox()
        self.line_type_combo.addItems(["Auto (Recommended)", "Words", "Letters"])
        line_layout.addWidget(self.line_type_combo)
        
        line_limit_layout = QHBoxLayout()
        line_limit_layout.addWidget(QLabel("Limit:"))
        self.line_limit_spin = QSpinBox()
        self.line_limit_spin.setRange(1, 50)
        self.line_limit_spin.setValue(5)
        line_limit_layout.addWidget(self.line_limit_spin)
        line_layout.addLayout(line_limit_layout)
        
        controls_layout.addWidget(line_group)
        
        # Output format
        format_group = QGroupBox("Output Format")
        format_layout = QVBoxLayout()
        format_group.setLayout(format_layout)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["SRT (.srt)", "ASS (.ass)"])
        format_layout.addWidget(self.format_combo)
        
        controls_layout.addWidget(format_group)
        
        # Output folder
        output_group = QGroupBox("Output Location")
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)
        
        output_folder_layout = QHBoxLayout()
        self.output_folder_line = QLineEdit()
        self.output_folder_line.setReadOnly(True)
        output_folder_layout.addWidget(self.output_folder_line)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.select_output_folder)
        output_folder_layout.addWidget(self.browse_btn)
        output_layout.addLayout(output_folder_layout)
        
        controls_layout.addWidget(output_group)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Captions")
        self.generate_btn.setMinimumHeight(60)
        self.generate_btn.setStyleSheet("background-color: #ff2d55; color: white; font-size: 16px; font-weight: bold; border-radius: 10px;")
        controls_layout.addWidget(self.generate_btn)
        
        # Progress bars
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        controls_layout.addWidget(progress_group)
        
        # Media controls
        media_group = QGroupBox("Media Controls")
        media_layout = QVBoxLayout()
        media_group.setLayout(media_layout)
        
        self.play_btn = QPushButton("Play")
        self.play_btn.setEnabled(False)
        self.play_btn.clicked.connect(self.toggle_play)
        media_layout.addWidget(self.play_btn)
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setEnabled(False)
        self.timeline_slider.sliderMoved.connect(self.seek_audio)
        media_layout.addWidget(self.timeline_slider)
        
        controls_layout.addWidget(media_group)
        
        # Settings button
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        controls_layout.addWidget(self.settings_btn)
        
        # About button
        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.show_about)
        controls_layout.addWidget(about_btn)
        
        controls_layout.addStretch()
        
        right_panel.setWidget(controls_widget)
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.import_btn.clicked.connect(self.import_file)
        self.generate_btn.clicked.connect(self.generate_captions)
        self.edit_btn.clicked.connect(self.toggle_edit)
        self.player.positionChanged.connect(self.update_highlight)
        self.player.durationChanged.connect(self.set_duration)
        self.player.error.connect(self.on_player_error)
    
    def update_language_list(self):
        """Update language list based on selected tier"""
        self.lang_combo.clear()
        tier_text = self.lang_tier_combo.currentText()
        if "High" in tier_text:
            tier = "high"
        elif "Medium" in tier_text:
            tier = "medium"
        else:
            tier = "low"
        
        for name, code in LANGUAGE_TIERS[tier]["languages"]:
            self.lang_combo.addItem(f"{name} ({code})", code)
    
    def apply_theme(self):
        """Apply the selected theme"""
        theme = self.settings.get("theme", "Dark")
        if theme == "Light":
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            self.setPalette(palette)
        else:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(45, 45, 45))
            palette.setColor(QPalette.Text, Qt.white)
            self.setPalette(palette)
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.settings, self)
        dialog.settingsChanged.connect(self.on_settings_changed)
        dialog.exec_()
    
    def on_settings_changed(self, settings):
        self.settings = settings
        self.apply_theme()
    
    def import_file(self):
        """Import media file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Media File", "",
            "Media Files (*.mp4 *.avi *.mkv *.mov *.mp3 *.wav *.m4a *.flac);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        self.input_file = file_path
        self.file_label.setText(os.path.basename(file_path))
        
        # Set output folder to same as input file
        self.output_folder = os.path.dirname(file_path)
        self.output_folder_line.setText(self.output_folder)
        
        # Extract audio from video
        if file_path.lower().endswith(tuple(SUPPORTED_EXTENSIONS['video'])):
            self.status_label.setText("Extracting audio from video...")
            QApplication.processEvents()
            
            temp_dir = self.settings.get("temp_dir", tempfile.gettempdir())
            temp_audio = os.path.join(temp_dir, f"{os.path.basename(file_path)}.temp.wav")
            
            try:
                video = VideoFileClip(file_path)
                video.audio.write_audiofile(temp_audio, codec='pcm_s16le', verbose=False, logger=None)
                video.close()
                self.audio_file = temp_audio
                self.status_label.setText("Audio extracted successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to extract audio: {str(e)}")
                self.audio_file = file_path
        else:
            self.audio_file = file_path
        
        # Setup media player
        self.current_media_path = None
        self.play_btn.setEnabled(True)
        self.timeline_slider.setEnabled(True)
        
        QMessageBox.information(self, "Success", f"File imported successfully:\n{os.path.basename(file_path)}")
    
    def select_output_folder(self):
        """Select output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder or "")
        if folder:
            self.output_folder = folder
            self.output_folder_line.setText(folder)
    
    def generate_captions(self):
        """Generate captions using Whisper"""
        if not self.audio_file or not os.path.exists(self.audio_file):
            QMessageBox.warning(self, "Error", "Please import a media file first.")
            return
        
        # Get settings
        model_idx = self.model_combo.currentIndex()
        model_name = WHISPER_MODELS[model_idx][0]
        
        language_code = self.lang_combo.currentData()
        mode = "translate" if "Translate" in self.mode_combo.currentText() else "transcribe"
        
        vocal_idx = self.vocal_combo.currentIndex()
        vocal_separation = VOCAL_OPTIONS[vocal_idx][1]
        
        # Start worker thread
        self.generate_btn.setEnabled(False)
        self.import_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting...")
        
        self.worker = TranscriptionWorker(
            self.audio_file, model_name, language_code, mode, vocal_separation,
            str(Path(__file__).parent / "ffmpeg" / "ffmpeg.exe") if os.path.exists(Path(__file__).parent / "ffmpeg") else None
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_transcription_finished)
        self.worker.error.connect(self.on_transcription_error)
        self.worker.start()
    
    def update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        QApplication.processEvents()
    
    def on_transcription_finished(self, result):
        """Handle transcription completion"""
        self.progress_bar.setValue(100)
        self.status_label.setText("Processing results...")
        QApplication.processEvents()
        
        try:
            # Process segments into subtitles
            self.subtitles = []
            index = 1
            words_per_line = self.line_limit_spin.value()
            line_type = self.line_type_combo.currentText()
            
            for segment in result.get("segments", []):
                text = segment.get("text", "").strip()
                if not text:
                    continue
                
                start = segment.get("start", 0)
                end = segment.get("end", start + 1)
                
                # Split text based on line type
                if line_type == "Words":
                    words = text.split()
                    for i in range(0, len(words), words_per_line):
                        chunk = ' '.join(words[i:i+words_per_line])
                        chunk_end = start + (end - start) * min(i + words_per_line, len(words)) / len(words)
                        self.subtitles.append({
                            "index": index,
                            "start": timedelta(seconds=start + i * (end - start) / len(words)),
                            "end": timedelta(seconds=chunk_end),
                            "text": chunk
                        })
                        index += 1
                else:
                    # Auto or Letters
                    self.subtitles.append({
                        "index": index,
                        "start": timedelta(seconds=start),
                        "end": timedelta(seconds=end),
                        "text": text
                    })
                    index += 1
            
            # Update caption editor
            caption_text = ""
            for sub in self.subtitles:
                caption_text += f"{sub['index']}\n{sub['text']}\n\n"
            self.caption_edit.setText(caption_text.strip())
            
            # Save to file
            output_format = self.format_combo.currentText()
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(self.output_folder or os.path.dirname(self.input_file), f"{base_name}_captions")
            
            if output_format == "SRT (.srt)":
                output_file += ".srt"
                subs = pysrt.SubRipFile()
                for sub in self.subtitles:
                    item = pysrt.SubRipItem(
                        index=sub["index"],
                        start=pysrt.SubRipTime.from_ordinal(sub["start"].total_seconds() * 1000),
                        end=pysrt.SubRipTime.from_ordinal(sub["end"].total_seconds() * 1000),
                        text=sub["text"]
                    )
                    subs.append(item)
                subs.save(output_file, encoding='utf-8')
            else:
                output_file += ".ass"
                subs = pysubs2.SSAFile()
                for sub in self.subtitles:
                    event = pysubs2.SSAEvent(
                        start=int(sub["start"].total_seconds() * 1000),
                        end=int(sub["end"].total_seconds() * 1000),
                        text=sub["text"]
                    )
                    subs.events.append(event)
                subs.save(output_file)
            
            self.captions_generated = True
            self.edit_btn.setEnabled(True)
            self.status_label.setText(f"Captions saved to {os.path.basename(output_file)}")
            
            QMessageBox.information(self, "Success", f"Captions generated successfully!\nSaved to: {output_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process transcription: {str(e)}")
            self.status_label.setText("Error processing transcription")
        
        finally:
            self.generate_btn.setEnabled(True)
            self.import_btn.setEnabled(True)
    
    def on_transcription_error(self, error_msg):
        """Handle transcription error"""
        self.generate_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.status_label.setText("Error occurred")
        QMessageBox.critical(self, "Error", f"Transcription failed:\n{error_msg}")
    
    def toggle_edit(self):
        """Toggle edit mode for captions"""
        if not self.captions_generated:
            return
        
        if self.caption_edit.isReadOnly():
            self.caption_edit.setReadOnly(False)
            self.edit_btn.setText("Save Changes")
            self.status_label.setText("Edit mode - modify captions as needed")
        else:
            # Save changes
            self.caption_edit.setReadOnly(True)
            self.edit_btn.setText("Edit Captions")
            self.update_subtitles_from_text()
            self.status_label.setText("Changes saved")
    
    def update_subtitles_from_text(self):
        """Update subtitles from edited text"""
        text = self.caption_edit.toPlainText().strip()
        blocks = text.split('\n\n')
        new_subtitles = []
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 2 and lines[0].strip().isdigit():
                try:
                    idx = int(lines[0].strip())
                    sub_text = '\n'.join(lines[1:]).strip()
                    for sub in self.subtitles:
                        if sub["index"] == idx:
                            sub["text"] = sub_text
                            new_subtitles.append(sub)
                            break
                except:
                    pass
        
        self.subtitles = new_subtitles
        QMessageBox.information(self, "Success", "Captions updated successfully")
    
    def toggle_play(self):
        """Toggle media playback"""
        if not self.audio_file or not os.path.exists(self.audio_file):
            return
        
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_btn.setText("Play")
        else:
            try:
                if self.current_media_path != self.audio_file:
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file)))
                    self.current_media_path = self.audio_file
                self.player.play()
                self.play_btn.setText("Pause")
            except Exception as e:
                QMessageBox.warning(self, "Playback Error", str(e))
    
    def set_duration(self, duration):
        """Set media duration"""
        self.duration = duration
        self.timeline_slider.setRange(0, duration)
    
    def update_slider(self):
        """Update timeline slider position"""
        if self.duration > 0:
            pos = self.player.position()
            self.timeline_slider.setValue(pos)
    
    def seek_audio(self, position):
        """Seek to position in audio"""
        self.player.setPosition(position)
    
    def update_highlight(self, position):
        """Highlight current subtitle during playback"""
        if not self.subtitles or not self.captions_generated:
            return
        
        current_time = position / 1000.0
        
        # Find current subtitle
        for sub in self.subtitles:
            start = sub["start"].total_seconds()
            end = sub["end"].total_seconds()
            if start <= current_time < end:
                # Highlight in text edit
                text = self.caption_edit.toPlainText()
                cursor = self.caption_edit.textCursor()
                cursor.movePosition(QTextCursor.Start)
                
                # Find the block containing this subtitle
                blocks = text.split('\n\n')
                block_idx = sub["index"] - 1
                if 0 <= block_idx < len(blocks):
                    block_start = sum(len(b) + 2 for b in blocks[:block_idx])
                    cursor.setPosition(block_start)
                    cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor, len(blocks[block_idx].split('\n')))
                    
                    # Set highlight
                    format = cursor.charFormat()
                    format.setBackground(QColor(255, 200, 0))
                    cursor.setCharFormat(format)
                    
                    self.caption_edit.setTextCursor(cursor)
                    self.caption_edit.ensureCursorVisible()
                break
    
    def on_player_error(self, error):
        """Handle player errors"""
        QMessageBox.warning(self, "Media Error", f"Cannot play media:\n{self.player.errorString()}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", f"""
            <h2>{APP_NAME} v{APP_VERSION}</h2>
            <p>Professional AI-powered subtitle generator using OpenAI Whisper</p>
            <br/>
            <b>Features:</b><br/>
            • YouTube video download and captioning<br/>
            • Local video/audio file processing<br/>
            • Vocal separation with FFmpeg<br/>
            • 20+ languages with accuracy tiers<br/>
            • Smart subtitle formatting<br/>
            • Real-time playback with highlighting<br/>
            <br/>
            <b>Author:</b> {APP_AUTHOR}<br/>
            <b>License:</b> {APP_LICENSE}<br/>
            <br/>
            <b>Support:</b><br/>
            Telegram: <a href="{APP_TELEGRAM}">{APP_TELEGRAM}</a><br/>
            YouTube: <a href="{APP_YOUTUBE}">{APP_YOUTUBE}</a>
        """)
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event - cleanup all processes"""
        # Cancel any running worker
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.quit()
            self.worker.wait(2000)
        
        # Stop media player
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()
        
        # Clean up temporary audio file
        if self.audio_file and self.audio_file.endswith(".temp.wav") and os.path.exists(self.audio_file):
            try:
                os.remove(self.audio_file)
            except:
                pass
        
        # Clean up any remaining temp files
        temp_dir = self.settings.get("temp_dir", tempfile.gettempdir())
        for file in os.listdir(temp_dir):
            if file.startswith("vocals_") and file.endswith(".wav"):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except:
                    pass
        
        event.accept()

# ============================================================================
# Main Entry Point
# ============================================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application icon
    if os.path.exists('App.ico'):
        app.setWindowIcon(QIcon('App.ico'))
    
    window = NotyCaptionWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()