#!/usr/bin/env python3
"""
Audio Metadata Editor - Complete Version
Supports FLAC, MP3, M4A, OGG, OPUS, WMA, and WAV formats.
Includes Album Cover (option 1) with online/local selection and popup preview.
"""

import os
import sys
import tempfile
import requests
from PIL import Image, ImageTk
import tkinter as tk
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.wave import WAVE
from mutagen.asf import ASF
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2, TCON, TDRC, TRCK, TPOS, COMM, APIC
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

try:
    import musicbrainzngs
    musicbrainzngs.set_useragent("AudioMetadataEditor", "1.0", "")
except ImportError:
    print("Warning: musicbrainzngs not installed. Online cover fetch will not work.")

# ===================== SETTINGS =====================
AVAILABLE_TAGS = {
    "1": "cover",       # Album cover is now option 1
    "2": "artist",
    "3": "albumartist",
    "4": "album",
    "5": "title",
    "6": "genre",
    "7": "date",
    "8": "tracknumber",
    "9": "discnumber",
    "10": "comment"
}

GLOBAL_TAGS = {"artist", "albumartist", "album", "date", "genre"}
SUPPORTED_EXTENSIONS = {'.flac', '.mp3', '.m4a', '.ogg', '.opus', '.wma', '.wav'}

ID3_TAG_MAP = {
    'title': TIT2,
    'artist': TPE1,
    'album': TALB,
    'albumartist': TPE2,
    'genre': TCON,
    'date': TDRC,
    'tracknumber': TRCK,
    'discnumber': TPOS,
    'comment': COMM
}

MP4_TAG_MAP = {
    'title': '\xa9nam',
    'artist': '\xa9ART',
    'album': '\xa9alb',
    'albumartist': 'aART',
    'genre': '\xa9gen',
    'date': '\xa9day',
    'tracknumber': 'trkn',
    'discnumber': 'disk',
    'comment': '\xa9cmt'
}

# ===================== AUDIO UTILITIES =====================
def find_audio_files(base_dir: str) -> List[str]:
    base_dir = os.path.expanduser(base_dir.strip().strip('"').strip("'"))
    if not os.path.exists(base_dir):
        print(f"Error: Directory '{base_dir}' does not exist.")
        return []
    if not os.path.isdir(base_dir):
        print(f"Error: '{base_dir}' is not a directory.")
        return []
    audio_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if os.path.splitext(file.lower())[1] in SUPPORTED_EXTENSIONS:
                audio_files.append(os.path.join(root, file))
    return sorted(audio_files)

def load_audio_file(filepath: str):
    ext = os.path.splitext(filepath.lower())[1]
    try:
        if ext == '.flac':
            return FLAC(filepath)
        elif ext == '.mp3':
            return MP3(filepath)
        elif ext == '.m4a':
            return MP4(filepath)
        elif ext == '.ogg':
            return OggVorbis(filepath)
        elif ext == '.opus':
            return OggOpus(filepath)
        elif ext == '.wma':
            return ASF(filepath)
        elif ext == '.wav':
            return WAVE(filepath)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None
    return None

def get_tag_value(audio, tag: str, filepath: str) -> Optional[str]:
    ext = os.path.splitext(filepath.lower())[1]
    try:
        if ext in ('.mp3', '.wav'):
            if not hasattr(audio, 'tags') or audio.tags is None:
                return None
            tag_class = ID3_TAG_MAP.get(tag)
            if tag_class and tag_class.__name__ in audio.tags:
                return str(audio.tags[tag_class.__name__].text[0])
            return None
        elif ext == '.m4a':
            mp4_tag = MP4_TAG_MAP.get(tag)
            if mp4_tag and mp4_tag in audio.tags:
                value = audio.tags[mp4_tag]
                if tag in ('tracknumber', 'discnumber'):
                    return str(value[0][0]) if value and value[0] else None
                return str(value[0]) if value else None
            return None
        else:
            if tag in audio:
                return str(audio[tag][0]) if audio[tag] else None
            return None
    except Exception:
        return None

def set_tag_value(audio, tag: str, value: str, filepath: str) -> bool:
    ext = os.path.splitext(filepath.lower())[1]
    try:
        if ext in ('.mp3', '.wav'):
            if not hasattr(audio, 'tags') or audio.tags is None:
                audio.add_tags()
            tag_class = ID3_TAG_MAP.get(tag)
            if tag_class:
                if tag == 'comment':
                    audio.tags[tag_class.__name__] = tag_class(encoding=3, lang='eng', desc='', text=value)
                else:
                    audio.tags[tag_class.__name__] = tag_class(encoding=3, text=value)
            return True
        elif ext == '.m4a':
            mp4_tag = MP4_TAG_MAP.get(tag)
            if mp4_tag:
                if tag in ('tracknumber', 'discnumber'):
                    audio.tags[mp4_tag] = [(int(value), 0)]
                else:
                    audio.tags[mp4_tag] = [value]
            return True
        else:
            audio[tag] = [value]
            return True
    except Exception as e:
        print(f"  Warning: Could not set {tag}: {e}")
        return False

