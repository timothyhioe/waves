import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipBack, SkipForward, Shuffle, Repeat, Volume2, VolumeX, Volume1 } from 'lucide-react';
import './PlayerBar.css';

export function PlayerBar({
  currentSong,
  songs,
  setCurrentSong,
  isPlaying,
  setIsPlaying,
  // ...other props
}) {
  const audioRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.35);
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
          }
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

  // Set volume to default upon page reload
  useEffect(() => {
  if (audioRef.current) {
    audioRef.current.volume = volume;
  }
  }, [audioUrl, volume]);

  // Auto-play when song changes
  useEffect(() => {
    if (currentSong && audioRef.current && audioUrl) {
      audioRef.current.load();
      setCurrentTime(0);
    }
  }, [currentSong, audioUrl]);

  // Play/pause audio when isPlaying changes
  useEffect(() => {
    if (audioRef.current && audioUrl) {
      if (isPlaying) {
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise.catch(error => {
            console.log("Playback prevented:", error);
          });
        }
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying, audioUrl]);

  // Play/pause functionality
  const togglePlayPause = () => {
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  // Safely get current index
  const currentIndex = songs && songs.length > 0 
    ? songs.findIndex((song) => song.id === currentSong?.id)
    : -1;

  // Next song
  const handleNext = () => {
    if (songs && songs.length > 0 && currentIndex < songs.length - 1) {
      setCurrentSong(songs[currentIndex + 1]);
    }
  };

  // Previous song
  const handlePrev = () => {
    if (songs && songs.length > 0 && currentIndex > 0) {
      if(audioRef.current && audioRef.current.currentTime < 5){ //only go to prev song if current time is less than 5 seconds
        setCurrentSong(songs[currentIndex - 1]);
      }else{
        audioRef.current.currentTime = 0;
      }
    }
  };

  // Handle when audio is ready to play
  const handleCanPlay = () => {
    console.log("Audio can play");
    if (isPlaying && audioRef.current) {
      audioRef.current.play().catch(error => {
        console.log("Auto-play prevented:", error);
      });
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
    const newVolume = parseFloat(e.target.value);
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
      setVolume(0.3);
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

  // Get volume icon based on level
  const getVolumeIcon = () => {
    if (isMuted || volume === 0) {
      return <VolumeX size={18} />;
    } else if (volume <= 0.4) {
      return <Volume1 size={18} />;
    } else {
      return <Volume2 size={18} />;
    }
  };

  if (!currentSong) return null;

  // Check if songs array is valid
  const hasSongs = songs && songs.length > 0;

  return (
    <div className="player-bar">
      <audio
        ref={audioRef}
        src={audioUrl || ''}
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
        onCanPlay={handleCanPlay}
      />
      
      <div className="player-container">
        <div className="player-content">
          {/* Left: Song Info */}
          <div className="player-info">
            <div className="player-cover">
              <span className="player-cover-icon">♪</span>
            </div>
            <div className="player-details">
              <h4 className="player-title">
                {currentSong?.title || 'No song playing'}
              </h4>
              <p className="player-artist">
                {currentSong?.artist || 'Select a song to play'}
              </p>
            </div>
          </div>

          {/* Center: Player Controls */}
          <div className="player-controls">
            <div className="player-controls-buttons">
              <button
                className="player-control-btn"
                disabled
              >
                <Shuffle size={18} />
              </button>
              <button
                onClick={handlePrev}
                className="player-control-btn"
                disabled={!hasSongs || currentIndex <= 0}
              >
                <SkipBack size={22} />
              </button>
              <button
                onClick={togglePlayPause}
                className="player-play-btn"
                disabled={!currentSong}
              >
                {isPlaying ? <Pause size={24} /> : <Play size={24} />}
              </button>
              <button
                onClick={handleNext}
                className="player-control-btn"
                disabled={!hasSongs || currentIndex >= songs.length - 1}
              >
                <SkipForward size={22} />
              </button>
              <button
                className="player-control-btn"
                disabled
              >
                <Repeat size={18} />
              </button>
            </div>

            {/* Progress Bar - Desktop */}
            <div className="player-progress-section">
              <span className="player-time-text">{formatTime(currentTime)}</span>
              <div className="player-progress-bar" onClick={handleSeek}>
                <div
                  className="player-progress-fill"
                  style={{ width: `${(currentTime / duration) * 100}%` }}
                />
              </div>
              <span className="player-time-text">{formatTime(duration)}</span>
            </div>
          </div>

          {/* Right: Volume & Additional Controls */}
          <div className="player-right-controls">
            <div className="player-volume">
              <button className="player-volume-icon" onClick={toggleMute}>
                {getVolumeIcon()}
              </button>
              <input
                type="range"
                min="0"
                max="0.6"
                step="0.02"
                value={volume}
                onChange={handleVolumeChange}
                className="player-volume-slider"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

