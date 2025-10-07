import React from 'react';
import './searchbar.css';

function SearchBar({ searchQuery, setSearchQuery }) {
    return (
        <div className="search-bar">
            <div className="search-container">
                <div className="search-icon">🔍</div>
                <input
                type="text"
                placeholder="Search songs, artists, or albums..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
                />
                {searchQuery && (
                <button 
                    className="clear-search"
                    onClick={() => setSearchQuery('')}
                >
                    ✕
                </button>
                )}
            </div>
        </div>
    );
}

export default SearchBar;