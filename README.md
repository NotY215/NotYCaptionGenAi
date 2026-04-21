# 🎬 NotY Caption Generator AI v7.1

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-green.svg)](https://python.org)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://microsoft.com)
[![Version](https://img.shields.io/badge/Version-7.1-red.svg)](https://github.com/NotY215/NotYCaptionGenAi)

A powerful command-line AI tool that generates professional subtitles/captions for videos and audio files using OpenAI's Whisper, with advanced vocal separation using Spleeter, YouTube download support, and smart subtitle formatting.

## 📋 Table of Contents

- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Quick Installation](#-quick-installation)
- [What's New in v7.1](#-whats-new-in-v71)
- [How to Use](#-how-to-use)
- [Project Structure](#-project-structure)
- [Build from Source](#-build-from-source)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Performance](#-performance)
- [Support](#-support)
- [License](./LICENSE)

## ✨ Features

### Core Functionality
- 🎯 **AI-Powered Transcription** - Uses OpenAI Whisper for high accuracy with word-level timestamps
- 🎤 **Professional Vocal Separation** - Spleeter integration (2/4/5 stems) with local models support
- 📺 **YouTube Support** - Download and caption any YouTube video
- 🌍 **Multi-Language** - 7 languages + Auto Detect (English, Hindi, Japanese, Spanish, Korean, Chinese, Russian)
- 🔄 **Translation Mode** - Transcribe and translate to English simultaneously
- 📝 **Smart Subtitle Formatting** - Word/Character/Auto line breaks with intelligent sentence detection
- ⚡ **Audio Chunking** - Automatic 10-second chunk processing for better performance

### Technical Improvements (v7.1)
- 🚀 **60-70% Faster Startup** - Nuitka compiled executable
- 📦 **Modular Architecture** - Clean separation of core, utils, and UI modules
- 🗑️ **Automatic Cache Cleanup** - No leftover files on exit
- 🔧 **Enhanced Text Cleaning** - Removes hallucinations and repeated words
- 💾 **Reduced Memory Usage** - 25% less RAM consumption

## 📋 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10 (64-bit) | Windows 11 (64-bit) |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 5 GB free space | 10 GB free space |
| **CPU** | Any modern processor | Intel i5/AMD Ryzen 5+ |
| **GPU** | Not required | NVIDIA GPU (optional) |

## 🚀 Quick Installation

### Option 1: Installer (Recommended)
Download `NotYCaptionGenAI_Installer_v7.1.exe` and run:
```cmd
NotYCaptionGenAI_Installer_v7.1.exe
```

The installer will:
- Install to `C:\NotYCaptionGenAI`
- Copy all models (Whisper + Spleeter)
- Create Desktop and Start Menu shortcuts
- Add to Windows "Send To" menu
- Register in Add/Remove Programs

### Option 2: Portable
Download `NotYCaptionGenAI_Portable_v7.1.zip` and extract anywhere.

## 🆕 What's New in v7.1

### Major Changes
```
✨ COMPLETE MODULAR ARCHITECTURE REWRITE
   • Codebase restructured into clean module hierarchy
   • Separation of concerns: core, utils, UI modules
   • Better maintainability and scalability

✨ DUAL BUILD SYSTEM IMPLEMENTED
   • Nuitka for faster executable startup (60-70% faster)
   • PyInstaller for reliable installer creation
   • _packages_ folder for bundled dependencies

✨ AUDIO CHUNKING SYSTEM
   • Automatic audio splitting into 10-second chunks
   • 1-second overlap between chunks for seamless transcription
   • Intelligent merging of chunk results
```

### Fixed Issues
```
🐛 RESOLVED
   ✓ TensorFlow initialization errors
   ✓ Spleeter 'multiprocess_count' parameter error
   ✓ Repeated word hallucination (e.g., "अपने अपने अपने")
   ✓ Cache folder not deleting on application close
   ✓ _vocals suffix removed from output filenames
   ✓ Language auto-detection in Normal mode
   ✓ Import error with Colors class
```

## 🎮 How to Use

### Method 1: Run from Start Menu
Click **Start** → **NotY Caption Generator AI**

### Method 2: Right-click any file
Right-click any video/audio file → **Send To** → **NotYCaptionGenAi**

### Method 3: Command Line
```cmd
NotYCaptionGenAI.exe "C:\path\to\video.mp4"
```

### Interactive Menu Flow
```
1. Choose platform: YouTube or Local File
2. Select vocal separation (none/2stems/4stems/5stems)
3. Choose Whisper model (tiny/base/small/medium/large)
4. Select mode: Normal or Translate
5. Pick language (or Auto Detect)
6. Choose line break type (Auto/Words/Letters)
7. Generate captions!
```

## 📁 Project Structure

```
NotYCaptionGenAi/
├── noty_caption_gen.py          # Main entry point
├── requirements.txt              # Dependencies (locked versions)
├── README.md                     # This file
├── LICENSE                       # LGPL-3.0
│
├── Builder/                      # Build system
│   ├── build_nuitka.py          # Nuitka build script (FAST)
│   ├── build_installer.py       # PyInstaller installer builder
│   └── setup.py                 # Complete build orchestrator
│
├── src/                          # Modular source code
│   ├── core/                    # Core functionality
│   │   ├── transcriber.py       # Whisper transcription
│   │   ├── vocal_separator.py   # Spleeter/FFmpeg separation
│   │   ├── audio_processor.py   # Audio extraction & chunking
│   │   └── subtitle_generator.py # SRT generation
│   ├── utils/                   # Utilities
│   │   ├── colors.py            # ANSI color codes
│   │   ├── cleanup.py           # Temp file cleanup
│   │   ├── cache_manager.py     # Database caching
│   │   └── file_handlers.py     # File dialogs
│   └── ui/                      # User interface
│       └── menu.py              # Console menu system
│
├── _packages_/                   # Bundled dependencies (created by installer)
│
├── ffmpeg/                       # FFmpeg binaries
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
│
├── models/                       # Whisper model files
│   ├── tiny.pt                   # 75 MB - Fastest
│   ├── base.pt                   # 150 MB - Balanced
│   └── small.pt                  # 500 MB - Good
│
├── pretrained_models/            # Spleeter models
│   └── 5stems/                   # 5-stem separation model
│       ├── checkpoint
│       ├── model.data-00000-of-00001
│       ├── model.index
│       └── model.meta
│
└── resources/                    # Icons & assets
    ├── app.ico
    └── logo.ico
```

## 📦 Included Models

### Whisper Models (Speech Recognition)
| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 75 MB | Fastest | Good | Quick previews |
| base | 150 MB | Fast | Better | General use |
| small | 500 MB | Normal | High | Recommended |
| medium | 1.5 GB | Slow | Very High | Professional |
| large | 2.9 GB | Very Slow | Best | Maximum accuracy |

### Spleeter Models (Vocal Separation)
| Model | Components | Speed | Use Case |
|-------|------------|-------|----------|
| 2stems | Vocals + Accompaniment | Fast | Music with lyrics |
| 4stems | Vocals + Drums + Bass + Other | Medium | Detailed separation |
| 5stems | Vocals + Drums + Bass + Piano + Other | Slow | Studio quality |

## 🛠️ Build from Source

### Prerequisites
```bash
# Python 3.10 (required for TensorFlow/Spleeter)
python --version  # Should be 3.10.x

# Install build tools
pip install nuitka pyinstaller

# Install dependencies
pip install -r requirements.txt
```

### Build Commands
```bash
# Complete build (executable + installer)
python Builder/setup.py

# Build only executable with Nuitka (faster)
python Builder/build_nuitka.py

# Build only installer (requires executable)
python Builder/build_installer.py
```

### Build Output
| File | Size | Description |
|------|------|-------------|
| `NotYCaptionGenAI.exe` | ~100 MB | Nuitka compiled executable |
| `NotYCaptionGenAI_Installer_v7.1.exe` | ~1 GB | Windows installer |
| `NotYCaptionGenAI_Portable_v7.1.zip` | ~700 MB | Portable version |

## ⚙️ Configuration

### Supported File Formats
| Type | Extensions |
|------|------------|
| Video | `.mp4`, `.avi`, `.mkv`, `.mov`, `.m4v`, `.mpg`, `.mpeg`, `.webm` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac` |

### Language Codes
| Language | Code | ISO |
|----------|------|-----|
| English | en | en |
| Hindi | hi | hi |
| Japanese | ja | ja |
| Spanish | es | es |
| Korean | ko | ko |
| Chinese | zh | zh |
| Russian | ru | ru |
| Auto Detect | auto | auto |

### Environment Variables
```cmd
# Optional performance tuning
set OMP_NUM_THREADS=4
set TF_CPP_MIN_LOG_LEVEL=2
```

## 📊 Performance Metrics

### Speed Comparison (v6.1 vs v7.1)
| Metric | v6.1 | v7.1 | Improvement |
|--------|------|------|-------------|
| App Startup | 3-5 sec | 1-2 sec | **60-70% faster** |
| Memory Usage | ~800 MB | ~600 MB | **25% reduction** |
| Audio Processing | 1x | 1.5x | **50% faster** |
| Text Cleanup | Basic | Advanced | **Better accuracy** |

### Model Performance (per minute of audio)
| Model | Processing Time(Approximate) | RAM Usage |
|-------|----------------|-----------|
| tiny | 30 sec | 200 MB |
| base | 60 sec | 350 MB |
| small | 120 sec | 500 MB |
| medium | 240 sec | 1.5 GB |
| large | 480 sec | 2.9 GB |

## 🐛 Troubleshooting

### Issue: "TensorFlow not available"
**Solution:** 
- Ensure Python 3.10 is installed
- Run: `pip install tensorflow==2.10.0`
- Check: `python -c "import tensorflow as tf; print(tf.__version__)"`

### Issue: "Spleeter model not found"
**Solution:** 
- Models are included in `pretrained_models/` folder
- If missing, Spleeter will download on first use (~200 MB)
- Ensure write permissions to installation directory

### Issue: "Out of memory"
**Solution:** 
- Use smaller Whisper model (tiny or base)
- Disable vocal separation
- Close other applications
- Use 2stems instead of 5stems

### Issue: "FFmpeg not found"
**Solution:** 
- FFmpeg is bundled with the installer
- For portable version, ensure ffmpeg folder exists
- Or install FFmpeg system-wide

### Issue: "Repeated words in output"
**Solution:** 
- v7.1 includes automatic hallucination removal
- Use "Auto" line break mode
- Try a larger Whisper model for better accuracy

### Issue: "Cache folder not deleting"
**Solution:** 
- v7.1 automatically cleans cache on exit
- Manual cleanup: delete `C:\NotYCaptionGenAI\cache`

## 📞 Support

| Channel | Link |
|---------|------|
| **Telegram** | https://t.me/Noty_215 |
| **YouTube** | https://www.youtube.com/@NotY215 |
| **GitHub** | https://github.com/NotY215/NotYCaptionGenAi |
| **Email** | NotY215@outlook.com |

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

### Development Setup
```bash
git clone https://github.com/NotY215/NotYCaptionGenAi.git
cd NotYCaptionGenAi
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 🙏 Acknowledgments

- **[OpenAI Whisper](https://github.com/openai/whisper)** - Speech recognition technology
- **[Deezer Spleeter](https://github.com/deezer/spleeter)** - Vocal separation engine
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - YouTube downloading
- **[FFmpeg](https://ffmpeg.org)** - Audio processing backbone
- **[TensorFlow](https://tensorflow.org)** - Machine learning framework

## 📈 Version History

| Version | Date | Changes |
|---------|------|---------|
| 7.1 | Apr 2026 | Modular architecture, audio chunking, 60% faster startup |
| 6.1 | Mar 2026 | Spleeter integration, vocal separation, YouTube support |
| 6.0 | Feb 2026 | Whisper AI, multi-language, smart formatting |
| 5.0 | Jan 2026 | Initial release with basic transcription |

---

## ⭐ Star the Project
If you find this tool useful, please consider starring the repository on GitHub!


**Made with ❤️ by NotY215**

*Last Updated: April 2026*
