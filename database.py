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


def execute_sql_query(conn, query):
    """
    Executes a raw SQL query on the database.

    Args:
        conn (sqlite3.Connection): The database connection object.
        query (str): The SQL query string to execute.

    Returns:
        result (list): The result of the SQL query.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        
        if query.lower().startswith('select'):
            result = cursor.fetchall()  # Fetch all rows of a query result
        else:
            conn.commit()  # Commit changes for non-SELECT queries
            result = None  # Return None for non-SELECT queries
            
        return result
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None


def fetch_columns(conn, table_name):
    """
    Fetches column names from a given table.

    Args:
        conn (sqlite3.Connection): The database connection object.
        table_name (str): The table name to fetch columns from.

    Returns:
        columns (list): List of column names from the specified table.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]  # Get column names
        return columns
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []


def fetch_data_by_user_id(conn, user_id):
    """
    Fetches data from the database based on user_id.

    Args:
        conn (sqlite3.Connection): The database connection object.
        user_id (int): The user ID to search for.

    Returns:
        user_data (tuple): The user data if found, else None.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()  # Fetch a single row based on the user ID
        return user_data
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
