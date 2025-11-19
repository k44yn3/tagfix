// Initialize app - wrapped in function for pywebview compatibility
function initApp() {
    if (window.appInitialized) {
        console.log('App already initialized');
        return;
    }

    console.log('Initializing TagFix...');

    const pathInput = document.getElementById('path-input');
    const scanBtn = document.getElementById('scan-btn');
    const fileList = document.getElementById('file-list');
    const saveFab = document.getElementById('save-fab');
    const convertFab = document.getElementById('convert-fab');
    const convertDialog = document.getElementById('convert-dialog');
    const cancelConvertBtn = document.getElementById('cancel-convert');
    const confirmConvertBtn = document.getElementById('confirm-convert');

    if (!pathInput || !scanBtn) {
        console.error('Elements not found, retrying...');
        setTimeout(initApp, 100);
        return;
    }

    console.log('Elements found, setting up listeners...');

    let currentFiles = [];
    let modifiedFiles = new Set();

    // Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = themeToggleBtn.querySelector('span');

    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
        themeIcon.textContent = 'light_mode';
    }

    themeToggleBtn.addEventListener('click', () => {
        console.log('Theme clicked');
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        themeIcon.textContent = isDark ? 'light_mode' : 'dark_mode';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    // Scan Directory
    scanBtn.addEventListener('click', async () => {
        console.log('Scan clicked');
        const path = pathInput.value;
        if (!path) return;

        fileList.innerHTML = '<div class="empty-state"><p>Scanning...</p></div>';

        try {
            const response = await fetch('/api/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });

            const data = await response.json();

            if (data.error) {
                fileList.innerHTML = `<div class="empty-state"><p>Error: ${data.error}</p></div>`;
                return;
            }

            currentFiles = data.files;
            renderFiles(currentFiles);
        } catch (e) {
            fileList.innerHTML = `<div class="empty-state"><p>Network Error: ${e}</p></div>`;
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

            const ts = new Date().getTime();
            const coverUrl = `/api/cover?path=${encodeURIComponent(file.path)}&ts=${ts}`;

            card.innerHTML = `
                <div class="card-header">
                    <div class="filename" title="${file.filename}">${file.filename}</div>
                    <span class="material-symbols-outlined">music_note</span>
                </div>
                <div class="card-content">
                    <div class="cover-art-container">
                        <img src="${coverUrl}" class="cover-art" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2NjYzIiPjxwYXRoIGQ9Ik0xMiAzdjkuMjhhNC41IDQuNSAwIDEgMC0xLjQ0IDguNzJjNC45NyAxLjM1IDguOTQtMi4yNCA4Ljk0LTcuMzRWN2gtNlYzWiIvPjwvc3ZnPg=='">
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

            const inputs = card.querySelectorAll('input[type="text"]');
            inputs.forEach(input => {
                input.addEventListener('input', (e) => {
                    const field = e.target.dataset.field;
                    if (field === 'filename') {
                        file.metadata['filename'] = e.target.value;
                    } else {
                        file.metadata[field] = e.target.value;
                    }
                    modifiedFiles.add(file.path);
                    card.classList.add('modified');
                });
            });

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
                            const img = card.querySelector('.cover-art');
                            img.src = `/api/cover?path=${encodeURIComponent(file.path)}&ts=${new Date().getTime()}`;
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
        console.log('Save clicked');
        if (modifiedFiles.size === 0) {
            alert('No changes to save');
            return;
        }

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

        alert(`Saved ${successCount} files.`);
        modifiedFiles.clear();
        document.querySelectorAll('.file-card.modified').forEach(el => el.classList.remove('modified'));

        scanBtn.click();
    });

    // Convert Dialog
    convertFab.addEventListener('click', () => {
        console.log('Convert clicked');
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

        const originalText = convertFab.innerHTML;
        convertFab.innerHTML = '<span class="material-symbols-outlined">hourglass_empty</span> Converting...';

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ files, format })
            });

            const stats = await response.json();
            alert(`Conversion Complete!\nConverted: ${stats.converted}\nFailed: ${stats.failed}`);
        } catch (e) {
            alert('Conversion failed: ' + e);
        } finally {
            convertFab.innerHTML = originalText;
        }
    });

    window.appInitialized = true;
    console.log('Initialization complete!');
}

// Multiple initialization attempts for pywebview
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

window.addEventListener('load', function () {
    if (!window.appInitialized) {
        initApp();
    }
});