# ===================== METADATA ANALYSIS =====================
def analyze_metadata(audio_files: List[str], selected_tags: List[str]) -> Dict[str, Dict]:
    metadata_map = defaultdict(lambda: defaultdict(list))
    for filepath in audio_files:
        audio = load_audio_file(filepath)
        if audio is None:
            continue
        filename = os.path.basename(filepath)
        for tag in selected_tags:
            value = get_tag_value(audio, tag, filepath)
            metadata_map[tag][value if value else "[Not Set]"].append(filename)
    return metadata_map

def display_metadata_analysis(metadata_map: Dict[str, Dict], tag: str, audio_files: List[str]) -> None:
    print(f"\nCurrent {tag.title()} Values:")
    print("-" * 60)
    tag_data = metadata_map.get(tag, {})
    if not tag_data:
        print("  No metadata found")
        return
    sorted_values = sorted(tag_data.items(), key=lambda x: (x[0] == "[Not Set]", x[0]))
    for value, files in sorted_values:
        count = len(files)
        total = len(audio_files)
        percentage = (count / total * 100) if total > 0 else 0
        print(f"  '{value}' - {count} file(s) ({percentage:.1f}%)")
        if count <= 3:
            for f in files:
                print(f"    - {f}")
        else:
            for f in files[:2]:
                print(f"    - {f}")
            print(f"    ... and {count - 2} more")

# ===================== ALBUM COVER FUNCTIONS =====================
def fetch_cover_musicbrainz(artist: str, album: str) -> Optional[str]:
    try:
        results = musicbrainzngs.search_releases(artist=artist, release=album, limit=1)
        if not results['release-list']:
            return None
        mbid = results['release-list'][0]['id']
        image_info = musicbrainzngs.get_image_list(mbid)
        if not image_info['images']:
            return None
        image_url = image_info['images'][0]['image']
        resp = requests.get(image_url)
        if resp.status_code != 200:
            return None
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(resp.content)
        temp_file.close()
        return temp_file.name
    except Exception:
        return None

def show_image_popup(image_path: str):
    img = Image.open(image_path).convert("RGB")  # Original image
    root = tk.Tk()
    root.title("Album Cover Preview")

    # Create canvas with scrollbars
    canvas = tk.Canvas(root, width=800, height=600)
    hbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
    vbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    hbar.pack(side=tk.BOTTOM, fill=tk.X)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Place image on canvas
    tk_img = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.config(scrollregion=(0, 0, img.width, img.height))
    canvas.image = tk_img  # Keep reference

    root.update()
    return root, img

def process_album_cover(audio_folder: str):
    audio_files = find_audio_files(audio_folder)
    if not audio_files:
        print("No audio files found in the folder.")
        return
    first_audio = load_audio_file(audio_files[0])
    album = get_tag_value(first_audio, 'album', audio_files[0]) or ""
    artist = get_tag_value(first_audio, 'artist', audio_files[0]) or ""
    print(f"\nAlbum detected: {album}")
    print(f"Artist detected: {artist}\n")
    print("Choose album cover source:")
    print("[1] Search online (MusicBrainz)")
    print("[2] Provide local image file")
    
    while True:
        choice = input("Your choice [1/2]: ").strip()
        if choice in ('1', '2'):
            break

    cover_path = None

    # Option 1: online search
    if choice == '1':
        if 'musicbrainzngs' not in sys.modules:
            print("MusicBrainz module not available. Switching to local image.")
            choice = '2'
        else:
            print("Searching online for album cover...")
            cover_path = fetch_cover_musicbrainz(artist, album)
            if not cover_path:
                print("No online cover found. Switching to local image.")
                choice = '2'

    # Option 2: local image
    if choice == '2':
        while True:
            local_path = input("Enter local image path: ").strip()
            if os.path.exists(local_path) and os.path.isfile(local_path):
                ext = os.path.splitext(local_path)[1].lower()
                if ext in ('.jpg', '.jpeg', '.png', '.bmp', '.gif'):
                    cover_path = local_path
                    break
                else:
                    print("Unsupported image format. Try jpg/jpeg/png/bmp/gif.")
            else:
                print("File not found. Try again.")

    # Preview original image
    root, img = show_image_popup(cover_path)
    img_size = os.path.getsize(cover_path)
    print(f"\nCover file: {cover_path}")
    print(f"Dimensions: {img.width}x{img.height}")
    print(f"Size: {img_size // 1024} KB")
    while True:
        confirm = input("\nUse this cover? [y]es / [s]kip: ").strip().lower()
        if confirm in ('y', 's'):
            break
    root.destroy()
    if confirm == 's':
        print("Album cover embedding skipped.")
        return

    # Convert only after confirmation
    img = Image.open(cover_path).convert("RGB")
    img = img.resize((500, 500))
    converted_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
    img.save(converted_path, format="JPEG")

    # Embed into all audio files
    for fpath in audio_files:
        audio = load_audio_file(fpath)
        ext = os.path.splitext(fpath.lower())[1]
        with open(converted_path, 'rb') as imgfile:
            img_data = imgfile.read()

        if ext == '.mp3':
            if not hasattr(audio, 'tags') or audio.tags is None:
                audio.add_tags()
            audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img_data))
            audio.save()
        elif ext == '.flac':
            pic = Picture()
            pic.type = 3
            pic.mime = 'image/jpeg'
            pic.desc = 'Cover'
            pic.data = img_data
            audio.clear_pictures()
            audio.add_picture(pic)
            audio.save()
        elif ext == '.m4a':
            audio.tags['covr'] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]
            audio.save()
        elif ext in ('.ogg', '.opus', '.wma'):
            pic = Picture()
            pic.type = 3
            pic.mime = 'image/jpeg'
            pic.desc = 'Cover'
            pic.data = img_data
            audio.clear_pictures()
            audio.add_picture(pic)
            audio.save()

    print(f"Album cover embedded into {len(audio_files)} file(s).")

