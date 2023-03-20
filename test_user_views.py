import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()


app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    
    def setUp(self):
        """Set up the test database and create a test client."""
        
        # Create a test user to use in the tests
        user = User(
            username='testuser',
            email='testuser@test.com',
            password='testpassword',
        )
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id

        # Create a test message for the test user to like
        message = Message(
            text='test message',
            user_id=user.id,
        )
        db.session.add(message)
        db.session.commit()

        self.message_id = message.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up the test database after each test."""
        db.session.remove()
        db.drop_all()

    def test_list_users_route(self):
        """Test that the list_users route returns the expected status code and HTML."""
        # Set up the test client with a logged-in test user
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            # Send a request to the route
            resp = c.get('/users')

            # Check that the response has the expected status code and HTML
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'testuser', resp.data)

    def test_users_show_route(self):
        """Test that the users_show route returns the expected status code and HTML."""
        # Set up the test client with a logged-in test user
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            # Send a request to the route
            resp = c.get(f'/users/{self.user_id}')

            # Check that the response has the expected status code and HTML
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'testuser', resp.data)

    def test_show_following_route(self):
        """Test that the show_following route returns the expected status code and HTML."""
        # Set up the test client with a logged-in test user
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.user_id

            # Send a request to the route
            resp = c.get(f'/users/{self.user_id}/following')

            # Check that the response has the expected status code and HTML
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'testuser', resp.data)