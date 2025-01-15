import sqlite3
import os

def connect_to_db(db_path='/home/vr-dt-100/Desktop/chinook.db'):
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

def fetch_columns(conn, table_name):
    """
    Fetch the column names of a given table.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        table_name (str): Name of the table to fetch columns from.

    Returns:
        columns (list): A list of column names from the table or an empty list if there's an error.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]  # column[1] is the column name
        return columns
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    return []

def fetch_data_by_user_id(conn, user_id):
    """
    Fetch user data based on user ID.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        user_id (str): The user ID to search for.

    Returns:
        user_data (str): A string representation of the user's data or an empty string if no user is found.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return f"Name: {user[1]}, Email: {user[2]}"  # Adjust indices based on your table structure
        else:
            return None
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    return None
