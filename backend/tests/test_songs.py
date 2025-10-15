import unittest
import io
import json
import os
from app import app
from database import db
from database.models import User, Song

class SongTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        # Use in-memory SQLite for tests (auto-created, auto-destroyed)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Register and login user, get token
            self.client.post('/api/register', json={
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'TestPass123'
            })
            login_resp = self.client.post('/api/login', json={
                'username': 'testuser',
                'password': 'TestPass123'
            })
            self.token = login_resp.get_json()['token']

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_upload_song(self):
        # Simulate uploading a small mp3 file
        data = {
            'file': (io.BytesIO(b"fake mp3 data"), 'test.mp3')
        }
        response = self.client.post('/api/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            content_type='multipart/form-data',
            data=data
        )
        self.assertEqual(response.status_code, 201)
        resp_json = response.get_json()
        self.assertIn('song', resp_json)
        self.assertEqual(resp_json['song']['title'], 'test')  # Title from filename

    def test_list_songs(self):
        # Upload a song first
        self.test_upload_song()
        response = self.client.get('/api/songs',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertIn('songs', resp_json)
        self.assertGreaterEqual(len(resp_json['songs']), 1)

    def test_get_song(self):
        # Upload a song first
        self.test_upload_song()
        # Get song id
        response = self.client.get('/api/songs',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        song_id = response.get_json()['songs'][0]['id']
        # Get song details
        response = self.client.get(f'/api/songs/{song_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertEqual(resp_json['id'], song_id)

    def test_delete_song(self):
        # Upload a song first
        self.test_upload_song()
        # Get song id
        response = self.client.get('/api/songs',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        song_id = response.get_json()['songs'][0]['id']
        # Delete song
        response = self.client.delete(f'/api/songs/{song_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        resp_json = response.get_json()
        self.assertIn('message', resp_json)
        # Confirm deletion
        response = self.client.get(f'/api/songs/{song_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 404)

    def test_list_songs_unauthenticated(self):
        response = self.client.get('/api/songs')
        self.assertEqual(response.status_code, 401)
        resp_json = response.get_json()
        self.assertIn('error', resp_json)

if __name__ == '__main__':
    unittest.main()