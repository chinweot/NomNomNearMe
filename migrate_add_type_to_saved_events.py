import sqlite3

def add_type_column_to_saved_events(db_path='user_info.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE saved_events ADD COLUMN type TEXT;")
        print("Column 'type' added to saved_events table.")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("Column 'type' already exists.")
        else:
            print(f"Error: {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_type_column_to_saved_events()
