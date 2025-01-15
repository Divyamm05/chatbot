import sqlite3
import os

def connect_to_db(db_path='/home/vr-dt-100/Desktop/database.db'):
    """
    Connect to the SQLite database at the given path. Handles errors gracefully and checks if the file exists.

    Args:
        db_path (str): The path to the SQLite database file.

    Returns:
        conn (sqlite3.Connection): SQLite connection object or None if the connection fails.
    """
    try:
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found at: {db_path}")
        
        conn = sqlite3.connect(db_path)
        print("Connected to the database successfully.")
        return conn
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    return None


def fetch_users(conn):
    """
    Fetch user information from the database.

    Args:
        conn (sqlite3.Connection): SQLite connection object.

    Returns:
        users (list): A list of users fetched from the database or an empty list if there's an error.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")  # Modify as per your table structure
        users = cursor.fetchall()
        return users
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    return []
