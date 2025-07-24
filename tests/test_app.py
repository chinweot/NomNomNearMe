

import unittest
import os
from dotenv import load_dotenv
load_dotenv()
from app import app
import db
from apis.event_handler import search_all_events
from apis.yelp import format_date, search_yelp_events
from apis.reddit_api import genai_call, search_reddit_events

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_signup_page_get(self):
        response = self.app.get('/signup')
        self.assertEqual(response.status_code, 200)

    def test_home_page_get(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_search_page_get(self):
        response = self.app.get('/search')
        self.assertEqual(response.status_code, 200)

    def test_about_page_get(self):
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)

    def test_login_page_get(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_api_save_event_unauth(self):
        response = self.app.post('/api/save_event', json={"global_id": "1", "source": "test", "title": "Test Event"})
        self.assertEqual(response.status_code, 401)

    def test_api_save_event_no_data(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
        response = self.app.post('/api/save_event', json=None)
        self.assertEqual(response.status_code, 400)

    def test_api_delete_saved_event_unauth(self):
        response = self.app.post('/api/delete_saved_event', json={"global_id": "1"})
        self.assertEqual(response.status_code, 401)

    def test_api_delete_saved_event_no_id(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
        response = self.app.post('/api/delete_saved_event', json={})
        self.assertEqual(response.status_code, 400)

    def test_api_events_no_location(self):
        response = self.app.get('/api/events?interests=food')
        self.assertEqual(response.status_code, 400)

class TestDB(unittest.TestCase):

    def test_hash_password(self):
        pw = 'test123'
        hashed = db.hash_password(pw)
        self.assertNotEqual(pw, hashed)
        self.assertTrue(isinstance(hashed, str))

    def test_register_and_login_user(self):
        name = 'Test User'
        email = 'testuser@example.com'
        password = 'testpass'
        db.register_user(name, email, password)
        user = db.login_user(email, password)
        self.assertIsNotNone(user)
        self.assertIn('status', user)
        self.assertEqual(user['status'], 'access granted')

    def test_save_and_get_and_delete_event(self):
        user_id = 1
        event_data = {'global_id': 'event1', 'source': 'test', 'title': 'Test Event', 'date': '2025-07-24', 'location': 'NY', 'url': 'http://test.com'}
        db.save_event(user_id, event_data)
        events = db.get_saved_events(user_id)
        self.assertTrue(any(e['global_id'] == 'event1' for e in events))
        db.delete_saved_event(user_id, 'event1')
        events = db.get_saved_events(user_id)
        self.assertFalse(any(e['global_id'] == 'event1' for e in events))

class TestEventHandler(unittest.TestCase):
    def test_search_all_events(self):
        result = search_all_events('New York', 'food')
        self.assertIsInstance(result, list)

class TestYelp(unittest.TestCase):
    def test_format_date(self):
        iso = '2025-07-23T12:00:00Z'
        formatted = format_date(iso)
        self.assertIsInstance(formatted, str)

    def test_search_yelp_events(self):
        yelp_api_key = os.getenv('YELP_KEY')
        result = search_yelp_events('New York', 'food', yelp_api_key, 1, 1000)
        self.assertIsInstance(result, list)

class TestRedditAPI(unittest.TestCase):
    def test_genai_call(self):
        prompt = 'Tell me a joke.'
        result = genai_call(prompt)
        self.assertIsInstance(result, str)

    def test_search_reddit_events(self):
        reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
        reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        reddit_user_agent = os.getenv('REDDIT_USER_AGENT')
        result = search_reddit_events('New York', 'food', reddit_client_id, reddit_client_secret, reddit_user_agent)
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
