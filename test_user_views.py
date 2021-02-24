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


class UserViewTestCase(TestCase):
    """  Tests User Views  """

    def setUp(self):
        """ Adds sample users """

        # recreates tables
        db.drop_all()
        db.create_all()

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

    def test_signup_load_page(self):
        """ Test that signup route properly renders signup page on a
        GET request  """

        with app.test_client() as client:
            resp = client.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Signup View Function Test Comment -->", html)

    def test_signup_success_redirect(self):
        """ Test that signup route properly redirects to root page on
        successful signup  """

        data = {
            "username": "user3",
            "email": "user3@user3.com",
            "password": "password"
        }

        with app.test_client() as client:
            resp = client.post("/signup",
                               data=data,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Home HTML Test Comment -->", html)
            self.assertIn("@user3", html)

    def test_signup_failure_existing_username(self):
        """ Test that signup route re-renders signup page if username 
        already taken  """

        data = {
            "username": "user1",
            "email": "user3@user3.com",
            "password": "password"
        }

        with app.test_client() as client:
            resp = client.post("/signup",
                               data=data,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Signup View Function Test Comment -->", html)
            self.assertIn("Username/Email already taken", html)

    def test_signup_failure_existing_email(self):
        """ Test that signup route re-renders signup page if email 
        already taken  """

        data = {
            "username": "user3",
            "email": "user1@user1.com",
            "password": "password"
        }

        with app.test_client() as client:
            resp = client.post("/signup",
                               data=data,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Signup View Function Test Comment -->", html)
            self.assertIn("Username/Email already taken", html)

    def test_login_load_page(self):
        """ Test that login route properly renders login page on a
        GET request  """

        with app.test_client() as client:
            resp = client.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Login View Function Test Comment -->", html)

    def test_login_success_redirect(self):
        """ Test that login route properly redirects to root page on
        successful signup  """

        data = {
            "username": "user1",
            "password": "password"
        }

        with app.test_client() as client:
            resp = client.post("/login",
                               data=data,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Home HTML Test Comment -->", html)
            self.assertIn("Hello, user1!", html)

    def test_login_failure(self):
        """ Test that login route properly redirects to root page on
        successful signup  """

        data = {
            "username": "user1",
            "password": "badpassword"
        }

        with app.test_client() as client:
            resp = client.post("/login",
                               data=data,
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("Invalid credentials.", html)

    def test_logout_success(self):
        """ Test that logout route properly redirects to root page on
        successful signup  """

        data = {
            "username": "user2",
            "password": "password"
        }

        with app.test_client() as client:
            resp = client.post("/login",
                               data=data,
                               follow_redirects=True)

            resp = client.post("/logout",
                               data={},
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("You have successfully logged out", html)

            with self.assertRaises(KeyError):
                session[CURR_USER_KEY]

    def test_delete_user_fail_not_logged_in(self):
        """ Makes sure a user cannot be deleted if not logged in """

        with app.test_client() as client:
            resp = client.post("/users/delete",
                               follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Make sure it redirects
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("<!-- Home Anon HTML Test Comment -->", html)

            self.assertEqual(len(User.query.all()), 2)
