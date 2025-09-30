from flask import Blueprint, request, jsonify, Response
from data_structures import PlaylistManager
from database.models import Playlist, Song, PlaylistSong, db

playlists_songs_bp = Blueprint('playlists_songs', __name__)

#add song to playlist endpoint
@playlists_songs_bp.route('/playlists/<int:playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    data = request.json
    song_id = data.get('song_id')
    if not song_id:
        return jsonify({'error': 'Song ID is required'}), 400
    
    playlist = Playlist.query.get_or_404(playlist_id)
    song = Song.query.get_or_404(song_id)
    
    # Determine the next position
    max_position = db.session.query(db.func.max(PlaylistSong.position)).filter_by(playlist_id=playlist_id).scalar()
    next_position = (max_position or 0) + 1
    
    playlist_song = PlaylistSong(playlist_id=playlist.id, song_id=song.id, position=next_position)
    db.session.add(playlist_song)
    db.session.commit()
    
    return jsonify({'message': 'Song added to playlist successfully'}), 201

#remove song from playlist endpoint
@playlists_songs_bp.route('/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, song_id):
    playlist_song = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
    if not playlist_song:
        return jsonify({'error': 'Song not found in playlist'}), 404
    
    db.session.delete(playlist_song)
    db.session.commit()
    
    return jsonify({'message': 'Song removed from playlist successfully'}), 200

#reorder songs in playlist endpoint
@playlists_songs_bp.route('/playlists/<int:playlist_id>/songs/reorder', methods=['PUT'])
def reorder_songs_in_playlist(playlist_id):
    data = request.json
    new_order = data.get('new_order')  # Expecting a list of song IDs in the new order
    if not new_order or not isinstance(new_order, list):
        return jsonify({'error': 'New order must be a list of song IDs'}), 400
    
    playlist = Playlist.query.get_or_404(playlist_id)
    playlist_songs = {ps.song_id: ps for ps in playlist.playlist_songs}
    
    if set(new_order) != set(playlist_songs.keys()):
        return jsonify({'error': 'New order must contain the same song IDs as the current playlist'}), 400
    
    for position, song_id in enumerate(new_order, start=1):
        playlist_songs[song_id].position = position
    
    db.session.commit()
    
    return jsonify({'message': 'Playlist reordered successfully'}), 200

