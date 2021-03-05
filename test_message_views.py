"""Message View tests."""

import os
from unittest import TestCase
from app import app, CURR_USER_KEY
from flask import session
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

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")


USER_IMG_URL = ("https://images.theconversation.com/files/350865/original/file-20200803-24-50u91u.jpg?ixlib=rb-1.1.0&q=45&auto=format&w=1200&h=675.0&fit=crop")


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        # recreates tables
        db.drop_all()
        db.create_all()

        # User.query.delete()
        # Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        # add user data
        user1 = User.signup("user1", "user1@user1.com", "password", None)
        user2 = User.signup("user2", "user2@user2.com",
                            "password", USER_IMG_URL)

        db.session.add(user1)
        db.session.add(user2)

        db.session.commit()

        self.user1_id = user1.id
        self.user2_id = user2.id

    def tearDown(self):
        """Rollback the data."""

        db.session.rollback()

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

    def test_add_message_fail_not_logged_in(self):
        """ Makes sure a message cannot be created if not logged in """

        with self.client as c:
            resp = c.post("/messages/new",
                          data={"text": "Hello"},
                          follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("<!-- Home Anon HTML Test Comment -->", html)

            msg = Message.query.one_or_none()
            self.assertFalse(msg)

    def test_delete_message_fail_not_logged_in(self):
        """ Makes sure a message cannot be deleted if not logged in """

        msg = Message(text="TestMessage1", user_id=self.user1_id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            resp = c.post(f"/messages/{msg.id}/delete",
                          follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("<!-- Home Anon HTML Test Comment -->", html)

            msg = Message.query.get(msg.id)
            self.assertTrue(msg)
    

