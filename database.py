import sqlite3
import os

def connect_to_db(db_path='/home/vr-dt-100/Desktop/chinook.db'):
    """
    Connect to the SQLite database at the given path. Handles errors gracefully and checks if the file exists.
    """
    try:
        # Check if the database file exists
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found at: {db_path}")
        
        print(f"Trying to connect to database at {db_path}")
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to database at {db_path}")
        return conn
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    except FileNotFoundError as fnf_error:
        print(fnf_error)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def get_table_columns(conn):
    """
    Fetch all table names and their column names in the database.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        tables_columns = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            tables_columns[table_name] = [column[1] for column in columns]
        
        return tables_columns
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return {}
