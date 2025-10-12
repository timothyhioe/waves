#!/usr/bin/env python3
"""
Database initialization and migration script
"""

import os
import sys
from datetime import datetime, timezone

# Add the backend directory to the path
sys.path.append('/app')

from app import app, db
from database.models import Song, Playlist, PlaylistSong

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Create a default playlist
        if not Playlist.query.filter_by(name='Liked Songs').first():
            liked_playlist = Playlist(
                name='Liked Songs',
                description='Your favorite tracks',
                structure_type='list'
            )
            db.session.add(liked_playlist)
            db.session.commit()
            print("Created default 'Liked Songs' playlist")
        
        print("Database initialization complete!")

def check_database_connection():
    """Check if database connection is working"""
    try:
        with app.app_context():
            db.session.execute(db.text('SELECT 1'))
            print("Database connection successful!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == '__main__':
    if check_database_connection():
        init_database()
    else:
        sys.exit(1)