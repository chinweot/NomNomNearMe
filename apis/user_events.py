import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("USER_EVENTS_DB", "user_events.db")

def init_user_events_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            event_time TEXT NOT NULL,
            timezone TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user_event(title, location, event_time, timezone, description=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO user_events (title, location, event_time, timezone, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, location, event_time, timezone, description, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def format_event_time(event_time_str):
    """Convert '2025-07-23T09:57' to 'July 23, 2025 at 9:57 AM'"""
    try:
        dt = datetime.fromisoformat(event_time_str)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return event_time_str

def format_created_at(created_at_str):
    """Convert '2025-07-28T09:57:06.466820' to 'July 28, 2025'"""
    try:
        dt = datetime.fromisoformat(created_at_str)
        return dt.strftime("%B %d, %Y")
    except:
        return created_at_str

def get_user_events():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, location, event_time, timezone, description, created_at FROM user_events ORDER BY event_time ASC')
    events = c.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "title": row[1],
            "location": row[2],
            "event_time": format_event_time(row[3]),
            "timezone": row[4],
            "description": row[5],
            "created_at": format_created_at(row[6])
        }
        for row in events
    ]
