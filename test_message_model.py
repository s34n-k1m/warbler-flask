import os
from unittest import TestCase
from app import app
from models import (User, Follows, Message, Like, db,
                    DEFAULT_IMAGE_URL, DEFAULT_HEADER_IMAGE_URL)
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

bcrypt = Bcrypt()

# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# disable CSRF checking for tests to work
app.config['WTF_CSRF_ENABLED'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler-test'))


class MessageModelTestCase(TestCase):
    """  Tests Message Model  """

    def setUp(self):
        """ Adds sample users """

        # recreates tables
        db.drop_all()
        db.create_all()

        # add user data
        user1 = User.signup("user1", "user1@user1.com", "password", None)
        db.session.add(user1)
        db.session.commit()
        self.user1 = user1

    def tearDown(self):
        """Rollback the data."""

        db.session.rollback()

    def test_message_creation(self):
        """ successfully create new message """
        self.assertEqual(len(self.user1.messages), 0)

        message = Message(user_id=self.user1.id, text="Testing, testing, 123.")

        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.user1.messages), 1)
    
    def test_failed_message_creation_length(self):
        """ fail to create message because of length exeding 140 characters """

        with self.assertRaises(exc.DataError or exc.InvalidRequestError):
            message = Message(user_id=self.user1.id, 
                            text="Testing"*100)

            db.session.add(message)
            db.session.commit()

        db.session.rollback()
        self.assertEqual(len(self.user1.messages), 0)

