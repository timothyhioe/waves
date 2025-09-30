from database import db
from datetime import datetime
import json

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=True)
    genre = db.Column(db.String(50), nullable=True)
    file_path = db.Column(db.String(200), nullable=False, unique=True)
    file_size = db.Column(db.Integer, nullable=False)  # size in bytes
    bitrate = db.Column(db.Integer, nullable=True)  # bitrate in kbps
    format = db.Column(db.String(10), nullable=False)  # e.g., mp3, wav
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relationships
    playlist_songs = db.relationship('PlaylistSong', back_populates='song', cascade='all, delete-orphan')    


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    structure_type = db.Column(db.String(50), default='list')  # 'list', 'queue', 'stack', 'tree'
    
    # relationships
    playlist_songs = db.relationship('PlaylistSong', back_populates='playlist', cascade='all, delete-orphan')

class PlaylistSong(db.Model):
    #many to many relationship table
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    #relationships
    playlist = db.relationship('Playlist', back_populates='playlist_songs')
    song = db.relationship('Song', back_populates='playlist_songs')

class PlayHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)
    play_duration = db.Column(db.Float)

    song = db.relationship('Song', backref='play_history') # bidirectional relationship

    