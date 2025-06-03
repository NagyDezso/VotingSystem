import hashlib
import os
import secrets
from datetime import datetime, timedelta
from backend.database import get_db_connection
from backend.models import User, Session
from typing import Optional

def hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(stored_hash: str, password: str) -> bool:
    salt_hex, key_hex = stored_hash.split(':')
    salt = bytes.fromhex(salt_hex)
    key = bytes.fromhex(key_hex)
    new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return new_key == key

def create_session(user_id: int) -> Session:
    session_token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)",
        (user_id, session_token, expires_at)
    )
    connection.commit()
    cursor.close()
    connection.close()
    
    return Session(user_id=user_id, session_token=session_token)

def validate_session(session_token: str) -> Optional[int]:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT user_id, expires_at FROM sessions WHERE session_token = ?",
        (session_token,)
    )
    session_data = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if not session_data:
        return None
    
    user_id, expires_at = session_data
    # expires_at lehet string, ezért parse-olni kell
    expires_at_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expires_at_dt:
        return None
    
    return user_id

def delete_session(session_token: str):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM sessions WHERE session_token = ?",
        (session_token,)
    )
    connection.commit()
    cursor.close()
    connection.close()