import datetime
import sqlite3
from flask import render_template, request, redirect, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Connect to the database "notesapp.db"
connection = sqlite3.connect("notesapp.db", check_same_thread=False)

# Create a cursor instance which allows us to execute SQL queries on "notesapp.db"
cursor = connection.cursor()

# Silence any error that may arise when creating tables
# (in this case recreating a table that already exists)
try:
    cursor.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        hash TEXT NOT NULL
    )""")
    connection.commit()

    cursor.execute("""CREATE TABLE notes (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        content TEXT,
        last_mod_date DATETIME,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    connection.commit()
except:
    pass

def get_username():
    """Get username of logged in user"""

    # Query database for username of logged in user
    cursor.execute("SELECT username FROM users WHERE id = ?",
                    (session["user_id"],))

    # Return the username
    return cursor.fetchone()[0]

def add_note(title, content):
    """Add note to database"""

    # Connect to the database
    with connection:
        timestamp_obj = datetime.datetime.now()
        timestamp = timestamp_obj.strftime("%Y:%m:%d %H:%M:%S")

        cursor.execute("INSERT INTO notes(user_id, title, content, last_mod_date) VALUES(?, ?, ?, ?)",
                        (session["user_id"], title, content, timestamp))

def get_notes():
    """Retrieve all notes from database"""

    cursor.execute("SELECT * FROM notes WHERE user_id = ?",
                    (session["user_id"],))
    return cursor.fetchall()

def get_note(id):
    """Retrieve a note from database by its id"""

    cursor.execute("SELECT * FROM notes WHERE id = ? and user_id = ?",
                    (id, session["user_id"]))
    return cursor.fetchone()

def edit_note(id, title, content):
    """Edit note and update database"""

    # Connect to the database
    with connection:
        timestamp_obj = datetime.datetime.now()
        timestamp = timestamp_obj.strftime("%Y:%m:%d %H:%M:%S")

        cursor.execute("UPDATE notes SET title = ?, content = ?, last_mod_date =? WHERE id = ?",
                        (title, content, timestamp, id))

def delete_note(id):
    """Delete a note from database"""

    # Connect to the database
    with connection:
        cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
