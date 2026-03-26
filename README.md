<p align="center">
  <img src="https://raw.githubusercontent.com/NotY215/NotYCaptionGenAi/main/resources/app.ico" alt="NotYCaptionGenAi Logo" width="128">
</p>

<h1 align="center">🎬 NotYCaptionGenAi</h1>
<p align="center">
  <strong>AI-Powered Subtitle Generator with Whisper Integration</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Java-11+-orange.svg" alt="Java Version">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-LGPL%20v3-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Version-2.0.0-brightgreen.svg" alt="Version">
  <img src="https://img.shields.io/badge/Download-EXE-success.svg" alt="Download">
</p>

---

## 📋 Overview

**NotYCaptionGenAi** is a powerful desktop application that automatically generates subtitles/captions for video and audio files using OpenAI's Whisper AI model. It supports multiple media formats, provides intelligent line breaking, and offers advanced transliteration support for Hindi, Japanese, and other non-Latin scripts.

### ✨ Features

- 🎥 **Multi-format Support**: MP4, MKV, AVI, WMV, MPEG, MP3, WAV, M4A, FLAC
- 🤖 **AI-Powered**: Uses OpenAI Whisper for accurate transcription
- 📦 **Multiple Models**: Choose from Tiny (39MB) to Large V1 (2.9GB) models
- 🌐 **Multi-language**: Supports all languages with Whisper's language detection
- 🔄 **Advanced Transliteration**: Convert Hindi, Japanese, Arabic, Chinese, Korean, and Russian to English
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
   - Enable transliteration for non-English scripts

4. **Generate Subtitles**
   - Click "Generate Subtitles"
   - Confirm settings in dialog
   - Wait for processing (progress shown in status bar)
   - SRT file saved in the same folder as your media

5. **Output Files**
   - `[filename].srt` - Standard subtitles
   - `[filename]_translit.srt` - Transliterated version (if enabled)

---

## 🔤 Transliteration Feature

The application provides advanced transliteration for multiple languages:

### Supported Scripts

| Language | Script | Example Input | Transliterated Output |
|----------|--------|---------------|----------------------|
| **Hindi** | Devanagari | नमस्ते दुनिया | Namaste Duniya |
| **Japanese** | Hiragana/Katakana | こんにちは世界 | Konnichiwa Sekai |
| **Arabic** | Arabic Script | مرحبا بالعالم | Marhaban Bilalim |
| **Chinese** | Simplified/Traditional | 你好世界 | Ni Hao Shi Jie |
| **Korean** | Hangul | 안녕하세요 세계 | Annyeonghaseyo Segye |
| **Russian** | Cyrillic | Здравствуй мир | Zdravstvuy mir |

### How Transliteration Works

1. **Detection**: The system automatically detects non-Latin scripts
2. **Mapping**: Each character is mapped to its closest Latin equivalent
3. **Context**: Special character combinations are handled intelligently
4. **Preservation**: Numbers, punctuation, and Latin text remain unchanged

### Example Output

**Original Subtitle (Hindi):**
```bash
1
00:00:01,000 --> 00:00:04,000
नमस्ते, यह एक परीक्षण है
```

**Transliterated Output:**
```bash
1
00:00:01,000 --> 00:00:04,000
Namaste, yah ek parikshan hai
```

---

## 🎯 Model Comparison

| Model | Size | Speed | Accuracy | RAM Required | Best For |
|-------|------|-------|----------|--------------|----------|
| Tiny | 39 MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | 1 GB | Quick previews, short clips |
| Base | 142 MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | 2 GB | General use, balanced |
| Small | 466 MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | 3 GB | Higher quality needs |
| Medium | 1.5 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | 5 GB | Professional use |
| Large V1 | 2.9 GB | ⚡ | ⭐⭐⭐⭐⭐ | 8 GB | Maximum accuracy |

---

## 📦 Model Download Links

If you prefer to download models manually:

| Model | File Name | Download Link | Size |
|-------|-----------|---------------|------|
| Tiny | ggml-tiny.bin | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin | 39 MB |
| Base | ggml-base.bin | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin | 142 MB |
| Small | ggml-small.bin | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin | 466 MB |
| Medium | ggml-medium.bin | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin | 1.5 GB |
| Large V1 | ggml-large-v1.bin | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin | 2.9 GB |

**Place downloaded models in the same folder as the EXE.**

---

## 🎯 Supported Formats

| Type | Formats | Extensions |
|------|---------|------------|
| **Video** | MP4, MKV, AVI, WMV, MPEG | .mp4, .mkv, .avi, .wmv, .mpeg |
| **Audio** | MP3, WAV, M4A, FLAC | .mp3, .wav, .m4a, .flac |

---

## ⚙️ System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **RAM**: 2GB minimum (for Tiny/Base models)
- **Storage**: 500MB for application + model size
- **CPU**: Any modern processor with SSE2 support
- **Internet**: Required for model download

### Recommended Requirements
- **RAM**:
   - 4GB for Small/Medium models
   - 8GB for Large V1 model
- **Storage**: 4GB free space
- **CPU**: Multi-core processor (for faster transcription)
- **Internet**: High-speed connection for model downloads

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
├── ggml-tiny.bin # Downloaded model file (or other model)
├── ffmpeg.exe # Embedded FFmpeg (Windows)
├── ffprobe.exe # Embedded FFprobe (Windows)
├── whisper-jni.dll # Whisper JNI native library
└── [Your files].srt # Generated subtitles
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

