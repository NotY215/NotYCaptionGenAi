<p align="center">
  <img src="https://raw.githubusercontent.com/NotY215/NotYCaptionGenAi/main/resources/app.ico" alt="NotYCaptionGenAi Logo" width="128">
</p>

<h1 align="center">🎬 NotYCaptionGenAi v3.0</h1>
<p align="center">
  <strong>AI-Powered Subtitle Generator with Whisper Integration</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-LGPL%20v3-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Version-3.0.0-brightgreen.svg" alt="Version">
  <img src="https://img.shields.io/badge/Download-EXE-success.svg" alt="Download">
  <img src="https://img.shields.io/badge/No%20Java%20Required-Yes-brightgreen.svg" alt="No Java Required">
</p>

---

## 📋 Overview

**NotYCaptionGenAi** is a powerful desktop application that automatically generates subtitles/captions for video and audio files using OpenAI's Whisper AI model. Version 3.0 features a stunning Topaz-like dark UI, embedded Java runtime, maximize/restore functionality, and improved vocal extraction.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎥 **Multi-format Support** | MP4, MKV, AVI, WMV, MPEG, MP3, WAV, M4A, FLAC |
| 🤖 **AI-Powered** | Uses OpenAI Whisper for accurate transcription |
| 📦 **Multiple Models** | Tiny (39MB) to Large V1 (2.9GB) |
| 🌐 **Multi-language** | Supports 10+ languages with auto-detection |
| 🔄 **Transliteration** | Hindi, Japanese, Arabic, Chinese, Korean, Russian → English |
| 📝 **Smart Line Breaking** | Adjustable letters per line (20-80) |
| 💾 **SRT Format** | Universal subtitle format |
| 🚀 **No Java Required** | Embedded JRE in EXE |
| 🎨 **Modern UI** | Dark theme, glowing buttons, custom window controls |

---

## 📥 Download

### Latest Release
🔗 **[Download NotYCaptionGenAi.exe](https://github.com/NotY215/NotYCaptionGenAi/releases/latest/download/NotYCaptionGenAi.exe)**

**Requirements:**
- Windows 10 or Windows 11 (64-bit)
- 2GB RAM minimum (8GB recommended for Large model)
- 500MB - 3.5GB free disk space (depending on model)

**No Java installation needed!** Everything is included.

---

## 🚀 Quick Start Guide

### 1️⃣ Download & Run
- Download `NotYCaptionGenAi.exe` from the link above
- Double-click to run (no installation required)
- Allow through Windows Defender if prompted

### 2️⃣ First-Time Setup
1. **Select a Whisper Model** from the dropdown:
   - **Tiny (39 MB)** - Fastest, for quick previews
   - **Base (142 MB)** - Balanced speed/accuracy
   - **Small (466 MB)** - Better accuracy
   - **Medium (1.5 GB)** - High accuracy
   - **Large V1 (2.9 GB)** - Maximum accuracy

2. **Click "Download Selected Model"** 
   - Progress shows: percentage, downloaded size, speed
   - Wait for download to complete

### 3️⃣ Generate Subtitles
1. **Click "Select Video/Audio File"**
2. **Choose your media file** (MP4, MP3, AVI, etc.)
3. **Adjust settings:**
   - Max letters per line (20-80 characters)
   - Select language (or Auto Detect)
   - Enable Transliteration (for Hindi/Japanese/etc.)
4. **Click "Generate Subtitles"**
5. **Confirm** the settings in the dialog

### 4️⃣ Find Your Subtitles
- SRT file saved in the **same folder** as your media file
- `[filename].srt` - Standard subtitles
- `[filename]_translit.srt` - Transliterated version (if enabled)

---

## 🎯 Model Comparison

| Model | Size | Speed | Accuracy | RAM | Best For |
|-------|------|-------|----------|-----|----------|
| Tiny | 39 MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | 1 GB | Quick previews, short clips |
| Base | 142 MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | 2 GB | General use, balanced |
| Small | 466 MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | 3 GB | Higher quality needs |
| Medium | 1.5 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | 5 GB | Professional use |
| Large V1 | 2.9 GB | ⚡ | ⭐⭐⭐⭐⭐ | 8 GB | Maximum accuracy |

---

## 🎨 UI Features

### Modern Dark Theme
- **Gradient backgrounds** for depth
- **Glowing button animations** during activity
- **Rounded cards** with subtle borders
- **Vibrant accent colors** for actions

### Custom Window Controls
- **Minimize** → Send to taskbar
- **Maximize/Restore** → Toggle fullscreen
- **Close** → Exit application
- **Drag Title Bar** → Move window

### Status Indicators
- Real-time progress updates
- Color-coded messages (✅ green, ⚠️ orange, ❌ red, 🔵 blue)
- Loading animations during processing

---

## 📦 Model Download Links

Download models manually if needed (place in same folder as EXE):

| Model | File Name | Download Link | Size |
|-------|-----------|---------------|------|
| Tiny | `ggml-tiny.bin` | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin) | 39 MB |
| Base | `ggml-base.bin` | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin) | 142 MB |
| Small | `ggml-small.bin` | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin) | 466 MB |
| Medium | `ggml-medium.bin` | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin) | 1.5 GB |
| Large V1 | `ggml-large-v1.bin` | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin) | 2.9 GB |

