import sqlite3
import hashlib
from flask import session 

DB_PATH = "user_info.db"

def init_auth_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_global_id TEXT NOT NULL,
            event_source TEXT NOT NULL,
            event_title TEXT NOT NULL,
            event_date TEXT,
            event_location TEXT,
            event_url TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, event_global_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(name, email, password, phone):
    hashed_pw = hash_password(password)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if '@' not in email:
        return {"status": "fail", "message": "Invalid email address"}

    try:
        cursor.execute("""
            INSERT INTO users (name, email, password, phone)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed_pw, phone))
        conn.commit()
        
        user_id = cursor.lastrowid
        session['user_id'] = user_id

        result = {"status": "success", "message": "User registered successfully.", "user_id": user_id}
    except sqlite3.IntegrityError:
        result = {"status": "fail", "message": "Email already exists."}
    except Exception as e:
        result = {"status": "fail", "message": f"Registration failed: {e}"}
    
    conn.close()
    return result

def login_user(username, password):
    hashed = hash_password(password)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM users
        WHERE name = ? AND password = ?
    """, (username, hashed))
    result = cursor.fetchone()
    conn.close()

    if result:
        user_id = result[0]
        session['user_id'] = user_id # Set user_id in session upon successful login
        return {"status": "access granted", "user_id": user_id}
    else:
        return {"status": "access denied"}

def save_event(user_id, event_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    source = event_data.get('source')
    global_id = event_data.get('global_id')
    title = event_data.get('title')
    date = event_data.get('date')
    location = event_data.get('location')
    url = event_data.get('url')

    try:
        cursor.execute("""
            INSERT INTO saved_events (user_id, event_global_id, event_source, event_title, event_date, event_location, event_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, global_id, source, title, date, location, url)) 
        conn.commit()
        result = {"status": "success", "message": "Event saved successfully."}
    except sqlite3.IntegrityError:
        result = {"status": "fail", "message": "Event already saved by this user."}
    except Exception as e:
        result = {"status": "fail", "message": f"Error saving event: {e}"}
    finally:
        conn.close()
    return result

def get_saved_events(user_id: int) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT event_global_id, event_source, event_title, event_date, event_location, event_url
        FROM saved_events
        WHERE user_id = ?
        ORDER BY saved_at DESC
    """, (user_id,))
    
    saved_events_raw = cursor.fetchall()
    conn.close()

    saved_events_list = []
    for row in saved_events_raw:
        saved_events_list.append({
            "global_id": row[0],
            "source": row[1],
            "title": row[2],
            "date": row[3], 
            "location": row[4], 
            "url": row[5]
        })
    return saved_events_list

def delete_saved_event(user_id: int, event_global_id: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM saved_events
            WHERE user_id = ? AND event_global_id = ?
        """, (user_id, event_global_id))
        conn.commit()
        if cursor.rowcount > 0:
            result = {"status": "success", "message": "Event unsaved successfully."}
        else:
            result = {"status": "fail", "message": "Event not found for this user."}
    except Exception as e:
        result = {"status": "fail", "message": f"Error unsaving event: {e}"}
    finally:
        conn.close()
    return result
    
if __name__ == "__main__":
    init_auth_db()