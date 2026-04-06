
<p align="center">
  <img src="./resources/app.ico" alt="NotYCaptionGenAi Logo" width="128">
</p>

<h1 align="center">🎬 NotYCaptionGenAi</h1>
<p align="center">
  <strong>AI-Powered Subtitle & Lyrics Generator - No Installation Required</strong>
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

**NotYCaptionGenAi** is a powerful command-line tool that automatically creates SRT subtitles or song lyrics for video and audio files using OpenAI's Whisper AI. It features **vocal separation**, **online lyrics search**, **intelligent sentence detection**, and **complete transliteration** for Hindi and Japanese. **No installation required** – just download and run the EXE!

### ✨ Key Features

- 🎥 **Multi-format Support**: MP4, MKV, AVI, MOV, MP3, WAV, M4A, FLAC, WEBM
- 🤖 **AI-Powered**: Uses OpenAI Whisper for accurate transcription
- 🌐 **Translation Mode**: Automatically translate any language to English (only shown when source language is not English)
- 🔤 **Complete Transliteration**: Full Hindi (Devanagari) and Japanese (Kana/Kanji) → English/Romanized text
- 🎵 **Song Mode** (NEW): Enhanced lyrics generation with vocal separation and online lyrics search
- 🔊 **Vocal Separation**: Isolates vocals from background music for cleaner lyrics
- 📡 **Online Lyrics Search**: Searches Genius.com, AZLyrics, and other sources for matching lyrics
- 🔄 **Auto Line Break**: Intelligent sentence detection based on audio gaps and punctuation
- 📦 **Built-in Models**: Tiny, Base, Small, Medium, Large (choose speed vs accuracy)
- 📝 **Flexible Line Breaking**: Word count, character limit, or automatic detection
- 💾 **SRT Format**: Standard subtitle format compatible with all media players
- 🚀 **Portable**: Single EXE with all dependencies – no installation needed
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
1. **Download the EXE** from the releases page
2. **Run the Application** – double‑click to launch
3. **First‑time Setup**:
   - All required files are extracted automatically
   - Whisper models download on demand when selected
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
Double‑click NotYCaptionGenAI.exe

# Python Version
python noty_caption_gen.py
```

### Step‑by‑Step Walkthrough

**1. Launch the Application**
```
+==========================================================+
|              NotY Caption Generator AI v5.1              |
|                Copyright (c) 2026 NotY215                |
|                    License: LGPL-3.0                     |
|                Powered by OpenAI Whisper                 |
+==========================================================+
```

**2. Select a Video or Audio File**
- A file dialog opens showing all supported formats
- Or you can drag & drop a file into the console
```
Supported formats: .mp4, .avi, .mkv, .mov, .mp3, .wav, .m4a, .flac, .webm
> E:\Music\my_song.mp3
[OK] Selected: my_song.mp3
```

**3. Choose Whisper Model**
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

**5. Choose Mode**
- **Normal Mode**: Standard subtitles in selected language
- **Song Mode** (if selected): Enhanced lyrics with vocal separation and online search
- **Translate to English** (only appears when language ≠ English)
```
┌──────────────────────────────────────────────────┐
│                   SELECT MODE                     │
├──────────────────────────────────────────────────┤
│  1) Normal Mode - Generate subtitles from audio  │
│  2) Song Mode - Enhanced lyrics with online search│
│  0) Back                                         │
└──────────────────────────────────────────────────┘
Choose option (0-2): 2
```

**6. Song Search Option (only in Song Mode)**
```
┌──────────────────────────────────────────────────┐
│               SONG SEARCH OPTION                  │
├──────────────────────────────────────────────────┤
│  1) Auto Detect Song - Automatically from filename│
│  2) Manual Song Name - Enter artist - song name  │
│  0) Back                                         │
└──────────────────────────────────────────────────┘
Choose option (0-2): 2
> Enter song name: One Piece - Binks' Sake
```

**7. Line Type (Normal Mode only)**
- **Words**: Break by word count (1‑30)
- **Letters**: Break by character count (1‑30)
- **Auto**: Intelligent sentence detection using audio gaps & punctuation
```
┌──────────────────────────────────────────────────┐
│                   LINE TYPE                       │
├──────────────────────────────────────────────────┤
│  1) Words - Break by word count                  │
│  2) Letters - Break by character limit           │
│  3) Auto - Auto-detect sentence breaks           │
│  0) Back                                         │
└──────────────────────────────────────────────────┘
Choose option (0-3): 1
> How many words per line? (1-30): 8
```

**8. Confirmation & Generation**
```
+--------------------------------------------------+
| Media File: E:\Music\my_song.mp3                |
| Model: SMALL                                     |
| Language: English                                |
| Mode: Song Mode                                  |
| Search: Manual: One Piece - Binks' Sake         |
+--------------------------------------------------+

