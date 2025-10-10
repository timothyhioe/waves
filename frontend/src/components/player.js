import React, { useState, useRef, useEffect } from 'react';
import './player.css';

function Player({ currentSong, songs, setCurrentSong }) {
    const audioRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);

    // Play/pause functionality
    const togglePlayPause = () => {
        if (isPlaying) {
        audioRef.current.pause();
        } else {
        audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    const currentIndex = songs.findIndex(song => song.id === currentSong.id);

    // Next song
    const handleNext = () => {
        if (currentIndex < songs.length - 1) {
            setCurrentSong(songs[currentIndex + 1]);
        }
    }

    // Previous song
    const handlePrev = () => {
        if(currentIndex > 0) {
            setCurrentSong(songs[currentIndex - 1]);
        }
    }

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
    };

    // Format time display
    const formatTime = (seconds) => {
        if (isNaN(seconds)) return '0:00';
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
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
            src={`http://localhost:5000/api/songs/${currentSong.id}/stream`}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={() => setIsPlaying(false)}
            onError={(e) => {
                console.error('Audio error:', e);
                console.error('Audio error code:', e.target.error?.code);
                console.error('Audio error message:', e.target.error?.message);
                console.error('Audio src:', e.target.src);
            }}
            onLoadStart={() => console.log('Audio load started')}
            onCanPlay={() => console.log('Audio can play')}
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
            <button className="control-btn" onClick={handlePrev}>⏮️</button>
            <button className="play-pause-btn" onClick={togglePlayPause}>
                {isPlaying ? '⏸️' : '▶️'}
            </button>
            <button className="control-btn" onClick={handleNext}>⏭️</button>
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
            <span className="volume-icon">🔊</span>
            <input
            type="range"
            min="0"
            max="1"
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