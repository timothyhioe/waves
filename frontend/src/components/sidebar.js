import React from "react";
import "./sidebar.css";
import wavesLogo from "../assets/waves-logo.svg";
import LibraryMusicIcon from "@mui/icons-material/LibraryMusic";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import LogoutIcon from "@mui/icons-material/Logout";

function Sidebar({ currentPage, setCurrentPage }) {
    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.reload(); // Reload to show login page
    };

    return (
        <div className="sidebar">
        {/* App Title */}
        <div className="sidebar-header">
            <img src={wavesLogo} alt="Waves Logo" className="sidebar-logo" />
            <h2>Waves</h2>
        </div>

        {/* Navigation */}
        <div className="sidebar-nav">
            <button
            className={`nav-item ${currentPage === "songs" ? "active" : ""}`}
            onClick={() => setCurrentPage("songs")}
            >
            <span>
                {" "}
                <LibraryMusicIcon />{" "}
            </span>
            <span> My Songs </span>
            </button>

            <button
            className={`nav-item ${currentPage === "download" ? "active" : ""}`}
            onClick={() => setCurrentPage("download")}
            >
            <span>
                {" "}
                <CloudDownloadIcon />{" "}
            </span>
            <span> Download </span>
            </button>

            <button
            className={`nav-item ${currentPage === "upload" ? "active" : ""}`}
            onClick={() => setCurrentPage("upload")}
            >
            <span>
                {" "}
                <CloudUploadIcon />{" "}
            </span>
            <span> Upload </span>
            </button>
        </div>

        {/* Playlists Section (for later) */}
        <div className="sidebar-section">
            <h3>Playlists</h3>
            <div className="playlist-add">+ Create Playlist</div>
        </div>

        {/* Footer */}
        <div className="sidebar-footer">
            <button className="logout-button" onClick={handleLogout}>
            <LogoutIcon />
            <span>Logout</span>
            </button>
        </div>
        </div>
    );
}

export default Sidebar;
