from flask import Flask, request, jsonify, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os 
from datetime import datetime, timezone
from database import db
from database.models import Song, Playlist, PlaylistSong, PlayHistory
from file_manager import AudioFileManager

from routes.songs import songs_bp
from routes.playlists import playlists_bp  
from routes.playlist_song import playlists_songs_bp 

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music_player.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.register_blueprint(songs_bp, url_prefix='/api')
app.register_blueprint(playlists_bp, url_prefix='/api')
app.register_blueprint(playlists_songs_bp, url_prefix='/api') 

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

