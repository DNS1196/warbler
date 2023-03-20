"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        
        u1 = User.signup("test1", 'test1@gmail.com', 'password1', None)
        u1_id=10
        u1.id = u1_id      
        
        u2 = User.signup("test2", 'test2@gmail.com', 'password2', None)
        u2_id=20
        u2.id = u2_id
        
        db.session.commit()
        
        u1 = User.query.get(u1_id)
        u2 = User.query.get(u2_id)
        
        self.u1 =u1
        self.u1_id =u1_id
        self.u2 =u2
        self.u2_id =u2_id
                
        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.email, 'test@test.com')
        self.assertEqual(u.username, 'testuser')
        
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
        
    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertTrue(User.is_following(self.u1,self.u2))
        self.assertFalse(User.is_following(self.u2,self.u1))
        
    def test_user_is_followed(self):
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertTrue(User.is_followed_by(self.u2,self.u1))
        self.assertFalse(User.is_followed_by(self.u1,self.u2))
        self.assertFalse(User.is_followed_by(self.u1,self.u1))
       
    def test_valid_signup(self):
        userTest = User.signup('userTest', 'userTest@gmail.com', 'userTestPass', None)
        uTid= 11
        userTest.id=uTid
        db.session.commit()
        
        self.assertIsNotNone(userTest)
        self.assertEqual(userTest.username, 'userTest')
        self.assertEqual(userTest.email, 'userTest@gmail.com')
        self.assertTrue(userTest.password.startswith('$2b$'))
        
    def test_invalid_username_signup(self):
        badUser = User.signup(None,'userTest@gmail.com', 'userTestPass', None) 
        bUid = 1234
        badUser.id = bUid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
        
    def test_invalid_email_signup(self):
        badUser = User.signup('userTest',None, 'userTestPass', None) 
        bUid = 1234
        badUser.id = bUid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
            
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as contex:
            User.signup('badUser','userTest@gmail.com', '', None)
        with self.assertRaises(ValueError) as contex:
            User.signup('badUser','userTest@gmail.com', None, None)
        
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password1")
        self.assertEqual(u, self.u1)

    def test_invalid_username(self):
         
        user = User.authenticate("testwrongusername", "password1")
        self.assertFalse(user)

    def test_invalid_pass(self):
        user = User.authenticate(self.u1.username, 'badpassword')
        self.assertFalse(user)
        