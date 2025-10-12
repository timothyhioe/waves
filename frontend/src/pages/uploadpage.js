import React, { useState } from 'react';
import './uploadpage.css';

function UploadPage({ setSongs, songs }) {
    const [dragActive, setDragActive] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState([]);

    // Handle drag events
    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
        setDragActive(true);
        } else if (e.type === 'dragleave') {
        setDragActive(false);
        }
    };

    // Handle dropped files
    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFiles(e.dataTransfer.files);
        }
    };

    // Handle selected files
    const handleFileSelect = (e) => {
        if (e.target.files && e.target.files[0]) {
        handleFiles(e.target.files);
        }
    };

    // Upload files
    const handleFiles = async (files) => {
        const audioFiles = Array.from(files).filter(file => 
        file.type.startsWith('audio/') || 
        ['.mp3', '.wav', '.m4a', '.flac', '.ogg'].some(ext => 
            file.name.toLowerCase().endsWith(ext)
        )
        );

        if (audioFiles.length === 0) {
        alert('Please select valid audio files (.mp3, .wav, .m4a, .flac, .ogg)');
        return;
        }

        setUploading(true);
        const newProgress = audioFiles.map(file => ({
        name: file.name,
        progress: 0,
        status: 'uploading'
        }));
        setUploadProgress(newProgress);

        for (let i = 0; i < audioFiles.length; i++) {
        const file = audioFiles[i];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:5000/api/songs', {
            method: 'POST',
            body: formData,
            });

            if (response.ok) {
            const newSong = await response.json();
            setSongs(prevSongs => [...prevSongs, newSong]);
            
            // Update progress
            setUploadProgress(prev => prev.map((item, index) => 
                index === i ? { ...item, progress: 100, status: 'completed' } : item
            ));
            } else {
            setUploadProgress(prev => prev.map((item, index) => 
                index === i ? { ...item, status: 'error' } : item
            ));
            }
        } catch (error) {
            console.error('Upload error:', error);
            setUploadProgress(prev => prev.map((item, index) => 
            index === i ? { ...item, status: 'error' } : item
            ));
        }
        }

        setUploading(false);
        
        // Clear progress after 3 seconds
        setTimeout(() => {
        setUploadProgress([]);
        }, 3000);
    };

    return (
        <div className="upload-page">
        <div className="upload-header">
            <h2>Upload Music</h2>
            <p>Drag and drop your audio files here, or click to browse</p>
        </div>

        <div 
            className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
        >
            <div className="upload-content">
            <div className="upload-icon">🎵</div>
            <h3>Drop your music files here</h3>
            <p>or click to browse your computer</p>
            <div className="supported-formats">
                <small>Supports: MP3, WAV, M4A, FLAC, OGG</small>
            </div>
            </div>

            <input
            id="file-input"
            type="file"
            multiple
            accept="audio/*,.mp3,.wav,.m4a,.flac,.ogg"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            />
        </div>

        {/* Upload Progress */}
        {uploadProgress.length > 0 && (
            <div className="upload-progress">
            <h3>Uploading Files...</h3>
            {uploadProgress.map((item, index) => (
                <div key={index} className="progress-item">
                <div className="progress-info">
                    <span className="file-name">{item.name}</span>
                    <span className={`status ${item.status}`}>
                    {item.status === 'uploading' && '⏳ Uploading...'}
                    {item.status === 'completed' && '✅ Completed'}
                    {item.status === 'error' && '❌ Error'}
                    </span>
                </div>
                {item.status === 'uploading' && (
                    <div className="progress-bar">
                    <div 
                        className="progress-fill"
                        style={{ width: `${item.progress}%` }}
                    />
                    </div>
                )}
                </div>
            ))}
            </div>
        )}

        {/* Upload Tips */}
        <div className="upload-tips">
            <h3>💡 Upload Tips</h3>
            <ul>
            <li>Files without metadata will be enhanced automatically using filename and online databases</li>
            <li>Recommended filename: Artist - Song / Song - Artist</li>
            <li>You can upload multiple files at once</li>
            <li>Supported formats: MP3, WAV, M4A, FLAC, OGG</li>
            <li>Maximum file size: 50MB per file</li>
            </ul>
        </div>
        </div>
    );
}

export default UploadPage;