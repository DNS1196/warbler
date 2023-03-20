import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


  
class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        # Create sample user
        u1 = User.signup( "testuser1","test1@test.com", "HASHED_PASSWORD", None)
        u1_id=10
        u1.id = u1_id     
        db.session.commit()
        u1 = User.query.get(u1_id)
        self.u1 =u1
        self.u1_id =u1_id
        
        
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        msg = Message(text= "Test message", user_id= self.u1_id)
        self.msg = msg
        db.session.add(msg)
        db.session.commit()
        
        # Message should have a text and a user_id
        self.assertEqual(self.msg.text, "Test message")
        self.assertEqual(self.msg.user_id, 10)
        
    def test_message_likes(self):
        msg = Message(text= "Test message", user_id= self.u1_id)
        
        self.u1.likes.append(msg)
        db.session.commit()
        
        u1_likes= Likes.query.filter(Likes.user_id == self.u1_id).all()
        self.assertEqual(len(u1_likes), 1)
        self.assertEqual(u1_likes[0].user_id, self.u1_id)