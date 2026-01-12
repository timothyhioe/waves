# Waves Music Player

A modern, full-stack music streaming application with cloud deployment on Google Kubernetes Engine.

## Live Demo

**Deployed Application**: contact timothy.hioe@gmail.com

Create your own account to explore all features.

---

## Features

### Core Functionality

- **User Authentication**: Secure registration and login with JWT tokens
- **Music Upload**: Upload your own music files (MP3 supported)
- **YouTube Download**: Search and download music directly from YouTube to your song list
- **Music Streaming**: Stream uploaded and downloaded music
- **Search**: Find songs in your library

### Technical Highlights

- **Cloud Deployment**: Deployed on Google Kubernetes Engine (GKE)
- **Container Orchestration**: Full Kubernetes setup with Ingress, persistent storage, and autoscaling
- **Production-Ready**: Nginx-served React frontend, Flask API backend, PostgreSQL database

---

## Tech Stack

### Frontend

- **React** - UI framework
- **Nginx** - Production web server

### Backend

- **Flask** - Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **JWT** - Token-based authentication
- **yt-dlp** - YouTube download functionality
- **Mutagen** - Audio metadata parsing

### Infrastructure & DevOps

- **Docker** - Containerization
- **Kubernetes** - Container orchestration
- **Google Kubernetes Engine (GKE)** - Managed Kubernetes service
- **GCP Artifact Registry** - Container image registry
- **Ingress** - HTTP/HTTPS load balancing
- **Persistent Volumes** - Stateful storage for database and uploads

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GCP Load Balancer                    │
│                  (Ingress Controller)                   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐          ┌─────▼────┐
    │ Frontend │          │ Backend  │
    │  (Nginx) │          │  (Flask) │
    │  Port 80 │◄────────►│ Port 5000│
    └──────────┘          └─────┬────┘
                                │
                          ┌─────▼──────┐
                          │ PostgreSQL │
                          │  Port 5432 │
                          └────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼────────┐    ┌────────▼────────┐
            │ Postgres Data  │    │ Backend Uploads │
            │  (10Gi PVC)    │    │   (20Gi PVC)    │
            └────────────────┘    └─────────────────┘
```

### Components

- **Frontend**: React SPA served by Nginx, handles UI and user interactions
- **Backend API**: Flask REST API with authentication, music management, and YouTube download
- **Database**: PostgreSQL with persistent storage for user data, songs, playlists
- **Ingress**: Routes `/api/*` to backend, `/` to frontend
- **Storage**: Persistent volumes for database and uploaded music files

---

## Local Development

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Quick Start with Docker Compose

```bash
# Clone the repository
git clone https://github.com/timothyhioe/waves.git
cd waves

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

### Manual Setup

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Frontend:**

```bash
cd frontend
npm install
npm start
```

---

## Deployment

### Production Deployment on GKE

The application is deployed on Google Kubernetes Engine with:

- 1-2 auto-scaling nodes (e2-medium)
- Ingress with GCP Load Balancer
- Persistent storage for database and uploads
- Container images stored in GCP Artifact Registry

**Full deployment guide**: See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### Quick Deploy Overview

```bash
# Build and push images
docker build -t europe-west3-docker.pkg.dev/PROJECT_ID/waves-repo/waves-backend:latest backend/
docker build -f frontend/Dockerfile.prod -t europe-west3-docker.pkg.dev/PROJECT_ID/waves-repo/waves-frontend:latest frontend/
docker push europe-west3-docker.pkg.dev/PROJECT_ID/waves-repo/waves-backend:latest
docker push europe-west3-docker.pkg.dev/PROJECT_ID/waves-repo/waves-frontend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress/

# Get external IP
kubectl get ingress waves-ingress -n waves
```

---

## Project Structure

```
Music_Player/
├── backend/                 # Flask API backend
│   ├── routes/             # API route handlers
│   ├── database/           # Database models
│   ├── services/           # Business logic (YouTube download, search)
│   ├── metadata/           # Audio metadata parsing
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── assets/        # Static assets
│   ├── Dockerfile.prod    # Production Docker build
│   └── nginx.conf         # Nginx configuration
├── k8s/                    # Kubernetes manifests
│   ├── backend/           # Backend deployment, service, secrets
│   ├── frontend/          # Frontend deployment, service
│   ├── postgres/          # PostgreSQL statefulset, service
│   └── ingress/           # Ingress configuration
├── docs/
│   └── DEPLOYMENT.md      # Detailed deployment guide
└── docker-compose.yml     # Local development setup
```

---

## API Documentation

### Authentication Endpoints

- `POST /api/register` - Create new user account
- `POST /api/login` - Login and receive JWT token
- `GET /api/profile` - Get user profile (authenticated)

### Music Endpoints

- `GET /api/songs` - List all songs
- `POST /api/songs/upload` - Upload music file
- `DELETE /api/songs/:id` - Delete song
- `GET /api/songs/:id/stream` - Stream audio file
- `PUT /api/songs/:id` - Update song metadata

### YouTube Endpoints

- `GET /api/search` - Search YouTube for music
- `POST /api/download` - Download music from YouTube

### Playlist Endpoints

- `GET /api/playlists` - List user's playlists
- `POST /api/playlists` - Create new playlist
- `PUT /api/playlists/:id` - Update playlist
- `DELETE /api/playlists/:id` - Delete playlist
- `POST /api/playlists/:id/songs` - Add song to playlist

### Health Check

- `GET /api/health` - API health status

---

## Key Features Implementation

### YouTube Download

Integrated `yt-dlp` for downloading music from YouTube with:

- Search functionality
- Automatic metadata extraction
- Audio format conversion
- Error handling for rate limits

### Authentication & Authorization

- JWT-based authentication
- Password hashing with bcrypt
- Token-based session management
- Protected routes with middleware

### File Management

- Secure file uploads with validation
- Unique filename generation
- Persistent storage in Kubernetes PVCs
- Audio metadata parsing with Mutagen

### Database Design

- User authentication and profiles
- Song library with metadata
- Playlist management with many-to-many relationships
- Play history tracking
- UUID primary keys for security

---

## Environment Variables

### Backend

```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
FLASK_ENV=production
UPLOAD_FOLDER=/app/uploads
```

### Frontend

```bash
REACT_APP_API_URL=  # Empty for Ingress, or http://backend-url for direct access
```

---

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

Tests cover:

- Authentication flow
- Song upload and management
- Playlist operations
- API endpoints

---

## Performance & Scalability

### Current Setup

- **Horizontal Scaling**: Kubernetes deployments can scale based on load
- **Persistent Storage**: 10Gi for database, 20Gi for uploads
- **Resource Limits**: CPU and memory limits configured per service
- **Health Checks**: Liveness and readiness probes for all services

---

## Acknowledgments

- Built as a full-stack learning project
- Deployed on Google Kubernetes Engine
- Inspired by modern music streaming platforms

---

**Note**: This application is for educational and personal use only. Downloading copyrighted content from YouTube may violate terms of service and copyright laws. Please ensure you have the right to download and use any content.
