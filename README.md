<p align="center">
  <img src="./resources/app.ico" alt="NotYCaptionGenAi Logo" width="128">
</p>

<h1 align="center">🎬 NotYCaptionGenAi</h1>
<p align="center">
  <strong>AI-Powered Subtitle Generator - No Installation Required</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-5.1-brightgreen.svg" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Type-Console%20Application-orange.svg" alt="Type">
  <img src="https://img.shields.io/badge/License-LGPL%20v3-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Download-EXE-success.svg" alt="Download">
</p>

---

## 📋 Overview

**NotYCaptionGenAi** is a powerful command-line subtitle generator that automatically creates SRT subtitles for video and audio files using OpenAI's Whisper AI model with advanced features like vocal separation and online lyrics search. **No installation required** - just download and run the EXE!

### ✨ Features

- 🎥 **Multi-format Support**: MP4, MKV, AVI, MOV, MP3, WAV, M4A, FLAC, WEBM
- 🤖 **AI-Powered**: Uses OpenAI Whisper for accurate transcription
- 🌐 **Translation Mode**: Automatically translate subtitles to English
- 🔤 **Transliteration**: Complete Japanese/Hindi to English/Romanized text conversion
- 🎵 **Song Mode**: Enhanced lyrics with vocal separation and online lyrics search
- 🔊 **Vocal Separation**: Extracts vocals from background music for cleaner lyrics
- 📡 **Online Lyrics Search**: Searches Genius.com for matching song lyrics
- 🔄 **Auto Line Break**: Intelligent sentence detection based on audio gaps
- 📦 **Built-in Models**: Tiny, Base, Small, Medium, and Large models available
- 📝 **Smart Line Breaking**: Choose between word, letter, or auto-detection
- 💾 **SRT Format**: Standard subtitle format compatible with all media players
- 🚀 **Portable**: Single EXE file with bundled dependencies - no installation required
- 💬 **Automatic Links**: Opens Telegram and YouTube channels after completion
- 🐍 **Python Version**: Also available as a Python script for cross-platform use

---

## 🚀 Download & Installation

### Download Options

