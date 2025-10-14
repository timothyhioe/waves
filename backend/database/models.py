from database import db
from datetime import datetime, timezone
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash


# Check if we're using PostgreSQL for enhanced features
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///music_player.db')
IS_POSTGRESQL = DATABASE_URL.startswith('postgresql')

if IS_POSTGRESQL:
    from sqlalchemy.dialects.postgresql import UUID, JSONB
    import uuid

class User(db.Model):
    __tablename__ = 'users'

    if IS_POSTGRESQL:
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    else:
        id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False, index = True)
    email= db.Column(db.String(120), unique=True, nullable=False, index = True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)

    #relationships
    song = db.relationship('Song', back_populates='user', cascade='all, delete-orphan')
    playlist = db.relationship('Playlist', back_populates='user', cascade='all, delete-orphan')
    play_history = db.relationship('PlayHistory', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return{
            'id': str(self.id) if IS_POSTGRESQL else self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f'<User {self.username}>'

class Song(db.Model):
    __tablename__ = 'songs'
    
    if IS_POSTGRESQL:
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    else:
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
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
    user = db.relationship('User', back_populates='song')
    playlist_songs = db.relationship('PlaylistSong', back_populates='song', cascade='all, delete-orphan')
    play_history = db.relationship('PlayHistory', back_populates='song', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id) if IS_POSTGRESQL else self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'genre': self.genre,
            'duration': self.duration,
            'file_size': self.file_size,
            'bitrate': self.bitrate,
            'format': self.format,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'user_id': str(self.user_id) if IS_POSTGRESQL else self.user_id
        }
    
    def __repr__(self):
        return f'<Song {self.artist} - {self.title}>'


class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    if IS_POSTGRESQL:
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    else:
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
        
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    structure_type = db.Column(db.String(50), default='list')  # 'list', 'queue', 'stack', 'tree'
    
    # relationships
    user = db.relationship('User', back_populates='playlist')
    playlist_songs = db.relationship('PlaylistSong', back_populates='playlist', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': str(self.id) if IS_POSTGRESQL else self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': str(self.user_id) if IS_POSTGRESQL else self.user_id,
            'song_count': len(self.playlist_songs)
        }
    
    def __repr__(self):
        return f'<Playlist {self.name}>'


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

    #prevent duplicate songs in the same playlist
    __table_args__ = (db.UniqueConstraint('playlist_id', 'song_id', name='unique_playlist_song'),)


class PlayHistory(db.Model):
    __tablename__ = 'play_history'
    
    if IS_POSTGRESQL:
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        song_id = db.Column(UUID(as_uuid=True), db.ForeignKey('songs.id'), nullable=False)
        user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    else:
        id = db.Column(db.Integer, primary_key=True)
        song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    played_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    play_duration = db.Column(db.Float)

    # relationships
    user = db.relationship('User', back_populates='play_history')
    song = db.relationship('Song')

    def __repr__(self):
        return f'<PlayHistory {self.user_id} played {self.song_id}>'




