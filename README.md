# TagFix

A powerful audio metadata editor supporting FLAC, MP3, M4A, OGG, OPUS, WMA, and WAV formats.

## 1. Flutter App (Recommended)

The modern, cross-platform desktop application with a beautiful Material You interface.

### Prerequisites

-   **Flutter SDK**: Install from [flutter.dev](https://flutter.dev/docs/get-started/install)
-   **Build Tools**:
    -   **Linux**: `sudo apt-get install clang cmake ninja-build pkg-config libgtk-3-dev liblzma-dev`
    -   **Windows**: Visual Studio 2022 with "Desktop development with C++"
    -   **macOS**: Xcode

### Building

#### Linux
```bash
cd flutter_app
flutter create .
```

## Running

```bash
flutter run -d linux  # or windows, macos
```

## Features

- **Material You Design**: Dynamic theming based on seed color.
- **Cross-Platform**: Runs natively on desktop.
- **Metadata Editing**: Edit Title, Artist, Album, Year, Genre, Track/Disc numbers.
- **Cover Art**: View and update cover art.
- **Conversion**: Convert files to WAV or FLAC using system FFmpeg.
- **Recursive Scanning**: Scan folders for audio files.

## Project Structure

- `lib/models`: Data models (`AudioFile`).
- `lib/services`: Core logic (`FileService`, `TagService`, `FfmpegService`).
- `lib/providers`: State management (`AppState`).
- `lib/screens`: UI Screens (`MainScreen`).
- `lib/widgets`: Reusable widgets (`FileList`, `EditorPanel`, `CoverArtWidget`).

=======
flutter pub get
flutter build linux --release
```
The executable will be in `build/linux/x64/release/bundle/tagfix`.

#### Windows
```bash
cd flutter_app
flutter pub get
flutter build windows --release
```
The executable will be in `build\windows\runner\Release\tagfix.exe`.

#### macOS
```bash
cd flutter_app
flutter pub get
flutter build macos --release
```
The app bundle will be in `build/macos/Build/Products/Release/tagfix.app`.

---

## 2. CLI Version

The original Python-based command line interface and Tkinter GUI.

### Prerequisites
-   Python 3.8+
-   FFmpeg (for format conversion)

### Installation
```bash
pip install -r requirements.txt
```

### Usage
Run the script to open the GUI:
```bash
python3 tagfix.py
```

Or import it as a module for scripting.

---

## 3. Web Version

A web-based interface for TagFix, perfect for headless servers or remote access.

### Prerequisites
-   Python 3.8+
-   Flask

### Installation
```bash
pip install -r requirements.txt
```

### Usage
Start the web server:
```bash
python3 app.py
```
Open your browser and navigate to `http://localhost:5000`.