**Q: Model download fails?**
- ✅ Check internet connection
- ✅ Ensure sufficient disk space (model size + 10%)
- ✅ Try downloading model manually from links above
- ✅ Check firewall/antivirus isn't blocking
- ✅ Restart application and try again

**Q: Download is slow?**
- ✅ Model files are hosted on Hugging Face
- ✅ Download speed depends on your internet connection
- ✅ You can cancel and try again later
- ✅ Try downloading during off-peak hours

**Q: FFmpeg not found?**
- ✅ Application includes embedded FFmpeg
- ✅ If issues persist, download FFmpeg from https://ffmpeg.org
- ✅ Place ffmpeg.exe in the same folder as the application

**Q: Slow transcription?**
- ✅ Larger models take more time
- ✅ Use Tiny or Base for faster processing
- ✅ Ensure enough RAM for the selected model
- ✅ Close other applications to free up resources

**Q: Out of memory error?**
- ✅ Use a smaller model (Tiny or Base)
- ✅ Close other applications
- ✅ Run with more memory if using JAR version
- ✅ Upgrade RAM for Large V1 model

**Q: Subtitles not accurate?**
- ✅ Ensure clear audio quality
- ✅ Select correct language manually
- ✅ Try a larger model (Medium or Large V1)
- ✅ Check audio has no background noise
- ✅ Ensure audio isn't too low volume

**Q: Transliteration not working?**
- ✅ Ensure "Transliterate" checkbox is checked
- ✅ Check if text contains supported scripts
- ✅ Works for Hindi, Japanese, Arabic, Chinese, Korean, Russian
- ✅ English text remains unchanged

**Q: Application crashes during generation?**
- ✅ Close other memory-intensive applications
- ✅ Use smaller model
- ✅ Ensure enough disk space for temporary files
- ✅ Update Java to latest version

---

## 📝 Version History

### v2.0.0 (Current - 2024)
- ✅ Multiple model support (Tiny to Large V1)
- ✅ Enhanced download manager with speed/size display
- ✅ Cancel button for downloads
- ✅ Button locking during operations
- ✅ Confirmation dialogs before downloads/generation
- ✅ Real Whisper JNI integration structure
- ✅ Improved UI with model information
- ✅ Better error handling
- ✅ Advanced transliteration for 6+ languages
- ✅ LGPL v3 License

### v1.0.0
- Initial release
- Single model support
- Basic download functionality
- Basic transliteration for Hindi/Japanese

---

## 📄 License

This project is licensed under the **GNU Lesser General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### LGPL v3 Summary

The GNU Lesser General Public License (LGPL) is a free software license published by the Free Software Foundation (FSF). It allows developers and companies to use and integrate software covered by the LGPL into their own (even proprietary) software without being required to release the source code of their own components. However, any modifications to LGPL-covered software must be released under the LGPL.

**Key Points:**
- ✅ You can use this software commercially
- ✅ You can modify the source code
- ✅ You must disclose source code for modifications
- ✅ You must include copyright notice
- ✅ You must state changes made
- ✅ You must include license text
- ✅ You cannot hold authors liable

For the full license text, visit: https://www.gnu.org/licenses/lgpl-3.0.en.html

---

## 👨‍💻 Credits

- **Developed By**: NotY215
- **AI Model**: OpenAI Whisper
- **Model Format**: Whisper.cpp by ggerganov
- **Media Processing**: FFmpeg
- **UI Framework**: Java Swing
- **Transliteration Engine**: Custom implementation with Unicode mapping

---

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/NotY215/NotYCaptionGenAi/issues)
- **Email**: noty215@protonmail.com
- **Discord**: [Join our community](https://discord.gg/noty215)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

### Ways to Contribute
- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🌍 Add translations
- 🔧 Submit code improvements

---

## 🙏 Acknowledgments

- OpenAI for the Whisper model and research
- ggerganov for Whisper.cpp implementation
- FFmpeg team for media processing tools
- All open-source contributors
- Java community for Swing framework

---

## 📊 Statistics

<p align="center">
  <img src="https://img.shields.io/github/stars/NotY215/NotYCaptionGenAi?style=social" alt="Stars">
  <img src="https://img.shields.io/github/forks/NotY215/NotYCaptionGenAi?style=social" alt="Forks">
  <img src="https://img.shields.io/github/downloads/NotY215/NotYCaptionGenAi/total" alt="Downloads">
  <img src="https://img.shields.io/github/issues/NotY215/NotYCaptionGenAi" alt="Issues">
</p>

---

<p align="center">
  <b>Made with ❤️ by NotY215</b>
  <br>
  <sub>Copyright © 2024 NotY215. All rights reserved.</sub>
  <br>
  <sub>This software is provided under the GNU Lesser General Public License v3.0</sub>
</p>

---

## 🔗 Quick Links

- [Download Latest Release](https://github.com/NotY215/NotYCaptionGenAi/releases/latest)
- [Report an Issue](https://github.com/NotY215/NotYCaptionGenAi/issues)
- [Feature Request](https://github.com/NotY215/NotYCaptionGenAi/issues/new)
- [License Information](LICENSE)
- [Model Download Links](#-model-download-links)
- [Troubleshooting Guide](#-troubleshooting)