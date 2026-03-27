
<p align="center">
  <img src="https://raw.githubusercontent.com/NotY215/NotYCaptionGenAi/main/src/main/resources/app.ico" alt="NotYCaptionGenAi Logo" width="128">
</p>

<h1 align="center">🎬 NotYCaptionGenAi</h1>
<p align="center">
  <strong>AI-Powered Subtitle Generator - No Installation Required</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-3.0.2-brightgreen.svg" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Type-Console%20Application-orange.svg" alt="Type">
  <img src="https://img.shields.io/badge/License-LGPL%20v3-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Download-EXE-success.svg" alt="Download">
</p>

---

## 📋 Overview

**NotYCaptionGenAi** is a powerful command-line subtitle generator that automatically creates SRT subtitles for video and audio files using OpenAI's Whisper AI model. **No installation required** - just download and run the EXE!

### ✨ Features

- 🎥 **Multi-format Support**: MP4, MKV, AVI, MOV, MP3, WAV, M4A, FLAC, WEBM
- 🤖 **AI-Powered**: Uses OpenAI Whisper for accurate transcription
- 🌐 **Translation Mode**: Automatically translate subtitles to English
- 🔤 **Transliteration**: Convert Japanese/Hindi scripts to English/Romanized text
- 📦 **Built-in Models**: Tiny, Base, Small, Medium, and Large models available
- 📝 **Smart Line Breaking**: Choose between word or letter-based line breaking (1-30 per line)
- 💾 **SRT Format**: Standard subtitle format compatible with all media players
- 🚀 **Portable**: Single EXE file with bundled dependencies - no installation required
- 💬 **Automatic Links**: Opens Telegram and YouTube channels after completion

---

## 🚀 Download & Installation

### Download

