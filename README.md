# 🎬 NotYCaptionGenAi
### *AI-Powered Subtitle Generator with Letter Spacing Control*

[![C++](https://img.shields.io/badge/C++-17-blue.svg)](https://isocpp.org/)
[![OpenAI Whisper](https://img.shields.io/badge/OpenAI-Whisper-green.svg)](https://github.com/openai/whisper)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

![Banner](https://via.placeholder.com/1200x300/1a1a2e/ffffff?text=NotYCaptionGenAi+-+Smart+Subtitles+Generator)

## ✨ Features

- 🎯 **Multi-Format Support**: Audio/Video files (.wav, .mp4, .mp3, .m4a, .mkv, .avi, .wmv, .mpeg, .flac)
- 🔊 **Automatic Audio Extraction**: Extracts audio from video files to WAV format
- 🤖 **AI-Powered Transcription**: Uses OpenAI's Whisper model for accurate speech-to-text
- 🌍 **Multi-Language Support**: Supports all languages with English transliteration
- ✍️ **Letter Spacing Control**: Customize maximum characters per line
- 📝 **SRT Format Output**: Industry-standard subtitle format with precise timestamps
- 🚀 **Simple UI**: Easy-to-use command-line interface

## 📋 Prerequisites

- **CMake** (3.10+)
- **C++17 Compiler** (GCC 7+, Clang 5+, MSVC 2017+)
- **FFmpeg** (for audio extraction)
- **OpenAI Whisper** (C++ implementation)
- **OpenBLAS** (for Whisper dependencies)

## 🔧 Installation

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install cmake build-essential ffmpeg libavcodec-dev libavformat-dev libavutil-dev libswresample-dev
sudo apt-get install libopenblas-dev libsndfile1-dev
```
### MacOS
```bash
brew install cmake ffmpeg openblas libsndfile
```
### WINDOWS
```bash
# Install via vcpkg or manually download dependencies
vcpkg install ffmpeg openblas libsndfile
```

