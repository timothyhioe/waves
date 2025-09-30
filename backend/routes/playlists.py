from flask import Blueprint, request, jsonify
from data_structures import PlaylistManager
from database.models import Playlist, db

playlists_bp = Blueprint('playlists', __name__)



#playlist creation endpoint
@playlists_bp.route('/playlists', methods=['POST'])
def create_playlist(): 
    data = request.json
    name = data.get('name')
    description = data.get('description', '')
    structure_type = data.get('structure_type', 'list')  # default to list
    if not name:
        return jsonify({'error': 'Playlist name is required'}), 400
    
    playlist = Playlist(name=name, description=description, structure_type=structure_type)
    db.session.add(playlist)
    db.session.commit()
    return jsonify({'message': 'Playlist created successfully', 'playlist_id': playlist.id}), 201


#playlist listing endpoint
@playlists_bp.route('/playlists', methods=['GET'])
def list_playlists():
    playlists = Playlist.query.all()
    playlist_list = [{
        'id': pl.id,
        'name': pl.name,
        'description': pl.description,
        'structure_type': pl.structure_type,
        'created_at': pl.created_at
    } for pl in playlists]
    return jsonify(playlist_list), 200


#playlist detail endpoint
@playlists_bp.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    songs = [{
        'id': ps.song.id,
        'title': ps.song.title,
        'artist': ps.song.artist,
        'album': ps.song.album,
        'genre': ps.song.genre,
        'file_size': ps.song.file_size,
        'bitrate': ps.song.bitrate,
        'format': ps.song.format,
        'upload_date': ps.song.upload_date,
        'position': ps.position
    } for ps in playlist.playlist_songs]
    
    playlist_data = {
        'id': playlist.id,
        'name': playlist.name,
        'description': playlist.description,
        'structure_type': playlist.structure_type,
        'created_at': playlist.created_at,
        'songs': songs
    }
    return jsonify(playlist_data), 200


#playlist deletion endpoint
@playlists_bp.route('/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return jsonify({'message': 'Playlist deleted successfully'}), 200

#playlist shuffle endpoint
@playlists_bp.route('/playlists/<int:playlist_id>/shuffle', methods=['POST'])
def shuffle_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    # Convert to data structure and shuffle
    playlist_obj = PlaylistManager.create_playlist(
        playlist.structure_type, 
        [ps.song_id for ps in playlist.playlist_songs]
    )
    playlist_obj.shuffle()
    return jsonify({'message': 'Playlist shuffled'}), 200  

