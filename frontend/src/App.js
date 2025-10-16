import React, { useEffect, useState } from "react";
import "./App.css";

// Pages
import LoginPage from "./pages/LoginPage";

// Components (we'll create these)
import Sidebar from "./components/sidebar";
import SearchBar from "./components/searchbar";
import SongList from "./components/songlist";
import Player from "./components/player";
import UploadPage from "./pages/uploadpage";
import DownloadPage from "./pages/downloadpage";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [songs, setSongs] = useState([]);
  const [filteredSongs, setFilteredSongs] = useState([]);
  const [currentPage, setCurrentPage] = useState("songs"); // Fixed: only one initial value
  const [currentSong, setCurrentSong] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [onlineSearchResults, setOnlineSearchResults] = useState([]);

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  // Fetch songs from backend
  useEffect(() => {
    if (!isAuthenticated) return;

    const token = localStorage.getItem("token");

    fetch("http://localhost:5000/api/songs", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => {
        if (res.status === 401) {
          // Token expired or invalid
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          setIsAuthenticated(false);
          return;
        }
        return res.json();
      })
      .then((data) => {
        if (data) {
          console.log("API Response:", data);
          // Handle both array and object responses
          const songsArray = Array.isArray(data) ? data : data.songs || [];
          setSongs(songsArray);
          setFilteredSongs(songsArray);
        }
      })
      .catch((err) => console.error("Error fetching songs:", err));
  }, [isAuthenticated]);

  // Filter songs based on search
  useEffect(() => {
    if (searchQuery) {
      const filtered = songs.filter(
        (song) =>
          song.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          song.artist.toLowerCase().includes(searchQuery.toLowerCase()) ||
          song.album.toLowerCase().includes(searchQuery.toLowerCase()),
      );
      setFilteredSongs(filtered);
    } else {
      setFilteredSongs(songs);
    }
  }, [searchQuery, songs]);

  const playSong = (song) => {
    setCurrentSong(song);
  };

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="app">
      {/* Left Sidebar */}
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />

      {/* Main Content */}
      <div className="main-content">
        {/* Top Search Bar - Fixed parentheses */}
        {(currentPage === "songs" || currentPage === "download") && (
          <SearchBar
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            onlineSearchResults={onlineSearchResults}
            setOnlineSearchResults={setOnlineSearchResults}
          />
        )}

        {/* Page Content */}
        <div className="page-content">
          {currentPage === "songs" ? (
            <SongList
              songs={filteredSongs}
              playSong={playSong}
              setSongs={setSongs}
            />
          ) : currentPage === "upload" ? (
            <UploadPage setSongs={setSongs} songs={songs} />
          ) : currentPage === "download" ? (
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
      {currentSong && (
        <Player
          currentSong={currentSong}
          songs={songs}
          setCurrentSong={setCurrentSong}
        />
      )}
    </div>
  );
}

export default App;
