```javascript
// Initialize app - use both DOMContentLoaded and window.onload for pywebview compatibility
function initApp() {
    if (window.appInitialized) {
        console.log('App already initialized, skipping...');
        return;
    }
    
    console.log('Initializing TagFix app...');

    const pathInput = document.getElementById('path-input');
    const scanBtn = document.getElementById('scan-btn');
    const fileList = document.getElementById('file-list');
    const saveFab = document.getElementById('save-fab');
    const convertFab = document.getElementById('convert-fab');
    const convertDialog = document.getElementById('convert-dialog');
    const cancelConvertBtn = document.getElementById('cancel-convert');
    const confirmConvertBtn = document.getElementById('confirm-convert');

    if (!pathInput || !scanBtn || !fileList) {
        console.error('Required elements not found, retrying...');
        setTimeout(initApp, 100);
        return;
    }

    console.log('All elements found, setting up event listeners...');

    let currentFiles = [];
    let modifiedFiles = new Set();

    // Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = themeToggleBtn.querySelector('span');

    // Check local storage
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
        themeIcon.textContent = 'light_mode';
    }

    themeToggleBtn.addEventListener('click', () => {
        console.log('Theme toggle clicked');
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        themeIcon.textContent = isDark ? 'light_mode' : 'dark_mode';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    // Mark as initialized
    window.appInitialized = true;
    console.log('App initialization complete!');

    // Scan Directory
    scanBtn.addEventListener('click', async () => {
        console.log('Scan button clicked!');
        const path = pathInput.value;
        console.log('Path value:', path);
        if (!path) {
            console.log('No path provided');
            return;
        }

        fileList.innerHTML = '<div class="empty-state"><p>Scanning...</p></div>';

        try {
            const response = await fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });

            const data = await response.json();

            if (data.error) {
                fileList.innerHTML = `< div class="empty-state" > <p>Error: ${data.error}</p></div > `;
                return;
            }

            currentFiles = data.files;
            renderFiles(currentFiles);
        } catch (e) {
            fileList.innerHTML = `< div class="empty-state" > <p>Network Error: ${e}</p></div > `;
        }
    });

    function renderFiles(files) {
        fileList.innerHTML = '';
        if (files.length === 0) {
            fileList.innerHTML = '<div class="empty-state"><p>No audio files found</p></div>';
            return;
        }

        files.forEach((file, index) => {
            const card = document.createElement('div');
            card.className = 'file-card';
            card.dataset.index = index;

            // Timestamp to bust cache for cover art
            const ts = new Date().getTime();
            const coverUrl = `/ api / cover ? path = ${ encodeURIComponent(file.path) }& ts=${ ts } `;

            card.innerHTML = `
    < div class="card-header" >
                    <div class="filename" title="${file.filename}">${file.filename}</div>
                    <span class="material-symbols-outlined">music_note</span>
                </div >
    <div class="card-content">
        <div class="cover-art-container">
            <img src="${coverUrl}" class="cover-art" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2NjYzIiPjxwYXRoIGQ9M00xMiAzdjkuMjhhNC41IDQuNSAwIDEgMC0xLjQ0IDguNzJjNC45NyAxLjM1IDguOTQtMi4yNCA4Ljk0LTcuMzRWN2gtNlYzWiIvPjwvc3ZnPg=='">
                <label class="cover-upload-btn">
                    Change Cover
                    <input type="file" accept="image/*" style="display: none;" class="cover-input">
                </label>
        </div>
        <div class="metadata-grid">
            <div class="input-group full-width">
                <label>Filename</label>
                <input type="text" data-field="filename" value="${file.filename}">
            </div>
            <div class="input-group">
                <label>Title</label>
                <input type="text" data-field="title" value="${file.metadata.title || ''}">
            </div>
            <div class="input-group">
                <label>Artist</label>
                <input type="text" data-field="artist" value="${file.metadata.artist || ''}">
            </div>
            <div class="input-group">
                <label>Album</label>
                <input type="text" data-field="album" value="${file.metadata.album || ''}">
            </div>
            <div class="input-group">
                <label>Genre</label>
                <input type="text" data-field="genre" value="${file.metadata.genre || ''}">
            </div>
        </div>
    </div>
