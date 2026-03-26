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
  <img src="https://img.shields.io/badge/Version-2.0.0-brightgreen.svg" alt="Version">
</p>

---

## 📋 Overview

**NotYCaptionGenAi** is a powerful desktop application that automatically generates subtitles/captions for video and audio files using OpenAI's Whisper AI model. It supports multiple media formats, provides intelligent line breaking, and offers transliteration support for Hindi and Japanese languages.

### ✨ Features

- 🎥 **Multi-format Support**: MP4, MKV, AVI, WMV, MPEG, MP3, WAV, M4A, FLAC
- 🤖 **AI-Powered**: Uses OpenAI Whisper for accurate transcription
- 📦 **Multiple Models**: Choose from Tiny (39MB) to Large V1 (2.9GB) models
- 🌐 **Multi-language**: Supports all languages with Whisper's language detection
- 🔄 **Transliteration**: Convert Hindi and Japanese text to English
- 📝 **Smart Line Breaking**: Adjustable maximum letters per line
- 💾 **SRT Format**: Standard subtitle format compatible with all media players
- 🚀 **Easy to Use**: Simple GUI with drag-and-drop functionality
- 📊 **Download Manager**: Progress tracking with speed and size information
- 🛡️ **Safe Operations**: Disables buttons during downloads/generation to prevent crashes

---

## 🚀 Quick Start

### Download

**Download the latest EXE from:**  
🔗 **[https://github.com/NotY215/NotYCaptionGenAi/releases](https://github.com/NotY215/NotYCaptionGenAi/releases)**

No building required! Just download and run.

### Installation

1. **Download the EXE**: Get the latest `NotYCaptionGenAi.exe` from the releases page
2. **Run the Application**: Double-click to launch - no installation required!
3. **First-time Setup**:
   - Select a Whisper model from the dropdown (Tiny is fastest, Large V1 is most accurate)
   - Click "Download Selected Model"
   - Wait for download to complete (progress shown with speed and ETA)

### Usage Guide

1. **Select Media File**
   - Click "Select Video/Audio File"
   - Choose any supported media file

2. **Choose Model**
   - **Tiny (39 MB)**: Fastest, good for simple content
   - **Base (142 MB)**: Balanced speed and accuracy
   - **Small (466 MB)**: Better accuracy
   - **Medium (1.5 GB)**: High accuracy
   - **Large V1 (2.9 GB)**: Best accuracy, slower processing

3. **Configure Settings**
   - Adjust max letters per line (20-80 characters)
   - Select language (or use auto-detect)
   - Enable transliteration for Hindi/Japanese

4. **Generate Subtitles**
   - Click "Generate Subtitles"
   - Confirm settings in dialog
   - Wait for processing (progress shown in status bar)
   - SRT file saved in the same folder as your media

5. **Output Files**
   - `[filename].srt` - Standard subtitles
   - `[filename]_translit.srt` - Transliterated version (if enabled)

---

## 🎯 Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| Tiny | 39 MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Quick previews, short clips |
| Base | 142 MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | General use, balanced |
| Small | 466 MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Higher quality needs |
| Medium | 1.5 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Professional use |
| Large V1 | 2.9 GB | ⚡ | ⭐⭐⭐⭐⭐ | Maximum accuracy |

---

## 📦 Model Download Links

If you prefer to download models manually:

| Model | File Name | Download Link | Size |
|-------|-----------|---------------|------|
| Tiny | ggml-tiny.bin | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin) | 39 MB |
| Base | ggml-base.bin | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin) | 142 MB |
| Small | ggml-small.bin | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin) | 466 MB |
| Medium | ggml-medium.bin | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin) | 1.5 GB |
| Large V1 | ggml-large-v1.bin | [Download](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin) | 2.9 GB |

Place downloaded models in the same folder as the EXE.

---

## 🎯 Supported Formats

| Type | Formats |
|------|---------|
| **Video** | MP4, MKV, AVI, WMV, MPEG |
| **Audio** | MP3, WAV, M4A, FLAC |

---

## ⚙️ System Requirements

- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **RAM**:
   - 2GB minimum (for Tiny/Base models)
   - 4GB recommended (for Small/Medium models)
   - 8GB recommended (for Large V1 model)
- **Storage**:
   - 500MB for application
   - + Model size (39 MB to 2.9 GB)
- **CPU**: Any modern processor with SSE2 support
- **Internet**: Required for model download

---

## 🛠️ Technical Details

### How It Works

1. **Audio Extraction**: FFmpeg extracts audio from video files (converted to 16kHz WAV)
2. **AI Transcription**: Selected Whisper model processes audio with high accuracy
3. **Subtitle Generation**: Creates SRT format with precise timestamps
4. **Post-processing**: Applies letter spacing and transliteration

### File Structure
```bash
NotYCaptionGenAi.exe
├── ggml-tiny.bin # Downloaded model file
├── ggml-base.bin # (or other model)
├── ffmpeg.exe # Embedded FFmpeg (Windows)
├── ffprobe.exe # Embedded FFprobe (Windows)
└── [Your files].srt # Generated subtitles
```


---

## 🔧 Troubleshooting

### Common Issues

**Q: Model download fails?**
- Check internet connection
- Ensure sufficient disk space (model size + 10%)
- Try downloading model manually from links above
- Check firewall/antivirus isn't blocking

**Q: Download is slow?**
- Model files are hosted on Hugging Face
- Download speed depends on your internet connection
- You can cancel and try again later

**Q: FFmpeg not found?**
- Application includes embedded FFmpeg
- If issues persist, download FFmpeg from https://ffmpeg.org

**Q: Slow transcription?**
- Larger models take more time
- Use Tiny or Base for faster processing
- Ensure enough RAM for the selected model

**Q: Out of memory error?**
- Use a smaller model (Tiny or Base)
- Close other applications
- Run with more memory: `java -Xmx4G -jar NotYCaptionGenAi.jar`

**Q: Subtitles not accurate?**
- Ensure clear audio quality
- Select correct language manually
- Try a larger model (Medium or Large V1)
- Check audio has no background noise

---

## 📝 Version History

### v2.0.0 (Current)
- ✅ Multiple model support (Tiny to Large V1)
- ✅ Enhanced download manager with speed/size display
- ✅ Cancel button for downloads
- ✅ Button locking during operations
- ✅ Confirmation dialogs before downloads/generation
- ✅ Real Whisper JNI integration structure
- ✅ Improved UI with model information
- ✅ Better error handling

### v1.0.0
- Initial release
- Single model support
- Basic download functionality

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

### Development Setup

```bash
# Clone repository
git clone https://github.com/NotY215/NotYCaptionGenAi.git

# Build with Maven
mvn clean package

# Run application
java -jar target/NotYCaptionGenAi-2.0.0-jar-with-dependencies.jar