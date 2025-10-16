import React, { useState, useRef, useEffect } from "react";
import "./player.css";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import PauseCircleIcon from "@mui/icons-material/PauseCircle";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";
import VolumeDownIcon from "@mui/icons-material/VolumeDown";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";

function Player({ currentSong, songs, setCurrentSong }) {
    const audioRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(0.3);
    const [isMuted, setIsMuted] = useState(false);
    const [prevVolume, setPrevVolume] = useState(0.3);
    const [audioUrl, setAudioUrl] = useState(null);

    // Fetch audio with authentication when song changes
    useEffect(() => {
        if (!currentSong) return;

        const fetchAudio = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(
            `http://localhost:5000/api/songs/${currentSong.id}/stream`,
            {
                headers: {
                Authorization: `Bearer ${token}`,
                },
            },
            );

            if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            setAudioUrl(url);
            } else {
            console.error("Failed to fetch audio:", response.status);
            }
        } catch (error) {
            console.error("Error fetching audio:", error);
        }
        };

        fetchAudio();

        // Cleanup old blob URL
        return () => {
        if (audioUrl) {
            URL.revokeObjectURL(audioUrl);
        }
        };
    }, [currentSong]);

    // Play/pause functionality
    const togglePlayPause = () => {
        if (isPlaying) {
        audioRef.current.pause();
        } else {
        audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    const currentIndex = songs.findIndex((song) => song.id === currentSong.id);

    // Next song
    const handleNext = () => {
        if (currentIndex < songs.length - 1) {
        setCurrentSong(songs[currentIndex + 1]);
        }
    };

    // Previous song
    const handlePrev = () => {
        if (currentIndex > 0) {
        setCurrentSong(songs[currentIndex - 1]);
        }
    };

    // Update progress
    const handleTimeUpdate = () => {
        setCurrentTime(audioRef.current.currentTime);
    };

    // Set duration when metadata loads
    const handleLoadedMetadata = () => {
        setDuration(audioRef.current.duration);
    };

    // Seek to position
    const handleSeek = (e) => {
        const progressBar = e.currentTarget;
        const clickX = e.nativeEvent.offsetX;
        const width = progressBar.offsetWidth;
        const newTime = (clickX / width) * duration;

        audioRef.current.currentTime = newTime;
        setCurrentTime(newTime);
    };

    // Volume control
    const handleVolumeChange = (e) => {
        const newVolume = e.target.value;
        setVolume(newVolume);
        audioRef.current.volume = newVolume;

        if (isMuted && newVolume > 0) {
        setIsMuted(false);
        } else if (newVolume === 0) {
        setIsMuted(true);
        }
    };

    // Mute/unmute
    const toggleMute = () => {
        if (isMuted && prevVolume === 0) {
        setVolume(0.35);
        audioRef.current.volume = 0.3;
        setIsMuted(false);
        } else if (isMuted) {
        setVolume(prevVolume);
        audioRef.current.volume = prevVolume;
        setIsMuted(false);
        } else {
        setPrevVolume(volume);
        setVolume(0);
        audioRef.current.volume = 0;
        setIsMuted(true);
        }
    };

    // Format time display
    const formatTime = (seconds) => {
        if (isNaN(seconds)) return "0:00";
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
    };

    // Auto-play when song changes
    useEffect(() => {
        if (currentSong && audioRef.current) {
        audioRef.current.load();
        setIsPlaying(false);
        setCurrentTime(0);
        }
    }, [currentSong]);

    if (!currentSong) return null;

    return (
        <div className="player">
        <audio
            ref={audioRef}
            src={audioUrl}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={() => setIsPlaying(false)}
            onError={(e) => {
            console.error("Audio error:", e);
            console.error("Audio error code:", e.target.error?.code);
            console.error("Audio error message:", e.target.error?.message);
            console.error("Audio src:", e.target.src);
            }}
            onLoadStart={() => console.log("Audio load started")}
            onCanPlay={() => console.log("Audio can play")}
        />

        {/* Song Info */}
        <div className="player-song-info">
            <div className="song-details">
            <div className="song-title">{currentSong.title}</div>
            <div className="song-artist">{currentSong.artist}</div>
            </div>
        </div>

        {/* Player Controls */}
        <div className="player-controls">
            <div className="control-buttons">
            <button className="control-btn" onClick={handlePrev}>
                <SkipPreviousIcon />
            </button>
            <button className="play-pause-btn" onClick={togglePlayPause}>
                {isPlaying ? (
                <PauseCircleIcon style={{ fontSize: 30 }} />
                ) : (
                <PlayCircleIcon style={{ fontSize: 30 }} />
                )}
            </button>
            <button className="control-btn" onClick={handleNext}>
                <SkipNextIcon />
            </button>
            </div>

            <div className="progress-container">
            <span className="time-display">{formatTime(currentTime)}</span>
            <div className="progress-bar" onClick={handleSeek}>
                <div
                className="progress-fill"
                style={{ width: `${(currentTime / duration) * 100}%` }}
                />
            </div>
            <span className="time-display">{formatTime(duration)}</span>
            </div>
        </div>

        {/* Volume Control */}
        <div className="player-volume">
            <button className="volume-icon" onClick={toggleMute}>
            {isMuted || volume == 0 ? (
                <VolumeOffIcon />
            ) : volume <= 0.4 ? (
                <VolumeDownIcon />
            ) : (
                <VolumeUpIcon />
            )}
            </button>
            <input
            type="range"
            min="0"
            max="0.6"
            step="0.02"
            value={volume}
            onChange={handleVolumeChange}
            className="volume-slider"
            />
        </div>
        </div>
    );
}

export default Player;
