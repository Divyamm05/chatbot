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


def fetch_tables_and_columns(conn):
    """
    Fetch all tables and their columns from the database.

    Args:
        conn (sqlite3.Connection): SQLite connection object.

    Returns:
        tables (dict): A dictionary where keys are table names and values are lists of column names.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        tables_columns = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")  # Fetch column info
            columns = [column[1] for column in cursor.fetchall()]
            tables_columns[table_name] = columns

        return tables_columns
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    return {}


def fetch_data_for_query(conn, table, column, value):
    """
    Fetch data from a specific table and column based on user input.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        table (str): The table name.
        column (str): The column name.
        value (str): The value to search for in the column.

    Returns:
        result (list): A list of rows matching the query.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE {column} LIKE ?", (f"%{value}%",))
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    return []
