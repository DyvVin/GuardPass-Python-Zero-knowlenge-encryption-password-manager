import os
import sqlite3

def get_db_connection():
    db_path = os.environ.get("GUARDPASS_DB_PATH")
    
    if not db_path:
        raise RuntimeError("Database path not initialized in configuration.")
        
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;") # renovate
    conn.row_factory = sqlite3.Row
    return conn
