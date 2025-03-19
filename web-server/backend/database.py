import mysql.connector
from fastapi import HTTPException
import threading
import os
from backend.models import Vote

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "voting_user"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_DATABASE", "voting_system"),
}

db_lock = threading.Lock()

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise HTTPException(status_code=500, detail="Database connection error")

def setup_database():
    """Initialize database tables if they don't exist"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create votes table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                vote VARCHAR(255) NOT NULL,
                question_id INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create questions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create options table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS options (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question_id INT NOT NULL,
                option_text VARCHAR(255) NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        """)
        
        connection.commit()
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
    finally:
        if "connection" in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def write_vote_to_db(vote_data: Vote, question_id=None):
    with db_lock:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Insert the vote
            if question_id:
                query = "INSERT INTO votes (name, vote, question_id) VALUES (%s, %s, %s)"
                values = (vote_data.name, vote_data.vote, question_id)
            else:
                query = "INSERT INTO votes (name, vote) VALUES (%s, %s)"
                values = (vote_data.name, vote_data.vote)
                
            cursor.execute(query, values)
            connection.commit()
            print(f"Vote recorded: {vote_data.name} - {vote_data.vote}")

        except Exception as e:
            print("Database error:", e)
            raise HTTPException(status_code=500, detail="Database error")
        finally:
            if "connection" in locals() and connection.is_connected():
                cursor.close()
                connection.close()
