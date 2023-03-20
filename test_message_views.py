"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 1
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_not_logged_in(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized.", resp.data)
            
    def test_add_msg_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 2
                
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized.", resp.data)
            
    def test_message_show(self):
        msg = Message(id=10, text="This is a test message.", user_id = self.testuser_id)
        
        db.session.add(msg)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            msg = Message.query.get(10)
            res = c.get(f"/messages/{msg.id}")
            
            self.assertEqual(res.status_code, 200)
            self.assertIn(msg.text.encode(), res.data)
            
    def test_invalid_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            res = c.get('/messages/999')
            self.assertEqual(res.status_code, 404)
            
    def test_message_delete(self):
        msg = Message(id=10, text="This is a test message.", user_id = self.testuser_id)
        
        db.session.add(msg)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            res = c.post(f"/messages/10/delete", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIsNone(Message.query.get(10))
            
    def test_unauthorized_message_delete(self):
        
        badUser = User.signup('userTest','userTest@gmail.com', 'userTestPass', None) 
        bU_id = 1234
        badUser.id = bU_id
        
        msg = Message(id=10, text="This is a test message.", user_id = self.testuser_id)
        
        db.session.add_all([badUser, msg])
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1234
            res = c.post(f"/messages/10/delete", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Access unauthorized.", res.data)
                
    def test_message_delete_no_auth(self):
        msg = Message(id=10, text="This is a test message.", user_id = self.testuser_id)   

        db.session.add(msg)
        db.session.commit()
        with self.client as c:
            res = c.post(f"/messages/10/delete", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Access unauthorized.", res.data)
        