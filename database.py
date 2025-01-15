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


def fetch_table_data(conn, table_name):
    """
    Fetch data from a specified table in the database.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        table_name (str): The name of the table to fetch data from.

    Returns:
        data (list): A list of rows fetched from the table or an empty list if there's an error.
    """
    try:
        cursor = conn.cursor()

        # Check if the table exists in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"Table '{table_name}' does not exist.")
            return []
        
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        return data
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    return []


# Example usage
db_path = '/home/vr-dt-100/Desktop/chinook.db'
conn = connect_to_db(db_path)
if conn:
    table_name = 'users'  # Change this to the table you want to query
    users = fetch_table_data(conn, table_name)
    print(users)
