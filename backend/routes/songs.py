from flask import Blueprint, request, jsonify, Response, current_app, send_file
from file_manager import AudioFileManager
from database.models import Song, db
from flask_cors import cross_origin
from services.music_search import MusicSearchService
import os
import uuid
from auth_middleware import token_required

songs_bp = Blueprint('songs', __name__)

#song upload endpoint
@songs_bp.route('/songs', methods=['POST'])
@token_required
def upload_song(current_user):
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400
    
    manager = AudioFileManager(current_app.config['UPLOAD_FOLDER'])
    
    if not manager.allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400
    
    try:
        metadata = manager.save_file(file)
        new_song = Song(
            title=metadata['title'],
            artist=metadata['artist'],
            album=metadata['album'],
            genre=metadata.get('genre', 'Unknown'),
            duration=metadata.get('duration'),
            file_path=metadata['file_path'],
            file_size=metadata['file_size'],
            bitrate=metadata.get('bitrate', 0),
            format=metadata['format'],
            user_id=current_user.id
        )
        db.session.add(new_song)
        db.session.commit()
        return jsonify({
            'message': 'Song uploaded successfully',
            'song': {
                'id': str(new_song.id),
                'title': new_song.title,
                'artist': new_song.artist,
                'album': new_song.album
            }
        }), 201
    
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

#song listing endpoint
@songs_bp.route('/songs', methods=['GET'])
@token_required
def list_songs(current_user):
    try:
        songs = Song.query.filter_by(user_id = current_user.id).order_by(Song.upload_date.desc()).all()
        song_list = [{
            'id': str(song.id),
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
        return jsonify({
            'songs': song_list,
            'total_songs': len(song_list)
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error listing songs: {e}")
        return jsonify({'error': 'Failed to list songs'}), 500

#listing by song_id endpoint
@songs_bp.route('/songs/<song_id>', methods=['GET'])
@token_required
def get_song(current_user, song_id):
    try:
        # Try to validate as UUID, but don't fail if it's an integer (for SQLite tests)
        try:
            uuid.UUID(song_id)
        except ValueError:
            # If it's not a valid UUID, it might be an integer ID from SQLite
            pass

        song = Song.query.filter_by(id=song_id, user_id=current_user.id).first()

        if not song:
            return jsonify({'error': 'Song not found'}), 404
        
        return jsonify({
            'id': str(song.id),
            'title': song.title,
            'artist': song.artist,
            'album': song.album,
            'genre': song.genre,
            'duration': song.duration,
            'file_size': song.file_size,
            'bitrate': song.bitrate,
            'format': song.format,
            'upload_date': song.upload_date.isoformat() if song.upload_date else None
        }), 200

    except ValueError:
        return jsonify({'error': 'Invalid song ID format'}), 400
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving song: {e}")
        return jsonify({'error': 'Failed to retrieve song'}), 500
    

#song deletion endpoint
@songs_bp.route('/songs/<song_id>', methods=['DELETE'])
@token_required
def delete_song(current_user, song_id):
    try:
        # Try to validate as UUID, but don't fail if it's an integer (for SQLite tests)
        try:
            uuid.UUID(song_id)
        except ValueError:
            # If it's not a valid UUID, it might be an integer ID from SQLite
            pass

        song = Song.query.filter_by(id=song_id, user_id=current_user.id).first()
        file_path = song.file_path

        if not song:
            return jsonify({'error': 'Song not found'}), 404

        # Delete file from filesystem
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], song.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.session.delete(song)
        db.session.commit()
        
        return jsonify({'message': 'Song deleted successfully'}), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid song ID format'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete error: {e}")
        return jsonify({'error': 'Failed to delete song'}), 500

#song streaming endpoint
@songs_bp.route('/songs/<song_id>/stream', methods=['GET'])
@token_required
def stream_song(current_user, song_id):
    try:
        # Try to validate as UUID, but don't fail if it's an integer (for SQLite tests)
        try:
            uuid.UUID(song_id)
        except ValueError:
            # If it's not a valid UUID, it might be an integer ID from SQLite
            pass

        song = Song.query.filter_by(id=song_id, user_id=current_user.id).first()
        
        if not song:
            return jsonify({'error': 'Song not found'}), 404

        # Build the full file path - ensure it's always absolute
        if os.path.isabs(song.file_path):
            # Already absolute path
            file_path = song.file_path
        elif song.file_path.startswith('uploads/'):
            # Path already includes 'uploads/', remove it since we'll add UPLOAD_FOLDER
            filename = song.file_path.replace('uploads/', '')
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        else:
            # Just filename
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], song.file_path)
        
        # Make sure the path is absolute
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        print(f"Song file_path from DB: {song.file_path}")  # Debug
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
    
    except ValueError:
        return jsonify({'error': 'Invalid song ID format'}), 400
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
@token_required
def download_song(current_user):
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
            format=metadata['format'],
            user_id=current_user.id 
        )
        
        db.session.add(song)
        db.session.commit()
        
        return jsonify({
            'message': 'Song downloaded successfully',
            'song': {
                'id': str(song.id),  
                'title': song.title,
                'artist': song.artist,
                'album': song.album
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Download error: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500
