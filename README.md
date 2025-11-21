# TagFix

A powerful audio metadata editor supporting FLAC, MP3, M4A, OGG, OPUS, WMA, and WAV formats. Available as a modern Desktop App, CLI tool, and Web Interface.

## Download

**[Download the latest release here](https://github.com/k44yn3/tagfix/releases)**

Pre-built binaries are available for:
- **Windows** (Portable .zip)
- **Linux** (Portable .zip)
- **Android** (.apk)

## Features

- **Material Design**: Modern interface with dynamic theming.
- **Metadata Editing**: Edit Title, Artist, Album, Year, Genre, Track/Disc numbers.
- **Cover Art**: View and update album covers.
- **Format Conversion**: Convert files to WAV or FLAC.
- **Recursive Scanning**: Process entire directories at once.
- **Cross-Platform**: Consistent experience across all supported devices.

## Building from Source

### Flutter Desktop & Android

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

# Android
flutter build apk --release
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

TagFix is built with open-source software:

**Flutter Packages:**
- audiotags
- file_picker
- provider
- window_manager
- path_provider
- http
- google_fonts
- desktop_drop
- image

**Python Libraries:**
- Flask
- mutagen
- Pillow
- requests
