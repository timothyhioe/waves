import React from 'react';
import { Music, Download, Upload, ListMusic, Plus, LogOut } from 'lucide-react';
import WaveLogo from './WaveLogo';
import { Button } from './ui/button';
import './SideBar.css';

export function Sidebar({ activeItem, onNavigate, onCreatePlaylist, onLogout }) {
  const menuItems = [
    { id: 'songs', label: 'My Songs', icon: Music },
    { id: 'download', label: 'Download', icon: Download },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'playlists', label: 'Playlists', icon: ListMusic },
  ];

  return (
    <aside className="sidebar">
      {/* Logo Section */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-content">
          <div style={{ width: '48px', height: '48px' }}>
            <WaveLogo />
          </div>
          <div>
            <h1 className="sidebar-title">Waves</h1>
            <p className="sidebar-subtitle">Open Source</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeItem === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`sidebar-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </button>
          );
        })}

        {/* Create Playlist Button */}
        {activeItem === 'playlists' && (
          <Button
            onClick={onCreatePlaylist}
            variant="outline"
            className="sidebar-create-btn"
          >
            <Plus size={18} className="mr-2" />
            Create Playlist
          </Button>
        )}
      </nav>
    </aside>
  );
}
