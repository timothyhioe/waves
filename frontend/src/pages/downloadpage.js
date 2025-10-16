import React, { useState, useEffect } from "react";
import "./downloadpage.css";
import DownloadIcon from "@mui/icons-material/Download";
import SearchIcon from "@mui/icons-material/Search";
import WebIcon from "@mui/icons-material/Language";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import DownloadingIcon from "@mui/icons-material/Downloading";

function DownloadPage({
  setSongs,
  songs,
  searchQuery,
  onlineSearchResults,
  handleDownload,
}) {
  const [isDownloading, setIsDownloading] = useState({});

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  const handleDownloadClick = async (song) => {
    if (!song.youtube_url) {
      alert("No YouTube URL available for this song");
      return;
    }
    setIsDownloading((prev) => ({ ...prev, [song.id]: true }));

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:5000/api/download", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          youtube_url: song.youtube_url,
          song_info: song,
        }),
      });
      const data = await response.json();

      if (response.ok) {
        alert("Song downloaded successfully!");
        window.location.reload();
      } else {
        alert(`Download failed: ${data.error}`);
      }
    } catch (error) {
      console.error("Download error:", error);
      alert("Download failed");
    } finally {
      setIsDownloading((prev) => ({ ...prev, [song.id]: false }));
    }
  };

  const openYouTubeSearch = (song) => {
    const searchTerm = "${song.artist} ${song.title}".trim();
    window.open(
      `https://www.youtube.com/results?search_query=${encodeURIComponent(searchTerm)}`,
      "_blank",
    );
  };

  return (
    <div className="download-page">
      <div className="download-page-header">
        <h2>
          <WebIcon /> Download Songs
        </h2>
        <p>Search and download songs from YouTube to add to your library</p>
      </div>

      {searchQuery && (
        <div className="search-status">
          <p>
            Search results for: <strong>"{searchQuery}"</strong>
          </p>
        </div>
      )}
      {onlineSearchResults.length === 0 ? (
        <div className="empty-state">
          <SearchIcon sx={{ fontSize: 64, color: "#ccc", marginBottom: 2 }} />
          <h3>No search results</h3>
          <p>Use the search bar above to find songs online</p>
        </div>
      ) : (
        <div className="results-list">
          <div className="results-list-header">
            <h3>Found {onlineSearchResults.length} results</h3>
          </div>

          <div className="results-table">
            <div className="table-header">
              <div className="col-play"></div>
              <div className="col-title">Title</div>
              <div className="col-artist">Artist</div>
              <div className="col-source">Source</div>
              <div className="col-duration">Duration</div>
              <div className="col-actions">Actions</div>
            </div>

            {onlineSearchResults.map((song, index) => (
              <div
                key={`${song.source}-${song.id}-${index}`}
                className="table-row"
              >
                <div className="col-play">
                  <button
                    className="play-btn"
                    onClick={() => window.open(song.youtube_url, "_blank")}
                    title="Preview on YouTube"
                  >
                    <PlayCircleIcon />
                  </button>
                </div>
                <div className="col-title">
                  <div className="song-title">{song.title}</div>
                </div>
                <div className="col-artist">{song.artist}</div>
                <div className="col-source">
                  <span className="source-tag youtube">{song.source}</span>
                </div>
                <div className="col-duration">
                  {song.duration > 0 ? formatDuration(song.duration) : "--:--"}
                </div>
                <div className="col-actions">
                  {song.youtube_url ? (
                    <button
                      className="download-btn"
                      onClick={() => handleDownloadClick(song)}
                      disabled={isDownloading[song.id]}
                      title="Download song"
                    >
                      {isDownloading[song.id] ? (
                        <span className="loading">
                          <DownloadIcon />
                        </span>
                      ) : (
                        <DownloadIcon />
                      )}
                    </button>
                  ) : (
                    <button
                      className="search-btn"
                      onClick={() => openYouTubeSearch(song)}
                      title="Search on YouTube"
                    >
                      <SearchIcon />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
export default DownloadPage;
