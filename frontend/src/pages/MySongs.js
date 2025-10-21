import React from 'react';
import { Play, Edit2, Trash2, MoreVertical } from 'lucide-react';
import { Button } from '../components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import './MySongs.css';

export function MySongs({ songs, searchQuery, onPlay, onEdit, onDelete }) {
  const filteredSongs = songs.filter((song) => {
    const query = searchQuery.toLowerCase();
    return (
      song.title.toLowerCase().includes(query) ||
      song.artist.toLowerCase().includes(query) ||
      (song.album && song.album.toLowerCase().includes(query)) ||
      (song.genre && song.genre.toLowerCase().includes(query))
    );
  });

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatSize = (bytes) => {
    if (!bytes) return 'N/A';
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="mysongs">
      <div className="mysongs-header">
        <h2>My Songs</h2>
        <p>Your personal music library</p>
      </div>

      <div className="mysongs-table-container">
        <Table>
          <TableHeader>
            <TableRow className="mysongs-table-header-row">
              <TableHead className="mysongs-table-index"></TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Artist</TableHead>
              <TableHead>Album</TableHead>
              <TableHead>Genre</TableHead>
              <TableHead>Duration</TableHead>
              <TableHead>Size</TableHead>
              <TableHead className="mysongs-table-actions">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredSongs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="mysongs-empty">
                  {searchQuery ? 'No songs found matching your search' : 'No songs in your library yet'}
                </TableCell>
              </TableRow>
            ) : (
              filteredSongs.map((song, index) => (
                <TableRow key={song.id} className="mysongs-table-row">
                  <TableCell className="mysongs-index">{index + 1}</TableCell>
                  <TableCell>
                    <div className="mysongs-title-cell">
                      <button
                        onClick={() => onPlay(song)}
                        className="mysongs-play-btn"
                      >
                        <Play size={16} />
                      </button>
                      <span>{song.title}</span>
                    </div>
                  </TableCell>
                  <TableCell>{song.artist}</TableCell>
                  <TableCell>{song.album || 'Unknown'}</TableCell>
                  <TableCell>
                    <span className="mysongs-genre-badge">
                      {song.genre || 'Unknown'}
                    </span>
                  </TableCell>
                  <TableCell>{formatDuration(song.duration)}</TableCell>
                  <TableCell>{formatSize(song.file_size)}</TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="mysongs-menu-btn">
                          <MoreVertical size={16} />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onEdit(song)}>
                          <Edit2 size={14} className="mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => onDelete(song)}
                          className="text-red-600"
                        >
                          <Trash2 size={14} className="mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
