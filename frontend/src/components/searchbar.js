import React, { useState, useEffect, useCallback } from 'react';
import './searchbar.css';
import LoopIcon from '@mui/icons-material/Loop';

function SearchBar({ searchQuery, setSearchQuery, onlineSearchResults, setOnlineSearchResults }) {
    const[showOnlineResults, setShowOnlineResults] = React.useState(false);
    const[isSearching, setIsSearching] = useState(false);

    const searchOnline = useCallback(async (query) => {
        setIsSearching(true);
        console.log("Searching online for:", query);
        try{
            const response = await fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}&limit=5`);
            const data = await response.json();
            console.log("Search response:", data);

            if (response.ok) {
                setOnlineSearchResults(data.results);
                setShowOnlineResults(true);
                console.log("Online results set:", data.results);
            } else {
                console.error("Search failed:", data);
            }
        } catch (error){
            console.error("Online search error:", error);
        } finally {
            setIsSearching(false);
        }
    }, [setOnlineSearchResults]);

    useEffect(() => {
        if(searchQuery.length > 2) {
            const timeoutId = setTimeout(() => {
                searchOnline(searchQuery);
            }, 100); // 100ms waittime before triggering search

            return () => clearTimeout(timeoutId);
        } 
        else{
            setOnlineSearchResults([]);
            setShowOnlineResults(false);
        }
    }, [searchQuery, searchOnline, setOnlineSearchResults]);

    const handleDownload = async (song) => {
        if (!song.youtube_url){
            alert('No Youtube URL available for this song');
            return;
        }

        try{
            const response = await fetch('http://localhost:5000/api/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    youtube_url: song.youtube_url, 
                    song_info : song
                }),
            });

            const data = await response.json();

            if (response.ok) {
                alert('Song downloaded successfully!');
                setShowOnlineResults(false);
                setSearchQuery('');
                window.location.reload();
            } else{
                alert(`Download failed: ${data.error}`);
            }
        }catch (error){
            console.error('Download error:', error);
            alert('Download failed')
        }
    }

    // Debug logging
    console.log("SearchBar render - showOnlineResults:", showOnlineResults, "onlineSearchResults.length:", onlineSearchResults.length);

    return (
        <div className="search-bar">
            <div className="search-container">
                <div className="search-icon">🔍</div>
                <input
                type="text"
                placeholder="Search your songs or find new ones online..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
                />
                {searchQuery && (
                <button 
                    className="clear-search"
                    onClick={() => {
                    setSearchQuery('');
                    setShowOnlineResults(false);
                    }}
                >
                    ✕
                </button>
                )}
                
                {isSearching && (
                <div className="search-loading"><LoopIcon/></div>
                )}
            </div>
        </div>
    );
}

export default SearchBar;