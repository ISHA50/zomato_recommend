import sqlite3
import os

def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'zomato.db')  # SQLite DB file
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