**Download the latest EXE from:**  
🔗 **[https://github.com/NotY215/NotYCaptionGenAi/releases/latest](https://github.com/NotY215/NotYCaptionGenAi/releases/latest)**

### Installation

1. **Download the EXE**: Get `NotYCaptionGenAi.exe` from the releases page
2. **Run the Application**: Double-click to launch - that's it!
3. **First-time Setup**:
   - The app automatically extracts all required files (FFmpeg, Whisper)
   - Models download automatically when selected
   - No manual configuration needed

---

## 📖 Usage Guide

### Step-by-Step Instructions

**1. Launch the Application**
```
Double-click NotYCaptionGenAi.exe
```

**2. Enter Video/Audio File Path**
```
╔═══════════════════════════════════════════╗
║     NOTY CAPTION GENERATOR AI v1.0       ║
║     Powered by Whisper.cpp               ║
╚═══════════════════════════════════════════╝

📂 Provide Video/Audio Path
Allowed extensions: .mp4, .avi, .mkv, .mov, .mp3, .wav, .m4a, .flac, .webm
➤ C:\Videos\myvideo.mp4
```

**3. Choose Model Option**
```
┌─────────────────────────────────┐
│         MAIN MENU               │
├─────────────────────────────────┤
│  1) Choose Model               │
│  0) Go Back (Resend video path)│
└─────────────────────────────────┘
➤ Choose option (0-1): 1
```

**4. Select Whisper Model**
```
┌─────────────────────────────────┐
│       SELECT MODEL             │
├─────────────────────────────────┤
│  1) Tiny (75 MB) - Fastest     │
│  2) Base (150 MB) - Balanced   │
│  3) Small (500 MB) - Good      │
│  4) Medium (1.5 GB) - Accurate │
│  5) Large (2.9 GB) - Best      │
│  0) Back                       │
└─────────────────────────────────┘
➤ Choose model (0-5): 1
```

**5. Model Status & Download**
```
┌─────────────────────────────────┐
│       MODEL STATUS             │
├─────────────────────────────────┤
│  Selected: TINY (75 MB)        │
├─────────────────────────────────┤
│  ✗ Model not found!            │
│  1) Download Model             │
│     (≈ 75 MB)                  │
│  0) Back                       │
└─────────────────────────────────┘
➤ Choose option (0-1): 1

📥 Downloading TINY model...
🔗 URL: https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin
📦 Total size: 75 MB
[==================================================>] 100.0% 75.0 MB/75.0 MB
✅ Model downloaded successfully!
```

**6. Choose Line Breaking Method**
```
┌─────────────────────────────────┐
│       LINE PREFERENCE          │
├─────────────────────────────────┤
│  1) Words                      │
│  2) Letters                    │
│  0) Back                       │
└─────────────────────────────────┘
➤ Choose preference (0-2): 1
```

**7. Choose Subtitle Mode**
```
┌─────────────────────────────────────────┐
│         SUBTITLE MODE                   │
├─────────────────────────────────────────┤
│  1) Normal                              │
│     (Generate in original language)     │
│                                         │
│  2) Translation                         │
│     (Translate subtitle to English)     │
│                                         │
│  3) Transliteration                    │
│     (Convert Japanese/Hindi to English)│
│     ⚠️  Works only for Japanese/Hindi  │
│                                         │
│  0) Back                                │
└─────────────────────────────────────────┘
➤ Choose mode (0-3): 1
```

**8. Enter Number per Line**
```
┌─────────────────────────────────┐
│  How many words per line?      │
├─────────────────────────────────┤
│  Range: 1-30                   │
│  0) Back                       │
└─────────────────────────────────┘
➤ Enter number (0-30): 12
```

**9. Confirm Generation**
```
╔═══════════════════════════════════════════╗
║         CONFIRM GENERATION                ║
╠═══════════════════════════════════════════╣
║ 📁 Media File: C:\Videos\myvideo.mp4     ║
║ 🤖 Model: TINY                            ║
║ 🎯 Subtitle Mode: Normal (Original)      ║
║ 📝 Line Type: words                       ║
║ 🔢 Words per line: 12                     ║
║ 💾 Output: C:\Videos\myvideo.srt         ║
╠═══════════════════════════════════════════╣
║  1) Continue                             ║
║  0) Back                                 ║
╚═══════════════════════════════════════════╝
➤ Are you sure? (0-1): 1
```

**10. Processing & Generation**
```
🎬 Starting caption generation...
📝 This may take a while depending on media length...

🔧 Running command: resources/whisper/whisper-cli.exe -m resources/models/ggml-tiny.bin -f C:\Videos\myvideo.mp4 -of C:\Videos\myvideo -t 8 -p 4 --output-srt --print-progress

[==================================================>] 100.0%
✅ Captions generated and saved to: C:\Videos\myvideo.srt
```

**11. Completion**
```
✅ Thanks For using NotY Caption Generator AI!
Your caption has been generated successfully!

🌐 Opening links...
✓ Telegram opened
✓ YouTube opened

┌─────────────────────────────────┐
│         WHAT'S NEXT?           │
├─────────────────────────────────┤
│  1) Quit App                   │
│  0) Next Video                 │
└─────────────────────────────────┘
➤ Choose option (0-1): 0
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
## Model Download Links

| Model | Size | Download URL |
|-------|------|--------------|
| Tiny | 75 MB | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin |
| Base | 150 MB | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin |
| Small | 500 MB | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin |
| Medium | 1.5 GB | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin |
| Large | 2.9 GB | https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin |

---
## 🌐 Subtitle Modes Explained

### 1. **Normal Mode**
- Generates subtitles in the original language script
- Preserves native characters (Devanagari, Kanji, etc.)
- Best for viewers who understand the original language

### 2. **Translation Mode**
- Automatically translates subtitles to English
- Uses Whisper's built-in translation capability
- Perfect for international audiences

### 3. **Transliteration Mode**
- Converts Japanese and Hindi scripts to English/Romanized text
- Japanese: Kanji/Kana → Romaji
- Hindi: Devanagari → Romanized Hindi
- Ideal for learners or viewers who prefer Latin script

---

## 📁 Output Files

After successful generation, you'll find:

| File | Description |
|------|-------------|
| `[filename].srt` | Standard subtitles in original language |
| `[filename]_en.srt` | English translated subtitles (Translation mode) |
| `[filename]_translit.srt` | Romanized subtitles (Transliteration mode) |

All SRT files are saved in the same folder as your source media file.

---

## 🎯 Supported Formats

| Type | Formats |
|------|---------|
| **Video** | MP4, AVI, MKV, MOV, WEBM, MPG, MPEG, WMV |
| **Audio** | MP3, WAV, M4A, FLAC |

---

## ⚙️ System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 2GB (for Tiny/Base models)
- **Storage**: 500MB for application + models
- **CPU**: Any modern processor (Intel Core i3 or equivalent)

### Recommended Requirements
- **RAM**: 8GB (for Medium/Large models)
- **Storage**: 4GB free space
- **CPU**: Intel Core i5/i7 or AMD Ryzen 5/7
- **GPU**: Optional - no GPU required

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

**Q: Transliteration not working?**
- ✅ Transliteration works only for Japanese and Hindi
- ✅ Ensure audio contains these languages
- ✅ Try Normal mode first to verify language detection
- ✅ Use Translation mode for other languages

**Q: FFmpeg or Whisper errors?**
- ✅ Re-download the latest EXE version
- ✅ Extract to a new folder (avoid old files)
- ✅ Run as administrator
- ✅ Check antivirus - may quarantine required files

---

## 💬 Support & Community

Join our Telegram channel for:
- 📢 Latest updates and releases
- 🛠️ Technical support
- 💡 Tips and tricks
- 🤝 Community discussions

<p align="center">
<a href="https://t.me/Noty_215">
<img src="https://img.shields.io/badge/Join%20us%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram" alt="Join Telegram">
</a>
<a href="https://www.youtube.com/@NotY215">
<img src="https://img.shields.io/badge/Subscribe%20on-YouTube-FF0000?style=for-the-badge&logo=youtube" alt="Subscribe on YouTube">
</a>
</p>

**Telegram Channel:** [https://t.me/Noty_215](https://t.me/Noty_215)  
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
- **Model Format**: Whisper.cpp by ggerganov
- **Media Processing**: FFmpeg
- **Dependencies**: Python (bundled), PyTorch (bundled)

---

## 📞 Contact

- **Telegram**: https://t.me/Noty_215
- **YouTube**: https://www.youtube.com/@NotY215
- **GitHub**: https://github.com/NotY215/NotYCaptionGenAi

---

## 🆕 What's New in Version 3.0

- ✨ Added Translation Mode - Translate subtitles to English automatically
- ✨ Added Transliteration Mode - Convert Japanese/Hindi to Romanized text
- ✨ Added Small model option (500 MB)
- ✨ Improved progress bar with download speed display
- ✨ Better error handling and user feedback
- ✨ UTF-8 encoding support for all languages
- ✨ Faster model downloads with resume capability
- ✨ Enhanced command-line interface with better formatting

---

<p align="center">
<b>Made with ❤️ by NotY215</b>
<br>
<sub>Copyright © 2026 NotY215. All rights reserved.</sub>
<br>
<sub>This software is provided under the GNU Lesser General Public License v3.0</sub>
<br>
<sub>No installation required - just download and run!</sub>
</p>
