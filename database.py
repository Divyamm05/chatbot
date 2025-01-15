import sqlite3
import os

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

