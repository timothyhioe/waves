import React, { useEffect, useState } from 'react';
import './App.css';

// Components (we'll create these)
import Sidebar from './components/sidebar';
import SearchBar from './components/searchbar';
import SongList from './components/songlist';
import Player from './components/player';
import UploadPage from './pages/uploadpage';
import DownloadPage from './pages/downloadpage';

function App() {
  const [songs, setSongs] = useState([]);
  const [filteredSongs, setFilteredSongs] = useState([]);
  const [currentPage, setCurrentPage] = useState('songs'); // Fixed: only one initial value
  const [currentSong, setCurrentSong] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [onlineSearchResults, setOnlineSearchResults] = useState([]);

  // Fetch songs from backend
  useEffect(() => {
    fetch('http://localhost:5000/api/songs')
      .then(res => res.json())
      .then(data => {
        console.log('API Response:', data);
        setSongs(data);
        setFilteredSongs(data);
      })
      .catch(err => console.error('Error fetching songs:', err));
  }, []);

  // Filter songs based on search
  useEffect(() => {
    if (searchQuery) {
      const filtered = songs.filter(song => 
        song.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        song.artist.toLowerCase().includes(searchQuery.toLowerCase()) ||
        song.album.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredSongs(filtered);
    } else {
      setFilteredSongs(songs);
    }
  }, [searchQuery, songs]);

  const playSong = (song) => {
    setCurrentSong(song);
  };

  return (
    <div className="app">
      {/* Left Sidebar */}
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      
      {/* Main Content */}
      <div className="main-content">
        {/* Top Search Bar - Fixed parentheses */}
        {(currentPage === 'songs' || currentPage === 'download') && (
          <SearchBar 
            searchQuery={searchQuery} 
            setSearchQuery={setSearchQuery} 
            onlineSearchResults={onlineSearchResults}
            setOnlineSearchResults={setOnlineSearchResults}
          />
        )}
        
        {/* Page Content */}
        <div className="page-content">
          {currentPage === 'songs' ? (
            <SongList songs={filteredSongs} playSong={playSong} setSongs={setSongs} />
          ) : currentPage === 'upload' ? (
            <UploadPage setSongs={setSongs} songs={songs} />
          ) : currentPage === 'download' ? (
            <DownloadPage 
              setSongs={setSongs} 
              songs={songs}
              searchQuery={searchQuery}
              onlineSearchResults={onlineSearchResults}
            />
          ) : null}
        </div>
      </div>
      
      {/* Bottom Player */}
      {currentSong && 
      <Player 
        currentSong={currentSong} 
        songs={songs}
        setCurrentSong={setCurrentSong}
      />}
    </div>
  );
}

export default App;