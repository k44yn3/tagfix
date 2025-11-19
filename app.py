from flask import Flask, render_template, request, jsonify, send_file
import os
import tagfix
from typing import List, Dict
import io
import base64

app = Flask(__name__)

# Ensure we can find files relative to where the script is run
BASE_DIR = os.path.abspath(os.getcwd())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan_directory():
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({'error': 'No path provided'}), 400
    
    normalized_path = tagfix.normalize_input_path(path)
    if not os.path.exists(normalized_path):
        return jsonify({'error': 'Path does not exist'}), 404
        
    audio_files = tagfix.resolve_audio_targets(normalized_path)
    
    results = []
    for f in audio_files:
        audio = tagfix.load_audio_file(f)
        if not audio:
            continue
            
        metadata = {}
        for tag in ['title', 'artist', 'album', 'year', 'genre']:
            val = tagfix.get_tag_value(audio, tag if tag != 'year' else 'date', f)
            metadata[tag] = val if val else ""
            
        results.append({
            'path': f,
            'filename': os.path.basename(f),
            'metadata': metadata
        })
        
    return jsonify({'files': results, 'count': len(results)})

@app.route('/api/update', methods=['POST'])
def update_metadata():
    data = request.json
    files = data.get('files', [])
    updates = data.get('updates', {})
    
    if not files or not updates:
        return jsonify({'error': 'Missing files or updates'}), 400
        
    success_count = 0
    failed_files = []
    
    for fpath in files:
        try:
            audio = tagfix.load_audio_file(fpath)
            if not audio:
                failed_files.append(fpath)
                continue
                
            for tag, value in updates.items():
                if tag == 'filename':
                    # Handle rename
                    new_path = tagfix.rename_audio_file(fpath, value)
                    # Update fpath for subsequent operations if any (though usually rename is last or standalone)
                    # But we might need to return the new path to the frontend
                    fpath = new_path 
                else:
                    # Map 'year' back to 'date' for tagfix
                    tag_key = 'date' if tag == 'year' else tag
                    tagfix.set_tag_value(audio, tag_key, value, fpath)
            
            audio.save()
            success_count += 1
        except Exception as e:
            print(f"Error updating {fpath}: {e}")
            failed_files.append(fpath)
            
    return jsonify({
        'success': success_count,
        'failed': len(failed_files),
        'failed_files': failed_files
    })

@app.route('/api/cover', methods=['GET'])
def get_cover():
    path = request.args.get('path')
    if not path or not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
        
    cover_data = tagfix.get_cover_art(path)
    if cover_data:
        return send_file(io.BytesIO(cover_data), mimetype='image/jpeg')
    else:
        # Return a placeholder or 404. Let's return 404 so frontend shows default icon
        return "", 404

@app.route('/api/cover/upload', methods=['POST'])
def upload_cover():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    target_path = request.form.get('target_path')
    
    if not file or not target_path:
        return jsonify({'error': 'Missing file or target path'}), 400
        
    if not os.path.exists(target_path):
        return jsonify({'error': 'Target file not found'}), 404
        
    try:
        image_data = file.read()
        success = tagfix.set_cover_art(target_path, image_data, file.mimetype)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to set cover art'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/convert', methods=['POST'])
def convert_files():
    data = request.json
    files = data.get('files', [])
    format_type = data.get('format', 'wav') # wav or flac
    
    if not files:
        return jsonify({'error': 'No files provided'}), 400
        
    if format_type == 'wav':
        stats = tagfix.convert_to_wav_logic(files)
    elif format_type == 'flac':
        stats = tagfix.convert_to_flac_logic(files)
    else:
        return jsonify({'error': 'Invalid format'}), 400
        
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
