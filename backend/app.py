from flask import Flask, request, jsonify, Response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime, timezone
from database import db
from database.models import Song, Playlist, PlaylistSong, PlayHistory
from file_manager import AudioFileManager
from dotenv import load_dotenv

from routes.songs import songs_bp
from routes.playlists import playlists_bp
from routes.users import auth_bp

app = Flask(__name__)

load_dotenv()

# More explicit CORS configuration
# Allow all origins for development (restrict in production)
CORS(
    app,
    origins=["*"],  # Allow all origins for now (for Kubernetes port-forward/Ingress)
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    supports_credentials=True,
)


# Add CORS headers manually to all responses
@app.after_request
def after_request(response):
    # Get origin from request, fallback to localhost:3000
    origin = request.headers.get("Origin", "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Origin", origin)
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


# Database configuration - PostgreSQL or fallback to SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///music_player.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB limit
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "supersecretkey")

db.init_app(app)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(songs_bp, url_prefix="/api")
app.register_blueprint(playlists_bp, url_prefix="/api")


@app.route("/api/health")
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "database": DATABASE_URL.split("@")[-1]
            if "@" in DATABASE_URL
            else "sqlite",
            "upload_folder": app.config["UPLOAD_FOLDER"],
            "timestamp": datetime.now(timezone.utc),
        }
    )


if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")

            # Test connection
            from sqlalchemy import text

            result = db.session.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL version: {version}")

        except Exception as e:
            print(f"Database error: {e}")
    app.run(host="0.0.0.0", debug=True)
