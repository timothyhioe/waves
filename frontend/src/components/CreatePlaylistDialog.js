import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';

export function CreatePlaylistDialog({ open, onOpenChange, onCreate }) {
  const [name, setName] = useState('');
  const [selectedColor, setSelectedColor] = useState('#26c6da');

  const colors = [
    '#26c6da',
    '#4dd0e1',
    '#1e88e5',
    '#7e57c2',
    '#ec407a',
    '#ff7043',
    '#66bb6a',
    '#ffa726',
  ];

  const adjustColor = (color, amount) => {
    const hex = color.replace('#', '');
    const num = parseInt(hex, 16);
    const r = Math.max(0, Math.min(255, (num >> 16) + amount));
    const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00ff) + amount));
    const b = Math.max(0, Math.min(255, (num & 0x0000ff) + amount));
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`;
  };

  const handleCreate = () => {
    if (name.trim()) {
      onCreate(name, selectedColor);
      setName('');
      setSelectedColor('#26c6da');
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle>Create New Playlist</DialogTitle>
          <DialogDescription>
            Choose a name and color for your playlist
          </DialogDescription>
        </DialogHeader>

        <div style={{ display: 'grid', gap: '1.5rem', padding: '1rem 0' }}>
          <div>
            <Label htmlFor="playlist-name">Playlist Name</Label>
            <Input
              id="playlist-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My Awesome Playlist"
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
            />
          </div>

          <div>
            <Label>Cover Color</Label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: '0.5rem', marginTop: '0.5rem' }}>
              {colors.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setSelectedColor(color)}
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '8px',
                    backgroundColor: color,
                    border: selectedColor === color ? '3px solid #0a2342' : 'none',
                    transform: selectedColor === color ? 'scale(1.1)' : 'scale(1)',
                    transition: 'all 0.2s ease',
                    cursor: 'pointer',
                  }}
                />
              ))}
            </div>
          </div>

          {/* Preview */}
          <div>
            <Label>Preview</Label>
            <div style={{ marginTop: '0.5rem', padding: '1rem', background: '#f9fafb', borderRadius: '12px' }}>
              <div
                style={{
                  height: '128px',
                  borderRadius: '12px',
                  background: `linear-gradient(135deg, ${selectedColor}, ${adjustColor(selectedColor, -20)})`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <p style={{ color: 'white', fontSize: '1.125rem' }}>{name || 'Playlist Name'}</p>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            disabled={!name.trim()}
            style={{
              background: 'linear-gradient(to right, #26c6da, #4dd0e1)',
              color: 'white',
            }}
          >
            Create Playlist
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