# ===================== SETUP MENU =====================
def setup_menu(audio_files: List[str]) -> Tuple[List[str], Dict[str,str], List[str]]:
    print("\n" + "=" * 60)
    print("Setup Menu - Select Metadata Fields to Edit")
    print("=" * 60)
    for key, tag in sorted(AVAILABLE_TAGS.items()):
        print(f"  [{key}] {tag.title()}")
    print("\nInstructions: Enter numbers separated by spaces, e.g., 1 2 4")
    while True:
        choices = input("\nYour selection: ").strip().split()
        selected_tags = [AVAILABLE_TAGS[c] for c in choices if c in AVAILABLE_TAGS]
        if selected_tags:
            break
        print("Error: No valid tags selected. Try again.")
    global_values = {}
    per_file_tags = []
    metadata_map = analyze_metadata(audio_files, selected_tags)
    for tag in selected_tags:
        if tag == 'cover':
            continue
        display_metadata_analysis(metadata_map, tag, audio_files)
        if tag in GLOBAL_TAGS:
            print(f"\nOptions for {tag.title()}: [g]lobal / [i]ndividual / [s]kip")
            while True:
                choice = input("Choice: ").strip().lower()
                if choice in ('g','i','s'):
                    break
            if choice == 'g':
                new_val = input(f"New {tag.title()} value: ").strip()
                if new_val:
                    global_values[tag] = new_val
            elif choice == 'i':
                per_file_tags.append(tag)
        else:
            per_file_tags.append(tag)
    return selected_tags, global_values, per_file_tags

# ===================== EDIT AUDIO FILES =====================
def edit_audio_files(audio_files: List[str], selected_tags: List[str], 
                    global_values: Dict[str,str], per_file_tags: List[str]) -> None:
    if not audio_files:
        print("\nNo audio files found.\n")
        return
    # Apply global values
    if global_values:
        for filepath in audio_files:
            audio = load_audio_file(filepath)
            if audio is None:
                continue
            for tag, val in global_values.items():
                set_tag_value(audio, tag, val, filepath)
            audio.save()
    if not per_file_tags:
        print("\nNo per-file edits required. Done.")
        return
    stats = {"processed":0,"skipped":0,"failed":0}
    for idx, path in enumerate(audio_files, start=1):
        audio = load_audio_file(path)
        if audio is None:
            stats["failed"] += 1
            continue
        filename = os.path.basename(path)
        print(f"\n[{idx}/{len(audio_files)}] File: {filename}")
        for tag in per_file_tags:
            current = get_tag_value(audio, tag, path)
            display_current = current if current else "[Not Set]"
            print(f"  {tag.title()}: {display_current}")
        print("Options: [Enter] to edit | [s] skip | [q] quit")
        action = input("Action: ").strip().lower()
        if action == 'q':
            break
        elif action == 's':
            stats["skipped"] += 1
            continue
        modified = False
        for tag in per_file_tags:
            current = get_tag_value(audio, tag, path)
            display_current = f"[{current}]" if current else "[Not Set]"
            new_val = input(f"  {tag.title()} {display_current}: ").strip()
            if new_val:
                set_tag_value(audio, tag, new_val, path)
                modified = True
        if modified:
            audio.save()
            stats["processed"] += 1
        else:
            stats["skipped"] += 1
    print("\nBatch Operation Summary")
    if global_values:
        print(f"  Global edits applied to {len(audio_files)} file(s)")
    print(f"  Per-file processed: {stats['processed']}")
    print(f"  Per-file skipped:   {stats['skipped']}")
    print(f"  Failed:             {stats['failed']}")

# ===================== MAIN LOOP =====================
def main_loop() -> None:
    print("="*60)
    print("Audio Metadata Editor - Complete Version")
    print("="*60)
    while True:
        print("\nEnter directory path to begin (or 0 to exit)")
        directory = input("Directory: ").strip()
        if directory == "0":
            break
        if not directory:
            continue
        audio_files = find_audio_files(directory)
        if not audio_files:
            print("No audio files found in folder.")
            continue
        print(f"Found {len(audio_files)} audio file(s).")
        selected_tags, global_values, per_file_tags = setup_menu(audio_files)
        if "cover" in selected_tags:
            process_album_cover(directory)
        edit_audio_files(audio_files, selected_tags, global_values, per_file_tags)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
