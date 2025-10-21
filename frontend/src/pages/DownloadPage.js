import React, { useState } from 'react';
import { Search, Download as DownloadIcon, Youtube, Play } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from '../components/ui/sonner';
import './DownloadPage.css';

export function DownloadPage({ onDownload }) {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [isDownloading, setIsDownloading] = useState({});

  const formatDuration = (seconds) => {
    if (!seconds || seconds <= 0) return '--:--';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    setSearchResults([]);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:5000/api/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
        if (data.results?.length === 0) {
          toast.info('No results found', {
            description: 'Try a different search term',
          });
        }
      } else {
        const error = await response.json();
        toast.error('Search failed', {
          description: error.error || 'Please try again',
        });
      }
    } catch (error) {
      console.error('Search error:', error);
      toast.error('Search failed', {
        description: 'Network error. Please try again.',
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleDownloadClick = async (song) => {
    if (!song.youtube_url) {
      toast.error('No YouTube URL available for this song');
      return;
    }

    setIsDownloading((prev) => ({ ...prev, [song.id]: true }));

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          youtube_url: song.youtube_url,
          song_info: song,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success('Song downloaded successfully!', {
          description: `${song.title} has been added to your library`,
        });
        if (onDownload) onDownload(data);
        // Remove downloaded song from results
        setSearchResults(searchResults.filter(s => s.id !== song.id));
      } else {
        toast.error('Download failed', {
          description: data.error || 'Please try again',
        });
      }
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Download failed', {
        description: 'Network error. Please try again.',
      });
    } finally {
      setIsDownloading((prev) => ({ ...prev, [song.id]: false }));
    }
  };

  return (
    <div className="download">
      <div className="download-header">
        <h2>Download from YouTube</h2>
        <p>Search and download songs from YouTube to add to your library</p>
      </div>

      {/* Search Section */}
      <div className="download-search-container">
        <div className="download-search">
          <Search className="download-search-icon" size={20} />
          <input
            type="text"
            placeholder="Search for songs, artists, albums..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="download-search-input"
          />
          <Button
            onClick={handleSearch}
            disabled={isSearching || !query.trim()}
            className="download-search-btn"
          >
            <Search size={18} className="mr-2" />
            {isSearching ? 'Searching...' : 'Search'}
          </Button>
        </div>
      </div>

      {/* Search Results Table */}
      {searchResults.length > 0 ? (
        <div className="download-results">
          <div className="download-results-header">
            <h3>Found {searchResults.length} results</h3>
          </div>

          <div className="download-table">
            <div className="download-table-header">
              <div className="col-play"></div>
              <div className="col-title">Title</div>
              <div className="col-artist">Artist</div>
              <div className="col-source">Source</div>
              <div className="col-duration">Duration</div>
              <div className="col-actions">Actions</div>
            </div>

            <div className="download-table-body">
              {searchResults.map((song, index) => (
                <div
                  key={`${song.source}-${song.id}-${index}`}
                  className="download-table-row"
                >
                  <div className="col-play">
                    <button
                      className="download-play-btn"
                      onClick={() => window.open(song.youtube_url, '_blank')}
                      title="Preview on YouTube"
                    >
                      <Play size={16} />
                    </button>
                  </div>
                  <div className="col-title">
                    <div className="song-title">{song.title}</div>
                  </div>
                  <div className="col-artist">{song.artist}</div>
                  <div className="col-source">
                    <span className="source-tag">
                      <Youtube size={14} />
                      {song.source}
                    </span>
                  </div>
                  <div className="col-duration">
                    {formatDuration(song.duration)}
                  </div>
                  <div className="col-actions">
                    <button
                      className="download-action-btn"
                      onClick={() => handleDownloadClick(song)}
                      disabled={isDownloading[song.id]}
                      title="Download song"
                    >
                      <DownloadIcon size={16} />
                      {isDownloading[song.id] ? 'Downloading...' : 'Download'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : query && !isSearching ? (
        <div className="download-empty">
          <Search size={64} className="download-empty-icon" />
          <h3>No results found</h3>
          <p>Try a different search term</p>
        </div>
      ) : (
        <div className="download-info">
          <Youtube size={64} className="download-info-icon" />
          <h3 className="download-info-title">Search for Songs</h3>
          <p className="download-info-text">
            1. Enter a song name, artist, or album<br />
            2. Click Search to find results<br />
            3. Preview songs on YouTube<br />
            4. Click Download to add to your library
          </p>
        </div>
      )}
    </div>
  );
}
