<p align="center">
  <img src="resources/app.ico" alt="NotYCaptionGenAi Logo" width="128">
</p>

<h1 align="center">🎬 NotYCaptionGenAi</h1>
<p align="center">
  <strong>AI-Powered Subtitle Generator with Whisper Integration</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Java-11+-orange.svg" alt="Java Version">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Version-1.0.0-brightgreen.svg" alt="Version">
</p>

---

## 📋 Overview

**NotYCaptionGenAi** is a powerful desktop application that automatically generates subtitles/captions for video and audio files using OpenAI's Whisper AI model. It supports multiple media formats, provides intelligent line breaking, and offers transliteration support for Hindi and Japanese languages.

### ✨ Features

- 🎥 **Multi-format Support**: MP4, MKV, AVI, WMV, MPEG, MP3, WAV, M4A, FLAC
- 🤖 **AI-Powered**: Uses OpenAI Whisper for accurate transcription
- 🌐 **Multi-language**: Supports all languages with Whisper's language detection
- 🔄 **Transliteration**: Convert Hindi and Japanese text to English
- 📝 **Smart Line Breaking**: Adjustable maximum letters per line
- 💾 **SRT Format**: Standard subtitle format compatible with all media players
- 🚀 **Easy to Use**: Simple GUI with drag-and-drop functionality
- 📦 **Self-contained**: Includes FFmpeg - no external dependencies needed

---

## 🚀 Quick Start

### Installation

1. **Download the EXE**: Get the latest `NotYCaptionGenAi.exe` from the releases page
2. **Run the Application**: Double-click to launch - no installation required!
3. **First-time Setup**: If the Whisper model isn't present, click "Download Model" to get it

### Usage Guide

1. **Select Media File**
    - Click "Select Video/Audio File"
    - Choose any supported media file

2. **Configure Settings**
    - Adjust max letters per line (20-80 characters)
    - Select language (or use auto-detect)
    - Enable transliteration for Hindi/Japanese

3. **Generate Subtitles**
    - Click "Generate Subtitles"
    - Wait for processing (progress shown in status bar)
    - SRT file saved in the same folder as your media

4. **Output Files**
    - `[filename].srt` - Standard subtitles
    - `[filename]_translit.srt` - Transliterated version (if enabled)

---

## 🎯 Supported Formats

| Type | Formats |
|------|---------|
| **Video** | MP4, MKV, AVI, WMV, MPEG |
| **Audio** | MP3, WAV, M4A, FLAC |

---

## ⚙️ System Requirements

- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 500MB for application + 1.5GB for Whisper model
- **CPU**: Any modern processor (SSE2 support required)

---

## 🛠️ Technical Details

### How It Works

1. **Audio Extraction**: FFmpeg extracts audio from video files (converted to 16kHz WAV)
2. **AI Transcription**: Whisper model processes audio with high accuracy
3. **Subtitle Generation**: Creates SRT format with precise timestamps
4. **Post-processing**: Applies letter spacing and transliteration

### File Structure

```bash
NotYCaptionGenAi.exe
├── ggml-base.bin # Whisper model (downloaded on first use)
├── ffmpeg.exe # Embedded FFmpeg (Windows)
├── ffprobe.exe # Embedded FFprobe (Windows)
└── [Your files].srt # Generated subtitles
```

---

## 🌟 Advanced Features

### Letter Spacing Control
- Adjust from 20 to 80 characters per line
- Intelligently breaks at word boundaries
- Maintains subtitle readability

### Language Support
- **Auto-detect**: Whisper automatically identifies the language
- **Manual selection**: Choose from 9+ languages
- **Transliteration**: Hindi and Japanese to English conversion

### Model Management
- One-click model download
- Automatic model verification
- Progress indicator during download

---

## ❓ Troubleshooting

### Common Issues

**Q: Model download fails?**
- Check internet connection
- Ensure sufficient disk space (1.5GB)
- Try restarting the application

**Q: FFmpeg not found?**
- Application includes embedded FFmpeg
- If issues persist, install FFmpeg system-wide

**Q: Slow transcription?**
- First run downloads the model
- Subsequent runs are faster
- Use smaller files for quicker processing

**Q: Subtitles not accurate?**
- Ensure clear audio quality
- Select correct language manually
- Try different media file

---

## 🔧 Building from Source

For developers who want to build from source:

```bash
# Clone repository
git clone https://github.com/NotY215/NotYCaptionGenAi.git

# Build with Maven
mvn clean package

# Run application
java -jar target/NotYCaptionGenAi-1.0.0-jar-with-dependencies.jar