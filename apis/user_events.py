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
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user_event(title, location, event_time, timezone):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO user_events (title, location, event_time, timezone, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, location, event_time, timezone, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_user_events():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, location, event_time, timezone, created_at FROM user_events ORDER BY event_time ASC')
    events = c.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "title": row[1],
            "location": row[2],
            "event_time": row[3],
            "timezone": row[4],
            "created_at": row[5]
        }
        for row in events
    ]
