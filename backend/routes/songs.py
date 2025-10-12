from flask import Blueprint, request, jsonify, Response, current_app, send_file
from file_manager import AudioFileManager
from database.models import Song, db
from flask_cors import cross_origin
from services.music_search import MusicSearchService
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
            duration=metadata.get('duration'),
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
        'duration': song.duration,
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
@songs_bp.route('/songs/<int:song_id>/stream', methods=['GET'])
def stream_song(song_id):
    try:
        song = Song.query.get_or_404(song_id)
        
        print(f"Streaming song: {song.title}")  # Debug
        print(f"File path in DB: {song.file_path}")  # Debug

        # Build the full file path
        if os.path.isabs(song.file_path):
            file_path = song.file_path
        else:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], song.file_path)
        
        print(f"Full file path: {file_path}")  # Debug
        print(f"File exists: {os.path.exists(file_path)}")  # Debug

        if not os.path.exists(file_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'flac': 'audio/flac',
            'm4a': 'audio/mp4',
            'ogg': 'audio/ogg'
        }

        mimetype = mime_types.get(song.format.lower(), 'audio/mpeg')

        return send_file(
            file_path,  # Use the calculated file_path
            mimetype=mimetype,
            as_attachment=False,
            download_name=f"{song.artist} - {song.title}.{song.format}"
        )
    
    except Exception as e:
        print(f"Streaming error: {e}")  # Debug
        return jsonify({'error': 'Failed to stream audio'}), 500
    
#search music online endpoint
@songs_bp.route('/search', methods=['GET'])
def search_songs():
    query=request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    limit = min(int(request.args.get('limit', 10)), 20) # limit search results to 20 max

    try:
        search_service = MusicSearchService()
        results = search_service.search_songs_online(query, limit)
        return jsonify({
            'query': query,
            'results': results,
            'total_results': len(results)
        }), 200


    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500
    
#download song from youtube endpoint
@songs_bp.route('/download', methods=['POST'])
def download_song():
    """Download song from YouTube URL"""
    data = request.get_json() 
    youtube_url = data.get('youtube_url')
    song_info = data.get('song_info', {})
    
    if not youtube_url:
        return jsonify({'error': 'YouTube URL required'}), 400
    
    try:
        search_service = MusicSearchService()
        
        # Download the song
        full_filename = search_service.download_from_youtube(
            youtube_url, 
            current_app.config['UPLOAD_FOLDER']
        )
        
        if not full_filename:
            return jsonify({'error': 'Download failed'}), 500
        
        # Extract filename
        filename = os.path.basename(full_filename)
        
        # Create metadata from song info
        metadata = {
            'title': song_info.get('title', 'Unknown'),
            'artist': song_info.get('artist', 'Unknown'),
            'album': song_info.get('album', 'Unknown'),
            'genre': song_info.get('genre', 'Unknown'),
            'duration': song_info.get('duration', 0),
            'file_path': filename,
            'file_size': os.path.getsize(full_filename),
            'bitrate': 192000,  # yt-dlp default
            'format': 'mp3'
        }
        
        # Save to database
        song = Song(
            title=metadata['title'],
            artist=metadata['artist'],
            album=metadata['album'],
            genre=metadata['genre'],
            duration=metadata['duration'],
            file_path=metadata['file_path'],
            file_size=metadata['file_size'],
            bitrate=metadata['bitrate'],
            format=metadata['format']
        )
        
        db.session.add(song)
        db.session.commit()
        
        return jsonify({
            'message': 'Song downloaded successfully',
            'song': {
                'id': song.id,
                'title': song.title,
                'artist': song.artist,
                'album': song.album
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500
