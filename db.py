import sqlite3
import hashlib

DB_PATH = "user_info.db"

def init_auth_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_title TEXT NOT NULL,
            event_description TEXT,  -- Currently not used by your API structure
            event_date TEXT,
            event_location TEXT,
            event_url TEXT,
            event_data TEXT,         -- Designed to store the full JSON data
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
                   """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(name, email, password):
    hashed_pw = hash_password(password)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if '@' not in email:
        return {"status": "fail", "message": "Unvalid email address"}

    try:
        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, hashed_pw))
        conn.commit()
        result = {"status": "success", "message": "User registered successfully."}
    except sqlite3.IntegrityError:
        result = {"status": "fail", "message": "Email already exists."}
    
    conn.close()
    return result

def login_user(email, password):
    hashed = hash_password(password)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM users
        WHERE email = ? AND password = ?
    """, (email, hashed))
    result = cursor.fetchone()
    conn.close()

    if result:
        print("Successful")
        return {"status": "access granted"}
    else:
        print("Unsuccesful")
        return {"status": "access denied"}


# use the following below in the main file 
if __name__ == "__main__":
    init_auth_db()
