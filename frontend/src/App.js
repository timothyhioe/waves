import React, { useEffect, useState } from "react";
import "./App.css";

import LoginPage from "./pages/LoginPage";
import { Sidebar } from "./components/SideBar";
import { TopBar } from "./components/TopBar";
import { MySongs } from "./pages/MySongs";
import { UploadPage } from "./pages/UploadPage";
import { DownloadPage } from "./pages/DownloadPage";
import { PlayerBar } from "./components/PlayerBar";
import { DeleteConfirmDialog } from "./components/DeleteConfirmDialog";
import { EditSongDialog } from "./components/EditSongDialog";
import { CreatePlaylistDialog } from "./components/CreatePlaylistDialog";
import { Toaster, toast } from "./components/ui/sonner";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [songs, setSongs] = useState([]);
  const [currentPage, setCurrentPage] = useState("songs");
  const [currentSong, setCurrentSong] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);

  // Dialog states
  const [deleteDialog, setDeleteDialog] = useState({
    open: false,
    song: null,
  });
  const [editDialog, setEditDialog] = useState({
    open: false,
    song: null,
  });
  const [createPlaylistDialog, setCreatePlaylistDialog] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  // Fetch songs from backend
  const fetchSongs = async () => {
    if (!isAuthenticated) return;

    const token = localStorage.getItem("token");

    try {
      const res = await fetch("http://localhost:5000/api/songs", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.status === 401) {
        // Token expired or invalid
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setIsAuthenticated(false);
        return;
      }

      const data = await res.json();
      const songsArray = Array.isArray(data) ? data : data.songs || [];
      setSongs(songsArray);
    } catch (err) {
      console.error("Error fetching songs:", err);
    }
  };

  useEffect(() => {
    fetchSongs();
  }, [isAuthenticated]);

  // Handlers
  const handlePlaySong = (song) => {
    setCurrentSong(song);
    setIsPlaying(true);
    toast.success(`Now playing: ${song.title}`, {
      description: `By ${song.artist}`,
    });
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleNext = () => {
    if (currentSong && songs.length > 0) {
      const currentIndex = songs.findIndex((s) => s.id === currentSong.id);
      const nextIndex = (currentIndex + 1) % songs.length;
      handlePlaySong(songs[nextIndex]);
    }
  };

  const handlePrevious = () => {
    if (currentSong && songs.length > 0) {
      const currentIndex = songs.findIndex((s) => s.id === currentSong.id);
      const prevIndex = currentIndex === 0 ? songs.length - 1 : currentIndex - 1;
      handlePlaySong(songs[prevIndex]);
    }
  };

  const handleDeleteSong = (song) => {
    setDeleteDialog({ open: true, song });
  };

  const handleConfirmDelete = async () => {
    if (!deleteDialog.song) return;

    const token = localStorage.getItem("token");
    
    try {
      const response = await fetch(`http://localhost:5000/api/songs/${deleteDialog.song.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setSongs(songs.filter((s) => s.id !== deleteDialog.song.id));
        if (currentSong?.id === deleteDialog.song.id) {
          setCurrentSong(null);
          setIsPlaying(false);
        }
        toast.success("Song deleted successfully");
      } else {
        toast.error("Failed to delete song");
      }
    } catch (error) {
      toast.error("Network error. Please try again.");
    }

    setDeleteDialog({ open: false, song: null });
  };

  const handleEditSong = (song) => {
    setEditDialog({ open: true, song });
  };

  const handleSaveSongEdit = async (songId, updates) => {
    const token = localStorage.getItem("token");
    
    try {
      const response = await fetch(`http://localhost:5000/api/songs/${songId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        setSongs(songs.map((s) => (s.id === songId ? { ...s, ...updates } : s)));
        toast.success("Song updated successfully");
      } else {
        toast.error("Failed to update song");
      }
    } catch (error) {
      toast.error("Network error. Please try again.");
    }
  };

  const handleUpload = () => {
    fetchSongs(); // Refresh songs list after upload
  };

  const handleDownload = () => {
    fetchSongs(); // Refresh songs list after download
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setIsAuthenticated(false);
    toast.success("Logged out successfully");
  };

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="app">
      <div className="app-layout">
        {/* Sidebar */}
        <Sidebar
          activeItem={currentPage}
          onNavigate={setCurrentPage}
          onCreatePlaylist={() => setCreatePlaylistDialog(true)}
          onLogout={handleLogout}
        />

        {/* Main Content */}
        <div className="app-main">
          {/* Top Bar */}
          {currentPage === "songs" && (
            <TopBar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onLogout={handleLogout}
            />
          )}

          {/* Content Area */}
          <main className="app-content">
            {currentPage === "songs" && (
              <MySongs
                songs={songs}
                searchQuery={searchQuery}
                onPlay={handlePlaySong}
                onEdit={handleEditSong}
                onDelete={handleDeleteSong}
              />
            )}

            {currentPage === "download" && <DownloadPage onDownload={handleDownload} />}

            {currentPage === "upload" && <UploadPage onUpload={handleUpload} />}

            {currentPage === "playlists" && (
              <div style={{ padding: "1.5rem", textAlign: "center" }}>
                <h2>Playlists Coming Soon!</h2>
                <p style={{ color: "#666" }}>We're working on this feature</p>
              </div>
            )}
          </main>
        </div>
      </div>

      {/* Player Bar */}
      <PlayerBar
        currentSong={currentSong}
        songs={songs}
        setCurrentSong={setCurrentSong}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
        onPlayPause={handlePlayPause}
        onNext={handleNext}
        onPrevious={handlePrevious}
      />

      {/* Modals */}
      <DeleteConfirmDialog
        open={deleteDialog.open}
        onOpenChange={(open) => setDeleteDialog({ ...deleteDialog, open })}
        title="Delete Song"
        description={`Are you sure you want to delete "${deleteDialog.song?.title}"? This action cannot be undone.`}
        onConfirm={handleConfirmDelete}
      />

      <EditSongDialog
        open={editDialog.open}
        onOpenChange={(open) => setEditDialog({ ...editDialog, open })}
        song={editDialog.song}
        onSave={handleSaveSongEdit}
      />

      <CreatePlaylistDialog
        open={createPlaylistDialog}
        onOpenChange={setCreatePlaylistDialog}
        onCreate={(name, color) => {
          toast.success("Playlist created!", {
            description: `${name} has been created`,
          });
        }}
      />

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "white",
            border: "1px solid #26c6da",
            borderRadius: "12px",
          },
        }}
      />
    </div>
  );
}

export default App;
