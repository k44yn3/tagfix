# TagFix

### **Android release is available [here](https://github.com/k44yn3/tagfixandroid) !!!**

A powerful audio metadata editor supporting FLAC, MP3, M4A, OGG, OPUS, WMA, and WAV formats. Available as a modern Desktop App, CLI tool, and Web Interface.

## Download

**[Download the latest release here](https://github.com/k44yn3/tagfix/releases)**

Pre-built binaries are available for:
- **Windows** (Portable .zip)
- **Linux** (Portable .zip)

## Features

- **Metadata Editing**: Edit Title, Artist, Album, Year, Genre, Track/Disc numbers.
- **Cover Art**: Update album covers(Local/Online).
- **Format Conversion**: Convert files to WAV or FLAC.
- **Recursive Scanning**: Process entire directories at once.
- **Lyrics Embedding**: Embed lyrics into audio files(Local/Online).

## Building from Source

### Flutter Desktop

**Prerequisites:**
- Flutter SDK
- **Linux**: `sudo apt-get install clang cmake ninja-build pkg-config libgtk-3-dev liblzma-dev`
- **Windows**: Visual Studio 2022 with C++ workload

**Build:**
```bash
cd flutter_app
flutter pub get

# Linux
flutter build linux --release

# Windows
flutter build windows --release
```

### CLI & Web Version

**Prerequisites:**
- Python 3.8+
- FFmpeg

**Installation:**
```bash
pip install -r requirements.txt
```

**Usage:**
- **CLI**: `python3 tagfix.py`
- **Web**: `python3 app.py` (Access at `http://localhost:5000`)

## Credits

- Flutter
- FFmpeg for format conversion
- MusicBrainz for online covers fetching
- Lrclib for online lyrics fetching
