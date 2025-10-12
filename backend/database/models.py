from database import db
from datetime import datetime, timezone
import json
import os

# Check if we're using PostgreSQL for enhanced features
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///music_player.db')
IS_POSTGRESQL = DATABASE_URL.startswith('postgresql')

if IS_POSTGRESQL:
    from sqlalchemy.dialects.postgresql import UUID, JSONB
    import uuid

class Song(db.Model):
    __tablename__ = 'songs'
    
    if IS_POSTGRESQL:
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    else:
        id = db.Column(db.Integer, primary_key=True)
    
    title = db.Column(db.String(255), nullable=False, index=True)
    artist = db.Column(db.String(255), nullable=False, index=True)
    album = db.Column(db.String(255), nullable=True, index=True)
    genre = db.Column(db.String(100), nullable=True, index=True)
    duration = db.Column(db.Float, nullable=True)
    file_path = db.Column(db.String(500), nullable=False, unique=True)
    file_size = db.Column(db.BigInteger, nullable=False)  # size in bytes
    bitrate = db.Column(db.Integer, nullable=True)  # bitrate in kbps
    format = db.Column(db.String(20), nullable=False)  # e.g., mp3, wav
    
    # Enhanced timestamps with timezone support
    upload_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # PostgreSQL specific features
    if IS_POSTGRESQL:
        metadata_json = db.Column(JSONB, nullable=True)  # Store extra metadata
        play_count = db.Column(db.Integer, default=0)
        last_played = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # relationships
    playlist_songs = db.relationship('PlaylistSong', back_populates='song', cascade='all, delete-orphan')
    play_history = db.relationship('PlayHistory', back_populates='song', cascade='all, delete-orphan')


class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    if IS_POSTGRESQL:
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    else:
        id = db.Column(db.Integer, primary_key=True)
        
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    structure_type = db.Column(db.String(50), default='list')  # 'list', 'queue', 'stack', 'tree'
    
    # relationships
    playlist_songs = db.relationship('PlaylistSong', back_populates='playlist', cascade='all, delete-orphan')


class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'
    
    if IS_POSTGRESQL:
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        playlist_id = db.Column(UUID(as_uuid=True), db.ForeignKey('playlists.id'), nullable=False)
        song_id = db.Column(UUID(as_uuid=True), db.ForeignKey('songs.id'), nullable=False)
    else:
        id = db.Column(db.Integer, primary_key=True)
        playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
        song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    
    position = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # relationships
    playlist = db.relationship('Playlist', back_populates='playlist_songs')
    song = db.relationship('Song', back_populates='playlist_songs')


class PlayHistory(db.Model):
    __tablename__ = 'play_history'
    
    if IS_POSTGRESQL:
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        song_id = db.Column(UUID(as_uuid=True), db.ForeignKey('songs.id'), nullable=False)
    else:
        id = db.Column(db.Integer, primary_key=True)
        song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    
    played_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    play_duration = db.Column(db.Float)

    # relationships
    song = db.relationship('Song', back_populates='play_history')

