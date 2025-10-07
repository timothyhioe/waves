import React from 'react';
import './sidebar.css';

function Sidebar({ currentPage, setCurrentPage }) {
    return (
        <div className="sidebar">
        {/* App Title */}
        <div className="sidebar-header">
            <h2>🎵 Waves</h2>
        </div>
        
        {/* Navigation */}
        <div className="sidebar-nav">
            <button 
            className={`nav-item ${currentPage === 'songs' ? 'active' : ''}`}
            onClick={() => setCurrentPage('songs')}
            >
            🎶 My Songs
            </button>
            
            <button 
            className={`nav-item ${currentPage === 'upload' ? 'active' : ''}`}
            onClick={() => setCurrentPage('upload')}
            >
            ⬆️ Upload
            </button>
        </div>
        
        {/* Playlists Section (for later) */}
        <div className="sidebar-section">
            <h3>Playlists</h3>
            <div className="playlist-item">📋 Liked Songs</div>
            <div className="playlist-item">🔥 Recently Played</div>
            <div className="playlist-add">+ Create Playlist</div>
        </div>
        
        {/* Footer */}
        <div className="sidebar-footer">
            <small>Willkommen</small>
        </div>
        </div>
    );
}

export default Sidebar;