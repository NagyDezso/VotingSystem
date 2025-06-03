import sqlite3
from fastapi import HTTPException
import threading
import os
from backend.models import Vote
from backend.textlogger import save_vote_to_file


# Create database directory if it doesn't exist
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DB_DIR, exist_ok=True)

# SQLite database file path
DB_PATH = os.path.join(DB_DIR, "voting_system.db")

# Thread lock for database operations
db_lock = threading.Lock()

def get_db_connection():
    """Get a connection to the SQLite database"""
    try:
        # SQLite will create the file if it doesn't exist
        connection = sqlite3.connect(DB_PATH)
        # Enable foreign keys
        connection.execute("PRAGMA foreign_keys = ON")
        # Return dictionary-like rows
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as err:
        print(f"Database connection error: {err}")
        raise HTTPException(status_code=500, detail="Database connection error")

def setup_database():
    """Initialize database tables if they don't exist"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create options table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                option_text TEXT NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        """)
        
        # Create votes table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                vote TEXT NOT NULL,
                question_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        connection.commit()
        print(f"Database initialized successfully at {DB_PATH}")
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        if "connection" in locals():
            cursor.close()
            connection.close()

def write_vote_to_db(vote_data: Vote, question_id=None):
    with db_lock:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert the vote
            if question_id:
                query = "INSERT INTO votes (name, vote, question_id) VALUES (?, ?, ?)"
                vote_str = f"{vote_data.name};{vote_data.vote}"
                save_vote_to_file(vote_str)

                values = (vote_data.name, vote_data.vote, question_id)
            else:
                query = "INSERT INTO votes (name, vote) VALUES (?, ?)"
                vote_str = f"{vote_data.name};{vote_data.vote}"
                save_vote_to_file(vote_str)

                values = (vote_data.name, vote_data.vote)
                
            cursor.execute(query, values)
            connection.commit()
            print(f"Vote recorded: {vote_data.name} - {vote_data.vote}")

        except Exception as e:
            print("Database error:", e)
            raise HTTPException(status_code=500, detail="Database error")
        finally:
            if "connection" in locals():
                cursor.close()
                connection.close()

def get_user_by_id(user_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    if user:
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    return None