Generate lyrics? (y/n): y
```

**9. Processing Output**
```
[INFO] Generating lyrics with online search...
[PROGRESS] ████████████████████████████████████████ 10% - Extracting audio...
[PROGRESS] ████████████████████████████████████████ 30% - Separating vocals...
[PROGRESS] ████████████████████████████████████████ 45% - Searching lyrics...
[OK] Lyrics found on Genius!
[PROGRESS] ████████████████████████████████████████ 60% - Loading SMALL model...
[PROGRESS] ████████████████████████████████████████ 70% - Transcribing audio...
[PROGRESS] ████████████████████████████████████████ 80% - Processing lyrics...
[PROGRESS] ████████████████████████████████████████ 90% - Writing file...
[PROGRESS] ████████████████████████████████████████ 100% - Complete!

[OK] Lyrics saved to: E:\Music\my_song_lyrics.srt (with online lyrics)
[INFO] Generated 45 lyrics entries
```

**10. Completion & Next Steps**
```
[OK] Thanks for using NotY Caption Generator AI!
[OK] Your caption has been generated successfully!

Process another file? (y/n): n
```

---

## 🎯 Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| Tiny | 75 MB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Quick tests, short clips |
| Base | 150 MB | ⚡⚡⚡⚡ | ⭐⭐⭐ | General use, balanced |
| Small | 500 MB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Good accuracy, moderate speed |
| Medium | 1.5 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | High accuracy, longer files |
| Large | 2.9 GB | ⚡ | ⭐⭐⭐⭐⭐ | Professional, maximum accuracy |

---

## 🌐 Mode Explanations

### 1. **Normal Mode**
- Generates subtitles in the chosen language (or auto‑detected)
- Preserves original script (e.g., Devanagari, Kanji)
- Best for general video/audio transcription

### 2. **Translate to English** (only when source language ≠ English)
- Automatically translates subtitles to English
- Uses Whisper’s built‑in translation
- Ideal for international audiences

### 3. **Song Mode** (NEW in v5.1)
- **Vocal Separation**: Extracts vocals using FFmpeg filters
- **Online Lyrics Search**: Queries Genius.com, AZLyrics, and others
- **Timing Alignment**: Syncs found lyrics with audio segments
- **Fallback**: If no online lyrics found, uses AI transcription
- **Internet required** for online search (falls back gracefully)

---

## 📝 Line Type Options

| Option | Description | Best For |
|--------|-------------|----------|
| **Words** | Break by word count (1‑30) | Dialogue, general videos |
| **Letters** | Break by character count (1‑30) | Languages with long words, social media clips |
| **Auto** | Intelligent sentence detection using audio gaps & punctuation | Natural speech, presentations, podcasts |

---

## 🎵 Song Mode Deep Dive

### Vocal Separation
- Uses FFmpeg `highpass` and `lowpass` filters
- Reduces background music interference
- Works best with clear vocals

### Online Lyrics Sources
- **Genius.com** (primary)
- **AZLyrics** (fallback)
- **Lyrics.ovh API** (fallback)
- **ChartLyrics API** (fallback)
- **YouTube descriptions** (as a last resort)

### Automatic Retry
- If auto‑detection fails, the app suggests using manual entry with format:  
  `Artist - Song Name`
- Example: `"Taylor Swift - Shake It Off"`

---

## 📁 Output Files

| Filename Pattern | Description |
|------------------|-------------|
| `[filename].srt` | Standard subtitles in original language |
| `[filename]_en.srt` | English translated subtitles (Translation mode) |
| `[filename]_lyrics.srt` | Enhanced song lyrics (Song mode) |

All files are saved in the same directory as the source media.

---

## 🎯 Supported Formats

| Type | Extensions |
|------|------------|
| **Video** | `.mp4`, `.avi`, `.mkv`, `.mov`, `.webm`, `.m4v`, `.mpg`, `.mpeg` |
| **Audio** | `.mp3`, `.wav`, `.m4a`, `.flac` |

---

## ⚙️ System Requirements

### Minimum
| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11 (64‑bit) or Linux/macOS (Python version) |
| **RAM** | 2 GB (Tiny/Base models) |
| **Storage** | 500 MB (app + models) |
| **CPU** | Intel Core i3 or equivalent |
| **Internet** | Required for Song Mode lyrics search |

### Recommended
| Component | Recommendation |
|-----------|----------------|
| **RAM** | 8 GB (Medium/Large models) |
| **Storage** | 4 GB free space |
| **CPU** | Intel Core i5/i7 or AMD Ryzen 5/7 |
| **Internet** | Stable connection for Song Mode |

---

## 🔧 Troubleshooting

### Common Issues & Solutions

**Q: Application doesn't start?**
- Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Run as administrator if needed
- Temporarily disable Windows Defender

**Q: File not found error?**
- Use full path with double quotes if spaces: `"C:\My Files\video.mp4"`
- Ensure the file exists and is not corrupted

**Q: Model download fails?**
- Check internet connection
- Free up disk space (at least 2× model size)
- Disable firewall temporarily

**Q: Song Mode doesn't find lyrics?**
- Ensure file name contains the song name
- Check internet connection
- Try Manual Song Name with format `Artist - Song Name`
- Song Mode falls back to AI transcription automatically

**Q: Vocal separation not working?**
- FFmpeg is bundled – should work out of the box
- Works best with high‑quality audio (clear vocals)
- Separation failure falls back to original audio

**Q: Auto line break not working properly?**
- Ensure audio has natural pauses
- Works best with clear speech or well‑spaced sentences

**Q: Transliteration breaks words?**
- Fixed in v5.1 – complete character mapping
- Supports full Hindi and Japanese character sets

**Q: Slow transcription?**
- Use Tiny or Base model for speed
- Close other CPU‑intensive applications
- Use SSD storage

---

## 📊 Performance Tips

- **For quick previews**: Use Tiny or Base model
- **For best accuracy**: Use Large model (slower)
- **For songs**: Use Song Mode with clear file naming
- **For natural speech**: Use Auto line break mode
- **For Japanese/Hindi**: Transliteration is automatic when those languages are selected
- **For other languages**: Use Normal or Translate mode

---

## 💬 Support & Community

Join our Telegram channel for updates, support, and discussions:

<p align="center">
<a href="https://t.me/NotY215">
<img src="https://img.shields.io/badge/Join%20us%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram" alt="Join Telegram">
</a>
<a href="https://www.youtube.com/@NotY215">
<img src="https://img.shields.io/badge/Subscribe%20on-YouTube-FF0000?style=for-the-badge&logo=youtube" alt="Subscribe on YouTube">
</a>
</p>

- **Telegram**: [https://t.me/NotY215](https://t.me/NotY215)
- **YouTube**: [https://www.youtube.com/@NotY215](https://www.youtube.com/@NotY215)
- **GitHub**: [https://github.com/NotY215/NotYCaptionGenAi](https://github.com/NotY215/NotYCaptionGenAi)

---

## 📄 License

This project is licensed under the **GNU Lesser General Public License v3.0**.

You may:
- ✅ Use this software commercially
- ✅ Modify the source code
- ✅ Distribute the software

You must:
- ⚠️ Disclose source code for modifications
- ⚠️ Include the copyright notice

Full license: [https://www.gnu.org/licenses/lgpl-3.0.en.html](https://www.gnu.org/licenses/lgpl-3.0.en.html)

---

## 👨‍💻 Credits

- **Developer**: NotY215
- **AI Model**: OpenAI Whisper (PyTorch)
- **Media Processing**: FFmpeg
- **Lyrics Sources**: Genius, AZLyrics, Lyrics.ovh, ChartLyrics

---

## 🆕 What's New in Version 5.1

### Added
- 🎵 **Song Mode** – vocal separation + online lyrics search
- 🔊 **Vocal Separation** – isolates vocals for cleaner lyrics
- 📡 **Online Lyrics Search** – queries multiple sources
- 🔄 **Auto Line Break** – intelligent sentence detection
- ✨ **Complete Transliteration** – full Hindi/Japanese character maps
- 📊 **Progress Bar** – percentage‑based visual feedback

### Improved
- 🔧 **Transliteration** – no more word breaking
- 🔧 **Error Handling** – clearer messages
- 🔧 **Build Size** – smaller executable
- 🔧 **FFmpeg Integration** – bundled with the app
- 🔧 **Registry Registration** – appears in Windows Add/Remove Programs

### Fixed
- 🐛 Transliteration breaking words into parts
- 🐛 Progress display showing frames instead of percentage
- 🐛 Audio extraction for all formats
- 🐛 Model loading issues
- 🐛 Unicode encoding errors on Windows

---

## 🗺️ Roadmap (Planned)

- [ ] GPU acceleration support
- [ ] Batch processing for multiple files
- [ ] GUI version with drag‑and‑drop
- [ ] Cloud model storage
- [ ] More language support for transliteration
- [ ] Real‑time transcription
- [ ] Subtitle editing interface
- [ ] Export to ASS, VTT formats

---

## 📊 Version History

| Version | Date | Major Changes |
|---------|------|---------------|
| 5.1 | 2026 | Song Mode, vocal separation, online lyrics, auto line break |
| 4.5 | 2026 | FFmpeg bundling, registry support, admin check |
| 4.4 | 2026 | Improved word timing, translation mode |
| 4.3 | 2026 | Initial release |

---

<p align="center">
<b>Made with ❤️ by NotY215</b>
<br>
<sub>Copyright © 2026 NotY215. All rights reserved.</sub>
<br>
<sub>Licensed under GNU Lesser General Public License v3.0</sub>
<br>
<sub>No installation required – just download and run!</sub>
<br><br>
<sub>⭐ If you like this project, please star it on GitHub! ⭐</sub>
</p>
