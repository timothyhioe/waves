import unittest
import io
import json
from app import app
from database import db

class PlaylistTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Register and login user, get token
            reg_resp = self.client.post('/api/register', json={
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'TestPass123'
            })
            
            if reg_resp.status_code != 201:
                raise Exception(f"Registration failed: {reg_resp.get_json()}")
            
            login_resp = self.client.post('/api/login', json={
                'username': 'testuser',
                'password': 'TestPass123'
            })
            
            if login_resp.status_code != 200:
                raise Exception(f"Login failed: {login_resp.get_json()}")
            
            self.token = login_resp.get_json()['token']
            
            # Upload a test song
            data = {
                'file': (io.BytesIO(b"fake mp3 data"), 'test.mp3')
            }
            upload_resp = self.client.post('/api/songs',
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='multipart/form-data',
                data=data
            )
            self.song_id = upload_resp.get_json()['song']['id']

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_playlist(self):
        """Test creating a new playlist"""
        response = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={
                'name': 'My Playlist',
                'description': 'Test playlist',
                'structure_type': 'list'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('playlist', data)
        self.assertEqual(data['playlist']['name'], 'My Playlist')
        self.assertEqual(data['playlist']['structure_type'], 'list')

    def test_create_playlist_no_name(self):
        """Test creating playlist without name fails"""
        response = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={
                'description': 'Test playlist'
            }
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_create_playlist_unauthenticated(self):
        """Test creating playlist without auth fails"""
        response = self.client.post('/api/playlists',
            json={
                'name': 'My Playlist'
            }
        )
        self.assertEqual(response.status_code, 401)

    def test_create_playlist_with_long_name(self):
        """Test creating playlist with a very long name"""
        long_name = 'A' * 100
        response = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={
                'name': long_name,
                'description': 'Long name playlist'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['playlist']['name'], long_name)

    def test_create_playlist_with_special_characters(self):
        """Test creating playlist with special characters in name"""
        special_name = 'My Playlist!@#$%^&*()'
        response = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={
                'name': special_name,
                'description': 'Special chars'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['playlist']['name'], special_name)

    def test_list_playlists(self):
        """Test listing user's playlists"""
        # Create a playlist first
        self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Playlist 1'}
        )
        self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Playlist 2'}
        )
        
        response = self.client.get('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('playlists', data)
        self.assertEqual(len(data['playlists']), 2)
        self.assertEqual(data['total_playlists'], 2)

    def test_list_playlists_unauthenticated(self):
        """Test listing playlists without auth fails"""
        response = self.client.get('/api/playlists')
        self.assertEqual(response.status_code, 401)

    def test_get_playlist(self):
        """Test getting playlist details"""
        # Create a playlist
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test Playlist', 'description': 'A test'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        response = self.client.get(f'/api/playlists/{playlist_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Test Playlist')
        self.assertEqual(data['description'], 'A test')
        self.assertIn('songs', data)

    def test_get_playlist_not_found(self):
        """Test getting non-existent playlist"""
        response = self.client.get('/api/playlists/99999',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 404)

    def test_add_song_to_playlist(self):
        """Test adding a song to playlist"""
        # Create a playlist
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test Playlist'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        # Add song to playlist
        response = self.client.post(f'/api/playlists/{playlist_id}/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'song_id': self.song_id}
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['message'], 'Song added to playlist')
        self.assertIn('song', data)
        self.assertEqual(data['song']['position'], 1)

    def test_add_song_to_playlist_duplicate(self):
        """Test adding same song twice fails"""
        # Create playlist and add song
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test Playlist'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        self.client.post(f'/api/playlists/{playlist_id}/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'song_id': self.song_id}
        )
        
        # Try to add same song again
        response = self.client.post(f'/api/playlists/{playlist_id}/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'song_id': self.song_id}
        )
        self.assertEqual(response.status_code, 409)

    def test_remove_song_from_playlist(self):
        """Test removing a song from playlist"""
        # Create playlist and add song
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test Playlist'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        self.client.post(f'/api/playlists/{playlist_id}/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'song_id': self.song_id}
        )
        
        # Remove song
        response = self.client.delete(f'/api/playlists/{playlist_id}/songs/{self.song_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Song removed from playlist')

    def test_update_playlist(self):
        """Test updating playlist name and description"""
        # Create playlist
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Old Name', 'description': 'Old desc'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        # Update playlist
        response = self.client.put(f'/api/playlists/{playlist_id}',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'New Name', 'description': 'New desc'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['playlist']['name'], 'New Name')
        self.assertEqual(data['playlist']['description'], 'New desc')

    def test_update_playlist_partial(self):
        """Test updating only playlist name"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Partial Update', 'description': 'Desc'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        response = self.client.put(f'/api/playlists/{playlist_id}',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Updated Name'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['playlist']['name'], 'Updated Name')
        self.assertEqual(data['playlist']['description'], 'Desc')

    def test_delete_playlist(self):
        """Test deleting a playlist"""
        # Create playlist
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'To Delete'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        # Delete playlist
        response = self.client.delete(f'/api/playlists/{playlist_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        get_resp = self.client.get(f'/api/playlists/{playlist_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(get_resp.status_code, 404)

    def test_shuffle_playlist(self):
        """Test shuffling a playlist"""
        # Create playlist and add multiple songs
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Shuffle Test'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        # Upload and add multiple songs
        for i in range(3):
            data = {
                'file': (io.BytesIO(b"fake mp3 data"), f'test{i}.mp3')
            }
            upload_resp = self.client.post('/api/songs',
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='multipart/form-data',
                data=data
            )
            song_id = upload_resp.get_json()['song']['id']
            self.client.post(f'/api/playlists/{playlist_id}/songs',
                headers={'Authorization': f'Bearer {self.token}'},
                json={'song_id': song_id}
            )
        
        # Shuffle playlist
        response = self.client.post(f'/api/playlists/{playlist_id}/shuffle',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Playlist shuffled successfully')

    def test_shuffle_empty_playlist(self):
        """Test shuffling empty playlist fails"""
        # Create empty playlist
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Empty Playlist'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        # Try to shuffle
        response = self.client.post(f'/api/playlists/{playlist_id}/shuffle',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 400)

    def test_update_playlist_unauthenticated(self):
        """Test updating playlist without auth fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'To Update'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        response = self.client.put(f'/api/playlists/{playlist_id}',
            json={'name': 'Should Fail'}
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_playlist_unauthenticated(self):
        """Test deleting playlist without auth fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'To Delete'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        response = self.client.delete(f'/api/playlists/{playlist_id}')
        self.assertEqual(response.status_code, 401)

    def test_add_song_to_nonexistent_playlist(self):
        """Test adding song to a non-existent playlist fails"""
        response = self.client.post('/api/playlists/99999/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'song_id': self.song_id}
        )
        self.assertEqual(response.status_code, 404)

    def test_add_nonexistent_song_to_playlist(self):
        """Test adding non-existent song to playlist fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test Playlist'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        response = self.client.post(f'/api/playlists/{playlist_id}/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'song_id': '99999'}
        )
        self.assertEqual(response.status_code, 404)

    def test_remove_song_not_in_playlist(self):
        """Test removing a song not in playlist fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test Playlist'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        response = self.client.delete(f'/api/playlists/{playlist_id}/songs/99999',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_playlist_unauthenticated(self):
        """Test getting playlist details without auth fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test Playlist'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        response = self.client.get(f'/api/playlists/{playlist_id}')
        self.assertEqual(response.status_code, 401)

    def test_create_multiple_playlists_same_name(self):
        """Test creating multiple playlists with same name is allowed"""
        response1 = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Duplicate'}
        )
        response2 = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Duplicate'}
        )
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        # Verify both exist
        list_resp = self.client.get('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        data = list_resp.get_json()
        duplicate_count = sum(1 for p in data['playlists'] if p['name'] == 'Duplicate')
        self.assertEqual(duplicate_count, 2)

    def test_empty_playlist_has_zero_songs(self):
        """Test that newly created playlist has zero songs"""
        response = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Empty'}
        )
        data = response.get_json()
        playlist_id = data['playlist']['id']
        
        get_resp = self.client.get(f'/api/playlists/{playlist_id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        get_data = get_resp.get_json()
        self.assertEqual(get_data['song_count'], 0)
        self.assertEqual(len(get_data['songs']), 0)

    def test_add_multiple_songs_positions(self):
        """Test that adding multiple songs assigns correct positions"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Position Test'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        song_ids = []
        for i in range(3):
            data = {
                'file': (io.BytesIO(b"fake mp3 data"), f'song{i}.mp3')
            }
            upload_resp = self.client.post('/api/songs',
                headers={'Authorization': f'Bearer {self.token}'},
                content_type='multipart/form-data',
                data=data
            )
            song_id = upload_resp.get_json()['song']['id']
            song_ids.append(song_id)
            
            add_resp = self.client.post(f'/api/playlists/{playlist_id}/songs',
                headers={'Authorization': f'Bearer {self.token}'},
                json={'song_id': song_id}
            )
            self.assertEqual(add_resp.get_json()['song']['position'], i + 1)

    def test_list_empty_playlists(self):
        """Test listing playlists when user has none"""
        response = self.client.get('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['total_playlists'], 0)
        self.assertEqual(len(data['playlists']), 0)

    def test_update_playlist_not_found(self):
        """Test updating non-existent playlist fails"""
        response = self.client.put('/api/playlists/99999',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Updated'}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_playlist_not_found(self):
        """Test deleting non-existent playlist fails"""
        response = self.client.delete('/api/playlists/99999',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 404)

    def test_shuffle_nonexistent_playlist(self):
        """Test shuffling non-existent playlist fails"""
        response = self.client.post('/api/playlists/99999/shuffle',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        self.assertEqual(response.status_code, 404)

    def test_remove_song_unauthenticated(self):
        """Test removing song without auth fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        self.client.post(f'/api/playlists/{playlist_id}/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'song_id': self.song_id}
        )
        
        response = self.client.delete(f'/api/playlists/{playlist_id}/songs/{self.song_id}')
        self.assertEqual(response.status_code, 401)

    def test_add_song_unauthenticated(self):
        """Test adding song without auth fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        response = self.client.post(f'/api/playlists/{playlist_id}/songs',
            json={'song_id': self.song_id}
        )
        self.assertEqual(response.status_code, 401)

    def test_shuffle_unauthenticated(self):
        """Test shuffling playlist without auth fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        response = self.client.post(f'/api/playlists/{playlist_id}/shuffle')
        self.assertEqual(response.status_code, 401)

    def test_create_playlist_default_structure_type(self):
        """Test playlist defaults to 'list' structure type"""
        response = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Default Type'}
        )
        data = response.get_json()
        self.assertEqual(data['playlist']['structure_type'], 'list')

    def test_add_song_without_song_id(self):
        """Test adding song without song_id fails"""
        create_resp = self.client.post('/api/playlists',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'name': 'Test'}
        )
        playlist_id = create_resp.get_json()['playlist']['id']
        
        response = self.client.post(f'/api/playlists/{playlist_id}/songs',
            headers={'Authorization': f'Bearer {self.token}'},
            json={}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.get_json())