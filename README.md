# Warbler
Fullstack Twitter clone. The backend is built with a Flask, PostgreSQL, SQLAlchemy. The frontend is built with Jinja. jQuery and Axios is also utilized in the frontend.

Deployed demo can be viewed [here](https://seankim-warbler.herokuapp.com/).   
Note: there may be a short lag in loading the demo due to Heroku's dyno sleeping. 

# Features
Warbler allows users to:
* Sign up/login 
* Edit user profile info
* Follow/unfollow other users
* Write a message (similar to a Tweet)
* Delete a message
* Like other users' messages
* Search for users by username

# Getting Started
1. Clone this repository
2. `cd warbler`
3. Create the virtual environment
* `python3 -m venv venv`
* `source venv/bin/activate`
* `pip3 install -r requirements.txt`
4. Create the database
* `createdb warbler`
* `createdb warbler-test`
* `python3 seed.py`
4. Start the server
* `flask run`

# Testing
* All tests: `python3 -m unittest`
* Specific test file: `python3 -m unittest test_filename.py` 

# Authors
My pair for this project was @kellenrowe  