`;

            // Track changes
            const inputs = card.querySelectorAll('input[type="text"]');
            inputs.forEach(input => {
                input.addEventListener('input', (e) => {
                    const field = e.target.dataset.field;

                    if (field === 'filename') {
                        // Special handling for filename? 
                        // For now, just treat as another metadata field to update
                        // The backend will handle the rename logic
                        file.metadata['filename'] = e.target.value;
                    } else {
                        file.metadata[field] = e.target.value;
                    }

                    modifiedFiles.add(file.path);
                    card.classList.add('modified');
                });
            });

            // Handle Cover Upload
            const coverInput = card.querySelector('.cover-input');
            coverInput.addEventListener('change', async (e) => {
                if (e.target.files && e.target.files[0]) {
                    const formData = new FormData();
                    formData.append('file', e.target.files[0]);
                    formData.append('target_path', file.path);

                    try {
                        const res = await fetch('/api/cover/upload', {
                            method: 'POST',
                            body: formData
                        });
                        const resData = await res.json();
                        if (resData.success) {
                            // Refresh cover image
                            const img = card.querySelector('.cover-art');
                            img.src = `/ api / cover ? path = ${ encodeURIComponent(file.path) }& ts=${ new Date().getTime() } `;
                        } else {
                            alert('Failed to upload cover: ' + resData.error);
                        }
                    } catch (err) {
                        alert('Error uploading cover: ' + err);
                    }
                }
            });

            fileList.appendChild(card);
        });
    }

    // Save Changes
    saveFab.addEventListener('click', async () => {
        if (modifiedFiles.size === 0) {
            alert('No changes to save');
            return;
        }

        const updates = {}; // In a real app, we'd map per-file updates more carefully
        // For this simplified version, we'll just send the current state of modified files

        // Actually, the backend expects {files: [], updates: {tag: val}} for batch updates
        // or we need a new endpoint for per-file updates.
        // Let's assume we iterate and send updates one by one for now or batch them if they share values.
        // To keep it simple for this demo, let's just update the files that changed.

        // Wait, the backend `update_metadata` does batch update (same value for all files).
        // We need to refactor backend or loop here. Let's loop here.

        let successCount = 0;

        for (const fpath of modifiedFiles) {
            const file = currentFiles.find(f => f.path === fpath);
            if (!file) continue;

            try {
                await fetch('/api/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        files: [fpath],
                        updates: file.metadata
                    })
                });
                successCount++;
            } catch (e) {
                console.error(e);
            }
        }

        alert(`Saved ${ successCount } files.`);
        modifiedFiles.clear();
        document.querySelectorAll('.file-card.modified').forEach(el => el.classList.remove('modified'));

        // Re-scan to update paths (in case of renames)
        scanBtn.click();
    });

    // Convert Dialog
    convertFab.addEventListener('click', () => {
        if (currentFiles.length === 0) {
            alert('No files to convert');
            return;
        }
        convertDialog.showModal();
    });

    cancelConvertBtn.addEventListener('click', () => {
        convertDialog.close();
    });

    confirmConvertBtn.addEventListener('click', async () => {
        const format = document.querySelector('input[name="format"]:checked').value;
        const files = currentFiles.map(f => f.path);

        convertDialog.close();

        // Show loading indicator
        const originalText = convertFab.innerHTML;
        convertFab.innerHTML = '<span class="material-symbols-outlined">hourglass_empty</span> Converting...';

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files, format })
            });

            const stats = await response.json();
            alert(`Conversion Complete!\nConverted: ${ stats.converted } \nFailed: ${ stats.failed } `);
        } catch (e) {
            alert('Conversion failed: ' + e);
        } finally {
            convertFab.innerHTML = originalText;
        }
    });
}

// Try multiple initialization methods for pywebview compatibility
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    // DOM already loaded
    initApp();
}

// Fallback for pywebview
window.addEventListener('load', function () {
    if (!window.appInitialized) {
        initApp();
    }
});