---

## 🔧 Supported Formats

| Type | Formats | Extensions |
|------|---------|------------|
| **Video** | MP4, MKV, AVI, WMV, MPEG | `.mp4` `.mkv` `.avi` `.wmv` `.mpeg` |
| **Audio** | MP3, WAV, M4A, FLAC | `.mp3` `.wav` `.m4a` `.flac` |

---

## ⚙️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 (64-bit) | Windows 11 |
| **RAM** | 2 GB | 8 GB |
| **Storage** | 500 MB + model size | 4 GB SSD |
| **CPU** | Any modern processor | Multi-core processor |
| **Internet** | Required for model download | High-speed connection |

---

## 🔍 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Application won't start** | • Ensure all files are in same folder<br>• Check antivirus isn't blocking<br>• Run as administrator |
| **Model download fails** | • Check internet connection<br>• Ensure 3+ GB free disk space<br>• Try manual download from links above |
| **Download is slow** | • Model files are large (up to 2.9GB)<br>• Try downloading during off-peak hours<br>• Use wired internet connection |
| **No subtitles generated** | • Check audio is clear (not too quiet)<br>• Try a different model<br>• Select correct language manually |
| **Out of memory error** | • Use Tiny or Base model<br>• Close other applications<br>• Upgrade RAM for Large model |
| **Window won't move** | • Click and drag from title bar area<br>• Maximize then restore first |
| **Transliteration not working** | • Ensure checkbox is checked<br>• Only works for supported scripts |

---

## 📝 Version History

### v3.0.0 (Current - 2026)
- ✅ **Topaz-like dark UI** with gradient backgrounds
- ✅ **Custom window controls** (minimize, maximize, restore, close)
- ✅ **Embedded Java runtime** - no Java installation required
- ✅ **Enhanced vocal extraction** from audio
- ✅ **Proper icon support** (window + taskbar)
- ✅ **Glowing button animations**
- ✅ **Window dragging support**
- ✅ **Improved memory management**
- ✅ **Better error handling with user-friendly messages**

### v2.0.0
- Multiple model support (Tiny to Large V1)
- Download manager with speed display
- Button locking during operations

### v1.0.0
- Initial release with basic functionality

---

## 📄 License

This project is licensed under the **GNU Lesser General Public License v3.0**.

**Key Permissions:**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ Must disclose source for modifications
- ⚠️ Must include copyright notice
- ⚠️ Must include license text

For the full license text, visit: [https://www.gnu.org/licenses/lgpl-3.0.en.html](https://www.gnu.org/licenses/lgpl-3.0.en.html)

---

## 👨‍💻 Credits

| Component | Credit |
|-----------|--------|
| **Development** | NotY215 |
| **AI Model** | OpenAI Whisper |
| **Model Format** | [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) by ggerganov |
| **Media Processing** | [FFmpeg](https://ffmpeg.org) |
| **UI Framework** | Java Swing |
| **EXE Wrapper** | [Launch4j](http://launch4j.sourceforge.net) |

---

## 📞 Support & Links

| Resource | Link |
|----------|------|
| **Download Latest EXE** | [GitHub Releases](https://github.com/NotY215/NotYCaptionGenAi/releases) |
| **Report Issues** | [GitHub Issues](https://github.com/NotY215/NotYCaptionGenAi/issues) |
| **Feature Requests** | [Submit Request](https://github.com/NotY215/NotYCaptionGenAi/issues/new) |
| **Email** | noty215@protonmail.com |

---

## 📊 Statistics

<p align="center">
  <img src="https://img.shields.io/github/stars/NotY215/NotYCaptionGenAi?style=social" alt="Stars">
  <img src="https://img.shields.io/github/forks/NotY215/NotYCaptionGenAi?style=social" alt="Forks">
  <img src="https://img.shields.io/github/downloads/NotY215/NotYCaptionGenAi/total" alt="Downloads">
  <img src="https://img.shields.io/github/v/release/NotY215/NotYCaptionGenAi" alt="Latest Release">
</p>

---

<p align="center">
  <b>🎬 NotYCaptionGenAi v3.0</b><br>
  <i>AI-Powered Subtitle Generation Made Simple</i><br><br>
  <b>Made with ❤️ by NotY215</b><br>
  <sub>Copyright © 2026 NotY215. All rights reserved.</sub><br>
  <sub>Licensed under GNU Lesser General Public License v3.0</sub><br><br>
  <sub>⭐ If you find this useful, please star the repository on GitHub! ⭐</sub>
</p>