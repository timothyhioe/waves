from flask import Blueprint, request, jsonify, current_app
from data_structures import PlaylistManager
from database.models import Playlist, Song, PlaylistSong, db
import uuid
from auth_middleware import token_required

playlists_bp = Blueprint('playlists', __name__)



#playlist creation endpoint
@playlists_bp.route('/playlists', methods=['POST'])
@token_required
def create_playlist(current_user):
    try: 
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        structure_type = data.get('structure_type', 'list')  # default to list

        if not name:
            return jsonify({'error': 'Playlist name is required'}), 400
        
        playlist = Playlist(
            name=name, 
            description=description, 
            structure_type=structure_type,
            user_id=current_user.id
        )
        db.session.add(playlist)
        db.session.commit()

        return jsonify({
            'message': 'Playlist created successfully', 
            'playlist': {
                'id': playlist.id,
                'name': playlist.name,
                'description': playlist.description,
                'structure_type': playlist.structure_type,
                'created_at': playlist.created_at   
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Playlist creation error: {e}")
        return jsonify({'error': 'Failed to create playlist'}), 500


#playlist listing endpoint
@playlists_bp.route('/playlists', methods=['GET'])
@token_required
def list_playlists(current_user):
    try:
        playlists = Playlist.query.filter_by(user_id=current_user.id).order_by(Playlist.created_at.desc()).all()

        playlist_list = [{
            'id': pl.id,
            'name': pl.name,
            'description': pl.description,
            'structure_type': pl.structure_type,
            'created_at': pl.created_at,
            'song_count': len(pl.playlist_songs)
        } for pl in playlists]

        return jsonify({
            'playlists': playlist_list,
            'total_playlists': len(playlist_list)
        }), 200
    
    except Exception as e:  
        current_app.logger.error(f"Error listing playlists: {e}")
        return jsonify({'error': 'Failed to list playlists'}), 500


#playlist detail endpoint
@playlists_bp.route('/playlists/<playlist_id>', methods=['GET'])
@token_required
def get_playlist(current_user, playlist_id):
    try:
        # Convert playlist_id to int if it's a number (for SQLite tests)
        # Otherwise keep as string for UUID
        try:
            playlist_id = int(playlist_id)
        except ValueError:
            # It's a UUID string, keep it as is
            pass

        playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        songs = [{
            'id': str(ps.song.id),
            'title': ps.song.title,
            'artist': ps.song.artist,
            'album': ps.song.album,
            'genre': ps.song.genre,
            'duration': ps.song.duration,
            'file_size': ps.song.file_size,
            'bitrate': ps.song.bitrate,
            'format': ps.song.format,
            'upload_date': ps.song.upload_date.isoformat() if ps.song.upload_date else None,
            'position': ps.position
        } for ps in playlist.playlist_songs]
        
        playlist_data = {
            'id': playlist.id,
            'name': playlist.name,
            'description': playlist.description,
            'structure_type': playlist.structure_type,
            'created_at': playlist.created_at.isoformat() if playlist.created_at else None,
            'songs': songs,
            'song_count': len(songs)
        }
        return jsonify(playlist_data), 200
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving playlist: {e}")
        return jsonify({'error': 'Failed to retrieve playlist'}), 500
    

#add song to playlist endpoint
@playlists_bp.route('/playlists/<playlist_id>/songs', methods=['POST'])
@token_required
def add_song_to_playlist(current_user, playlist_id):
    try:
        data = request.json
        song_id = data.get('song_id')
        
        if not song_id:
            return jsonify({'error': 'song_id is required'}), 400
        
        # Convert IDs to int if they're numbers (for SQLite tests)
        try:
            playlist_id = int(playlist_id)
            song_id = int(song_id)
        except ValueError:
            pass  # Keep as strings for UUIDs
        
        # Check playlist ownership
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        # Check song ownership
        song = Song.query.filter_by(id=song_id, user_id=current_user.id).first()
        if not song:
            return jsonify({'error': 'Song not found'}), 404
        
        # Check if song already in playlist
        existing = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
        if existing:
            return jsonify({'error': 'Song already in playlist'}), 409
        
        # Get next position
        max_position = db.session.query(db.func.max(PlaylistSong.position)).filter_by(playlist_id=playlist_id).scalar() or 0
        
        # Add song to playlist
        playlist_song = PlaylistSong(
            playlist_id=playlist_id,
            song_id=song_id,
            position=max_position + 1
        )
        db.session.add(playlist_song)
        db.session.commit()
        
        return jsonify({
            'message': 'Song added to playlist',
            'song': {
                'id': str(song.id),
                'title': song.title,
                'artist': song.artist,
                'position': playlist_song.position
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding song to playlist: {e}")
        return jsonify({'error': 'Failed to add song to playlist'}), 500


#remove song from playlist endpoint
@playlists_bp.route('/playlists/<playlist_id>/songs/<song_id>', methods=['DELETE'])
@token_required
def remove_song_from_playlist(current_user, playlist_id, song_id):
    try:
        # Convert IDs to int if they're numbers (for SQLite tests)
        try:
            playlist_id = int(playlist_id)
            song_id = int(song_id)
        except ValueError:
            pass  # Keep as strings for UUIDs
        
        # Check playlist ownership
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        # Find and remove the playlist-song relationship
        playlist_song = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
        if not playlist_song:
            return jsonify({'error': 'Song not in playlist'}), 404
        
        db.session.delete(playlist_song)
        db.session.commit()
        
        return jsonify({'message': 'Song removed from playlist'}), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing song from playlist: {e}")
        return jsonify({'error': 'Failed to remove song from playlist'}), 500


#playlist update endpoint
@playlists_bp.route('/playlists/<playlist_id>', methods=['PUT'])
@token_required
def update_playlist(current_user, playlist_id):
    try:
        # Convert playlist_id to int if it's a number (for SQLite tests)
        try:
            playlist_id = int(playlist_id)
        except ValueError:
            pass  # Keep as string for UUIDs
        
        # Check playlist ownership
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        data = request.json
        if 'name' in data:
            playlist.name = data['name']
        if 'description' in data:
            playlist.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Playlist updated successfully',
            'playlist': {
                'id': str(playlist.id),
                'name': playlist.name,
                'description': playlist.description
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating playlist: {e}")
        return jsonify({'error': 'Failed to update playlist'}), 500


#playlist deletion endpoint
@playlists_bp.route('/playlists/<playlist_id>', methods=['DELETE'])
@token_required
def delete_playlist(current_user, playlist_id):
    try:
        # Convert playlist_id to int if it's a number (for SQLite tests)
        try:
            playlist_id = int(playlist_id)
        except ValueError:
            pass  # Keep as string for UUIDs
        
        # Only allow deleting user's own playlists
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
        
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        db.session.delete(playlist)
        db.session.commit()
        
        return jsonify({'message': 'Playlist deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting playlist: {e}")
        return jsonify({'error': 'Failed to delete playlist'}), 500


#playlist shuffle endpoint
@playlists_bp.route('/playlists/<playlist_id>/shuffle', methods=['POST'])
@token_required
def shuffle_playlist(current_user, playlist_id):
    try:
        # Convert playlist_id to int if it's a number (for SQLite tests)
        try:
            playlist_id = int(playlist_id)
        except ValueError:
            pass  # Keep as string for UUIDs
        
        # Only allow shuffling user's own playlists
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
        
        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404
        
        # Get all songs in playlist
        playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).all()
        
        if not playlist_songs:
            return jsonify({'error': 'Playlist is empty'}), 400
        
        # Convert to data structure and shuffle
        playlist_obj = PlaylistManager.create_playlist(
            playlist.structure_type, 
            [ps.song_id for ps in playlist_songs]
        )
        playlist_obj.shuffle()
        
        # Update positions based on shuffled order
        shuffled_songs = playlist_obj.songs if hasattr(playlist_obj, 'songs') else list(playlist_obj)
        for idx, song_id in enumerate(shuffled_songs):
            ps = next(ps for ps in playlist_songs if ps.song_id == song_id)
            ps.position = idx
        
        db.session.commit()
        
        return jsonify({'message': 'Playlist shuffled successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error shuffling playlist: {e}")
        return jsonify({'error': 'Failed to shuffle playlist'}), 500