
import sqlite3
import os
import hashlib
import secrets
import hmac
from datetime import datetime

DB_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "scan_history.db"
)


def init_auth_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        260000
    ).hex()


def create_user(name, email, password):
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                INSERT INTO users
                (name, email, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name.strip(),
                email.strip().lower(),
                password_hash,
                salt,
                datetime.now().isoformat()
            ))
        return True, "Account created successfully!"

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def verify_user(email, password):
    with sqlite3.connect(DB_NAME) as conn:
        user = conn.execute("""
            SELECT id, name, email, password_hash, salt
            FROM users
            WHERE email = ?
        """, (email.strip().lower(),)).fetchone()

    if user is None:
        return None

    entered_hash = hash_password(password, user[4])

    if hmac.compare_digest(entered_hash, user[3]):
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2]
        }

    return None


init_auth_database()
