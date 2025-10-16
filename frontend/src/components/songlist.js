import React from "react";
import "./songlist.css";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";

function SongList({ songs, playSong, setSongs }) {
    const formatDuration = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
    };

    const formatFileSize = (bytes) => {
        const mb = (bytes / (1024 * 1024)).toFixed(1);
        return `${mb} MB`;
    };

    const deleteSong = async (songId) => {
        if (window.confirm("Are you sure you want to delete this song?")) {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(
            `http://localhost:5000/api/songs/${songId}`,
            {
                method: "DELETE",
                headers: {
                Authorization: `Bearer ${token}`,
                },
            },
            );

            if (response.ok) {
            // Remove song from local state
            setSongs(songs.filter((song) => song.id !== songId));
            } else {
            alert("Failed to delete song");
            }
        } catch (error) {
            console.error("Error deleting song:", error);
            alert("Error deleting song");
        }
        }
    };

    if (songs.length === 0) {
        return (
        <div className="empty-state">
            <h2>🎵 No songs yet</h2>
            <p>Upload your first song to get started!</p>
        </div>
        );
    }

    return (
        <div className="song-list">
        <div className="song-list-header">
            <h2>My Songs ({songs.length})</h2>
        </div>

        <div className="song-table">
            <div className="table-header">
            <div className="col-play"></div>
            <div className="col-title">Title</div>
            <div className="col-artist">Artist</div>
            <div className="col-album">Album</div>
            <div className="col-genre">Genre</div>
            <div className="col-duration">Duration</div>
            <div className="col-size">Size</div>
            <div className="col-actions">Actions</div>
            </div>

            {songs.map((song, index) => (
            <div key={song.id} className="table-row">
                <div className="col-play">
                <button
                    className="play-btn"
                    onClick={() => playSong(song)}
                    title="Play song"
                >
                    <PlayCircleIcon />
                </button>
                </div>
                <div className="col-title">
                <div className="song-title">{song.title}</div>
                </div>
                <div className="col-artist">{song.artist}</div>
                <div className="col-album">{song.album}</div>
                <div className="col-genre">
                <span className="genre-tag">{song.genre}</span>
                </div>
                <div className="col-duration">{formatDuration(song.duration)}</div>
                <div className="col-size">{formatFileSize(song.file_size)}</div>
                <div className="col-actions">
                <button className="edit-btn" title="Edit metadata">
                    <EditIcon />
                </button>
                <button
                    className="delete-btn"
                    onClick={() => deleteSong(song.id)}
                    title="Delete song"
                >
                    <DeleteIcon />
                </button>
                </div>
            </div>
            ))}
        </div>
        </div>
    );
}

export default SongList;