**Option 1: Windows EXE (Recommended)**
🔗 **[Download NotYCaptionGenAI.exe](https://github.com/NotY215/NotYCaptionGenAi/releases/latest)**

**Option 2: Python Script (Cross-Platform)**
🔗 **[Download Python Version](https://github.com/NotY215/NotYCaptionGenAi/archive/refs/heads/main.zip)**

### Installation

**Windows EXE Version:**
1. **Download the EXE**: Get `NotYCaptionGenAI.exe` from the releases page
2. **Run the Application**: Double-click to launch - that's it!
3. **First-time Setup**:
   - The app automatically extracts all required files
   - Models download automatically when selected
   - No manual configuration needed

**Python Version:**
1. **Install Python 3.7+** from [python.org](https://python.org)
2. **Extract the files** to any folder
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Run**: `python noty_caption_gen.py`

---

## 📖 Usage Guide

### Quick Start

```bash
# Windows EXE
Double-click NotYCaptionGenAI.exe

# Python Version
python noty_caption_gen.py
```

### Step-by-Step Instructions

**1. Launch the Application**
```
+==========================================================+
|              NotY Caption Generator AI v5.1              |
|                Copyright (c) 2026 NotY215                |
|                    License: LGPL-3.0                     |
|                Powered by OpenAI Whisper                 |
+==========================================================+
```

**2. Enter Video/Audio File Path**
```
[INFO] Opening file selection dialog...
[OK] Selected: E:\Videos\myvideo.mp4
```

**3. Select Model**
```
┌──────────────────────────────────────────────────┐
│                   SELECT MODEL                    │
├──────────────────────────────────────────────────┤
│  1) TINY (75 MB) - Fastest                       │
│  2) BASE (150 MB) - Balanced                     │
│  3) SMALL (500 MB) - Good                        │
│  4) MEDIUM (1.5 GB) - Accurate                   │
│  5) LARGE (2.9 GB) - Best                        │
│  0) Back                                         │
└──────────────────────────────────────────────────┘
Choose option (0-5): 3
```

**4. Select Language**
```
┌──────────────────────────────────────────────────┐
│                 SELECT LANGUAGE                   │
├──────────────────────────────────────────────────┤
│  1) English (en)                                 │
│  2) Hindi (hi)                                   │
│  3) Japanese (ja)                                │
│  4) Auto Detect (auto)                           │
│  0) Back                                         │
└──────────────────────────────────────────────────┘
Choose option (0-4): 1
```

**5. Select Mode**
```
┌──────────────────────────────────────────────────┐
│                   SELECT MODE                     │
├──────────────────────────────────────────────────┤
│  1) Normal - Generate subtitles in selected lang │
│  2) Translate to English - Translate to English  │
│  3) Song Mode - Enhanced lyrics with online search│
│  0) Back                                         │
└──────────────────────────────────────────────────┘
Choose option (0-3): 3
```

**6. Select Line Type**
```
┌──────────────────────────────────────────────────┐
│                   LINE TYPE                       │
├──────────────────────────────────────────────────┤
│  1) Words - Break by word count                 │
│  2) Letters - Break by character limit          │
│  3) Auto - Auto-detect sentence breaks          │
│  0) Back                                         │
└──────────────────────────────────────────────────┘
Choose option (0-3): 1
```

**7. Set Words per Line (if Words selected)**
```
How many words per line? (1-30): 8
```

**8. Confirm Generation**
```
+--------------------------------------------------+
| Media File: E:\Videos\myvideo.mp4               |
| Model: SMALL                                     |
| Language: English                                |
| Mode: Song Mode                                  |
| Line Type: Words                                 |
| Settings: 8                                      |
+--------------------------------------------------+

Generate captions? (y/n): y
```

**9. Processing & Generation**
```
[INFO] Generating captions... This may take several minutes.
[PROGRESS] ████████████████████████████████████████ 10% - Extracting audio from video...
[PROGRESS] ████████████████████████████████████████ 30% - Separating vocals from background music...
[PROGRESS] ████████████████████████████████████████ 45% - Searching lyrics for: myvideo
[OK] Found lyrics online!
[PROGRESS] ████████████████████████████████████████ 60% - Loading SMALL model...
[PROGRESS] ████████████████████████████████████████ 70% - Transcribing audio...
[PROGRESS] ████████████████████████████████████████ 80% - Processing transcription...
[PROGRESS] ████████████████████████████████████████ 90% - Writing subtitle file...
[PROGRESS] ████████████████████████████████████████ 100% - Complete!

[OK] Captions saved to: E:\Videos\myvideo_lyrics.srt
[INFO] Generated 156 subtitle entries
```

**10. Completion**
```
[OK] Thanks for using NotY Caption Generator AI!
[OK] Your caption has been generated successfully!

Process another video? (y/n): n
```

---

## 🎯 Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| Tiny | 75 MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Quick tests, short videos |
| Base | 150 MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | General use, balanced performance |
| Small | 500 MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Good accuracy, moderate speed |
| Medium | 1.5 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | High accuracy, longer videos |
| Large | 2.9 GB | ⚡ | ⭐⭐⭐⭐⭐ | Maximum accuracy, professional use |

---

## 🌐 Subtitle Modes Explained

### 1. **Normal Mode**
- Generates subtitles in the original language script
- Preserves native characters (Devanagari, Kanji, etc.)
- Best for viewers who understand the original language
- Example: Japanese text stays in Japanese characters

### 2. **Translation Mode**
- Automatically translates subtitles to English
- Uses Whisper's built-in translation capability
- Perfect for international audiences
- Example: Japanese audio → English subtitles

### 3. **Song Mode** (NEW in v5.1)
- **Vocal Separation**: Extracts vocals from background music using FFmpeg
- **Online Lyrics Search**: Searches Genius.com for matching song lyrics
- **Enhanced Accuracy**: Combines AI transcription with online lyrics
- **Perfect for Music**: Creates professional-quality song lyrics
- **Internet Required**: For online lyrics search feature

---

## 📝 Line Type Options

### 1. **Words**
- Breaks subtitles by word count
- Customizable: 1-30 words per line
- Best for: General videos, dialogue

### 2. **Letters**
- Breaks subtitles by character count
- Customizable: 1-30 characters per line
- Best for: Languages with long words, social media clips

### 3. **Auto** (NEW in v5.1)
- Intelligent sentence detection
- Breaks at natural pauses and punctuation
- Uses audio gap analysis
- Best for: Natural speech, presentations

---

## 🎵 Song Mode Features

### Vocal Separation
- Extracts vocals using FFmpeg filters
- Reduces background music interference
- Improves lyric accuracy

### Online Lyrics Search
- Searches Genius.com database
- Matches by song name from filename
- Falls back to AI transcription if not found
- Requires internet connection

### Lyrics Processing
- Timestamp alignment with audio
- Natural line breaking
- Proper punctuation and formatting

---

## 📁 Output Files

After successful generation, you'll find:

| File | Description |
|------|-------------|
| `[filename].srt` | Standard subtitles in original language |
| `[filename]_en.srt` | English translated subtitles (Translation mode) |
| `[filename]_lyrics.srt` | Song lyrics with enhanced formatting (Song mode) |

All SRT files are saved in the same folder as your source media file.

---

## 🎯 Supported Formats

| Type | Formats |
|------|---------|
| **Video** | MP4, AVI, MKV, MOV, WEBM, MPG, MPEG, M4V |
| **Audio** | MP3, WAV, M4A, FLAC |

---

## ⚙️ System Requirements

### Minimum Requirements
| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11 (64-bit) or Linux/Mac (Python version) |
| **RAM** | 2GB (for Tiny/Base models) |
| **Storage** | 500MB for application + models |
| **CPU** | Any modern processor (Intel Core i3 or equivalent) |
| **Internet** | Required for Song Mode (lyrics search) |

### Recommended Requirements
| Component | Requirement |
|-----------|-------------|
| **RAM** | 8GB (for Medium/Large models) |
| **Storage** | 4GB free space |
| **CPU** | Intel Core i5/i7 or AMD Ryzen 5/7 |
| **GPU** | Optional - no GPU required |
| **Internet** | Stable connection for Song Mode |

---

## 🔧 Troubleshooting

### Common Issues & Solutions

**Q: Application doesn't start?**
- ✅ Ensure you have Visual C++ Redistributable installed
- ✅ Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
- ✅ Run as administrator if needed
- ✅ Check Windows Defender - allow the application

**Q: File not found error?**
- ✅ Enter the full file path correctly
- ✅ Use double quotes if path contains spaces
- ✅ Example: `"C:\My Videos\my video.mp4"`
- ✅ Ensure file exists and is not corrupted

**Q: Model download fails?**
- ✅ Check internet connection
- ✅ Ensure sufficient disk space (at least 2x model size)
- ✅ Try again - downloads resume automatically
- ✅ Disable firewall temporarily if needed

**Q: Song Mode not finding lyrics?**
- ✅ Ensure file name contains the song name
- ✅ Check internet connection
- ✅ Try renaming file to actual song name
- ✅ Song Mode falls back to AI transcription

**Q: Vocal separation not working?**
- ✅ Ensure FFmpeg is included in the package
- ✅ Check audio quality - clear vocals work best
- ✅ Song Mode works without separation too

**Q: Auto line break not working properly?**
- ✅ Ensure audio has clear pauses
- ✅ Adjust audio quality for better detection
- ✅ Falls back to word/letter mode if needed

**Q: Transliteration breaking words?**
- ✅ Fixed in v5.1 - complete character mapping
- ✅ Supports full Hindi and Japanese character sets
- ✅ Proper word boundary detection

**Q: Slow transcription?**
- ✅ Use Tiny or Base model for faster processing
- ✅ Close other applications to free up CPU
- ✅ Split long videos into shorter segments
- ✅ Use SSD instead of HDD for better performance

**Q: Subtitles not accurate?**
- ✅ Ensure clear audio quality (no background noise)
- ✅ Try a larger model (Medium or Large)
- ✅ Check if audio language is supported
- ✅ Use Normal mode instead of Translation for better accuracy

---

## 📊 Performance Tips

### For Best Results:
1. **Use high-quality audio** - Clear speech improves accuracy dramatically
2. **Choose the right model**:
   - Tiny/Base: Quick previews, short videos
   - Small/Medium: General use, good balance
   - Large: Professional use, maximum accuracy
3. **For songs**: Use Song Mode with clear file naming
4. **For natural speech**: Use Auto line break mode
5. **Optimize for speed**:
   - Use SSD storage for faster processing
   - Close unnecessary applications
   - Process shorter segments
6. **Language-specific tips**:
   - English: Works well with all models
   - Japanese/Hindi: Use transliteration for Latin script output
   - Other languages: Use Normal or Translation mode

---

## 💬 Support & Community

Join our Telegram channel for:
- 📢 Latest updates and releases
- 🛠️ Technical support
- 💡 Tips and tricks
- 🤝 Community discussions

<p align="center">
<a href="https://t.me/NotY215">
<img src="https://img.shields.io/badge/Join%20us%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram" alt="Join Telegram">
</a>
<a href="https://www.youtube.com/@NotY215">
<img src="https://img.shields.io/badge/Subscribe%20on-YouTube-FF0000?style=for-the-badge&logo=youtube" alt="Subscribe on YouTube">
</a>
</p>

**Telegram Channel:** [https://t.me/NotY215](https://t.me/NotY215)  
**YouTube Channel:** [https://www.youtube.com/@NotY215](https://www.youtube.com/@NotY215)

---

## 📄 License

This project is licensed under the **GNU Lesser General Public License v3.0**.

The LGPL license allows you to:
- ✅ Use this software commercially
- ✅ Modify the source code
- ✅ Distribute the software
- ⚠️ Must disclose source code for modifications
- ⚠️ Must include copyright notice

For the full license text, visit: https://www.gnu.org/licenses/lgpl-3.0.en.html

---

## 👨‍💻 Credits

- **Developed By**: NotY215
- **AI Model**: OpenAI Whisper
- **Model Format**: PyTorch Whisper
- **Media Processing**: FFmpeg
- **Lyrics Source**: Genius.com
- **Python Version**: Pure Python implementation with colorama

---

## 📞 Contact

- **Telegram**: https://t.me/NotY215
- **YouTube**: https://www.youtube.com/@NotY215
- **GitHub**: https://github.com/NotY215/NotYCaptionGenAi

---

## 🆕 What's New in Version 5.1

### Added Features:
- 🎵 **Song Mode** - Enhanced lyrics with vocal separation and online search
- 🔊 **Vocal Separation** - Extracts vocals from background music
- 📡 **Online Lyrics Search** - Searches Genius.com for matching lyrics
- 🔄 **Auto Line Break** - Intelligent sentence detection based on audio gaps
- ✨ **Complete Transliteration** - Full Hindi and Japanese character mapping
- 📊 **Progress Bar** - Visual percentage-based progress display

### Improvements:
- 🔧 **Fixed Transliteration** - No more word breaking issues
- 🔧 **Better Error Handling** - More descriptive error messages
- 🔧 **Optimized Build** - Smaller executable size
- 🔧 **FFmpeg Integration** - Built-in FFmpeg for audio processing
- 🔧 **Registry Registration** - Appears in Windows Add/Remove Programs

### Bug Fixes:
- 🐛 Fixed transliteration breaking words into parts
- 🐛 Fixed progress display showing frames instead of percentage
- 🐛 Fixed audio extraction for all formats
- 🐛 Fixed model loading issues
- 🐛 Fixed Unicode encoding errors on Windows

---

## 🗺️ Roadmap

### Future Plans:
- [ ] GPU acceleration support
- [ ] Batch processing for multiple files
- [ ] GUI version with drag-and-drop
- [ ] Cloud model storage
- [ ] More language support for transliteration
- [ ] Custom vocabulary support
- [ ] Real-time transcription
- [ ] Subtitle editing interface
- [ ] Export to multiple formats (ASS, VTT, etc.)
- [ ] Multiple lyrics sources (AZLyrics, MetroLyrics)

---

## 📊 Version History

| Version | Date | Changes |
|---------|------|---------|
| 5.1 | 2026 | Song Mode, Vocal Separation, Online Lyrics, Auto Line Break |
| 4.5 | 2026 | FFmpeg integration, Registry support, Admin check |
| 4.4 | 2026 | Improved word timing, Translation mode |
| 4.3 | 2026 | Initial release with Whisper.cpp |

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub! It helps others discover the project and motivates further development.

<p align="center">
<a href="https://github.com/NotY215/NotYCaptionGenAi/stargazers">
<img src="https://img.shields.io/github/stars/NotY215/NotYCaptionGenAi?style=social" alt="GitHub stars">
</a>
<a href="https://github.com/NotY215/NotYCaptionGenAi/network/members">
<img src="https://img.shields.io/github/forks/NotY215/NotYCaptionGenAi?style=social" alt="GitHub forks">
</a>
<a href="https://github.com/NotY215/NotYCaptionGenAi/watchers">
<img src="https://img.shields.io/github/watchers/NotY215/NotYCaptionGenAi?style=social" alt="GitHub watchers">
</a>
</p>

---

<p align="center">
<b>Made with ❤️ by NotY215</b>
<br>
<sub>Copyright © 2026 NotY215. All rights reserved.</sub>
<br>
<sub>This software is provided under the GNU Lesser General Public License v3.0</sub>
<br>
<sub>No installation required - just download and run!</sub>
<br>
<br>
<sub>🌟 If you like this project, don't forget to star it on GitHub! 🌟</sub>
</p>
