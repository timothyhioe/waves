from flask import Blueprint, request, jsonify, Response, current_app
from file_manager import AudioFileManager
from database.models import Song, db
import os

songs_bp = Blueprint('songs', __name__)

#song upload endpoint
@songs_bp.route('/songs', methods=['POST'])
def upload_song():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400
    
    manager = AudioFileManager(current_app.config['UPLOAD_FOLDER'])
    
    if not manager.allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400
    
    try:
        metadata = manager.save_file(file)
        song = Song(
            title=metadata['title'],
            artist=metadata['artist'],
            album=metadata['album'],
            genre=metadata.get('genre', 'Unknown'),
            file_path=metadata['file_path'],
            file_size=metadata['file_size'],
            bitrate=metadata.get('bitrate', 0),
            format=metadata['format']
        )
        db.session.add(song)
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully', 'song_id': song.id}), 201
    
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#song listing endpoint
@songs_bp.route('/songs', methods=['GET'])
def list_songs():
    songs = Song.query.all()
    song_list = [{
        'id': song.id,
        'title': song.title,
        'artist': song.artist,
        'album': song.album,
        'genre': song.genre,
        'file_size': song.file_size,
        'bitrate': song.bitrate,
        'format': song.format,
        'upload_date': song.upload_date
    } for song in songs]
    return jsonify(song_list), 200

#listing by song_id endpoint
@songs_bp.route('/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    song = Song.query.get_or_404(song_id)
    song_data = {
        'id': song.id,
        'title': song.title,
        'artist': song.artist,
        'album': song.album,
        'genre': song.genre,
        'file_size': song.file_size,
        'bitrate': song.bitrate,
        'format': song.format,
        'upload_date': song.upload_date
    }
    return jsonify(song_data), 200

#song deletion endpoint
@songs_bp.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    file_path = song.file_path

    manager = AudioFileManager(current_app.config['UPLOAD_FOLDER'])
    if manager.delete_file(file_path):
        db.session.delete(song)
        db.session.commit()
        return jsonify({'message': 'Song deleted successfully'}), 200
    else:
        return jsonify({'error': 'File deletion failed'}), 500

#song streaming endpoint
@songs_bp.route('/songs/<int:song_id>/stream')
def stream_song(song_id):
    song = Song.query.get_or_404(song_id)
    file_path = song.file_path
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    mime_types = {
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'flac': 'audio/flac',
        'ogg': 'audio/ogg',
        'm4a': 'audio/mp4',
        'aac': 'audio/aac'
    }
    mime_type = mime_types.get(song.format.lower(), 'audio/mpeg')
    
    def generate():
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                yield chunk
    
    return Response(generate(), mimetype=mime_type)

