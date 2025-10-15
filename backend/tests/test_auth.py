import unittest
import json
from app import app
from database import db
from database.models import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        response = self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('token', data)
        self.assertEqual(data['user']['username'], 'testuser')

    def test_login(self):
        # Register first
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123'
        })
        # Login
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('token', data)
        self.assertEqual(data['user']['username'], 'testuser')

    def test_login_wrong_password(self):
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123'
        })
        response = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'WrongPass'
        })
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)

    def test_protected_me_endpoint(self):
        # Register and login to get token
        self.client.post('/api/register', json={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPass123'
        })
        login_resp = self.client.post('/api/login', json={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        token = login_resp.get_json()['token']
        # Access protected endpoint
        response = self.client.get('/api/me', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['user']['username'], 'testuser')

    def test_protected_me_endpoint_no_token(self):
        response = self.client.get('/api/me')
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()