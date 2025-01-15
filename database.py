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
    Execute a given SQL query on the connected database.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        query (str): The SQL query to be executed.

    Returns:
        result (list): Result of the query execution (if any) or None if the query does not return results.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Commit changes for non-SELECT queries (INSERT, UPDATE, DELETE)
        if query.strip().lower().startswith(('insert', 'update', 'delete')):
            conn.commit()
            return None  # No result for these queries

        # Fetch the results for SELECT queries
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None


def fetch_columns(conn, table_name):
    """
    Fetch column names from a given table.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        table_name (str): The name of the table from which to fetch column names.

    Returns:
        columns (list): A list of column names from the table.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]  # Extract column names from the result
        return columns
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []


def fetch_data_by_user_id(conn, user_id):
    """
    Fetch data for a user by their user ID.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        user_id (int): The user ID to look up.

    Returns:
        user_data (dict): Data of the user with the specified ID.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if user_data:
            # Return user data as a dictionary (using column names if available)
            columns = [description[0] for description in cursor.description]
            user_data_dict = dict(zip(columns, user_data))
            return user_data_dict
        else:
            return None
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
