import sqlite3
import hashlib
from flask import session 
import json

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
            type TEXT NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, event_global_id),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            location TEXT,
            preferences TEXT, -- JSON string (dict: category -> weight)
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS liked_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_global_id TEXT NOT NULL,
        liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, event_global_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
""")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())


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
    event_type = event_data.get('type')  # "food" or "social"

    try:
        cursor.execute("""
            INSERT INTO saved_events (
                user_id, event_global_id, event_source, event_title,
                event_date, event_location, event_url, type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, global_id, source, title, date, location, url, event_type))
        
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
        SELECT event_global_id, event_source, event_title, event_date, event_location, event_url, type
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
            "url": row[5],
            "type": row[6]
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

def save_user_preferences(user_id, location, preferences):
    # if prefs is a list, init weights to 1
    if isinstance(preferences, list):
        preferences = {pref: 1 for pref in preferences}

    preferences_json = json.dumps(preferences)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_preferences (user_id, location, preferences)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET location=excluded.location, preferences=excluded.preferences
    """, (user_id, location, preferences_json))
    conn.commit()
    conn.close()

def get_user_preferences(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT location, preferences FROM user_preferences WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"location": row[0], "preferences": json.loads(row[1])}
    return None

def like_event(user_id, event_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    event_global_id = event_data.get('global_id')
    tags = event_data.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip().lower() for t in tags.split(",")]
    else:
        tags = [t.strip().lower() for t in tags]

    # Check if liked
    cursor.execute("""
        SELECT 1 FROM liked_events
        WHERE user_id = ? AND event_global_id = ?
    """, (user_id, event_global_id))
    already_liked = cursor.fetchone()

    print(f"[DEBUG] Liking event: {event_data}")
    print(f"[DEBUG] Already liked? {already_liked}")

    # Get prefs
    cursor.execute("SELECT preferences FROM user_preferences WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    preferences = json.loads(row[0]) if row else {}
    print(f"[DEBUG] Preferences before update: {preferences}")

    if already_liked:
        # UNLIKE
        cursor.execute("""
            DELETE FROM liked_events
            WHERE user_id = ? AND event_global_id = ?
        """, (user_id, event_global_id))

        for tag in tags:
            if tag in preferences:
                preferences[tag] = max(0, preferences[tag] - 1)

        result = {"status": "success", "message": "Event unliked."}

    else:
        # LIKE
        cursor.execute("""
            INSERT INTO liked_events (user_id, event_global_id)
            VALUES (?, ?)
        """, (user_id, event_global_id))

        # ensure event is saved
        cursor.execute("""
            SELECT 1 FROM saved_events WHERE event_global_id = ?
        """, (event_global_id,))
        exists_in_saved = cursor.fetchone()

        if not exists_in_saved:
            cursor.execute("""
                INSERT INTO saved_events (user_id, event_global_id, event_source, event_title, event_date, event_location, event_url, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                event_global_id,
                event_data.get('source', 'unknown'),
                event_data.get('title', 'No title'),
                event_data.get('date', ''),
                event_data.get('location', ''),
                event_data.get('url', ''),
                event_data.get('type', 'social')
            ))

        for tag in tags:
            if tag:
                preferences[tag] = preferences.get(tag, 0) + 1

        result = {"status": "success", "message": "Event liked."}

    preferences_json = json.dumps(preferences)
    cursor.execute("""
        UPDATE user_preferences
        SET preferences = ?
        WHERE user_id = ?
    """, (preferences_json, user_id))

    print(f"[DEBUG] Preferences after update: {preferences}")

    conn.commit()
    conn.close()
    return result

def get_liked_events(user_id: int) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"[DEBUG] Fetching liked events for user {user_id}")

    cursor.execute("""
        SELECT se.event_global_id, se.event_source, se.event_title, se.event_date, 
               se.event_location, se.event_url, se.type
        FROM liked_events le
        JOIN saved_events se ON le.event_global_id = se.event_global_id
        WHERE le.user_id = ?
        ORDER BY le.liked_at DESC
    """, (user_id,))
    
    liked_events_raw = cursor.fetchall()
    conn.close()

    print(f"[DEBUG] Raw rows: {liked_events_raw}")

    liked_events = []
    for row in liked_events_raw:
        liked_events.append({
            "global_id": row[0],
            "source": row[1],
            "title": row[2],
            "date": row[3],
            "location": row[4],
            "url": row[5],
            "type": row[6]
        })
    
    return liked_events

def get_events_posted_by_user(user_id: int) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, location, event_time, timezone
        FROM user_events
        WHERE user_id = ?
        ORDER BY event_time DESC
    """, (user_id,))
    
    posted_events_raw = cursor.fetchall()
    conn.close()

    posted_events = []
    for row in posted_events_raw:
        posted_events.append({
            "id": row[0],
            "title": row[1],
            "location": row[2],
            "event_time": row[3],
            "timezone": row[4]
        })
    
    return posted_events

def get_user_info(user_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, email
        FROM users
        WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"name": row[0], "email": row[1]}
    return None


if __name__ == "__main__":
    init_auth_db()
