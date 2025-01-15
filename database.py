import sqlite3
import os

def connect_to_db(db_path):
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


def execute_dynamic_query(conn, table_name, column_name, search_value, exact_match=False):
    """
    Executes a dynamic SQL query to search for a value in a specified column of a specified table.
    If exact_match is True, uses '=' for exact matching, otherwise uses 'LIKE'.
    """
    try:
        cursor = conn.cursor()

        # Ensure that the table and column exist in the database schema
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        table_exists = cursor.fetchone()
        if not table_exists:
            return None, f"The table '{table_name}' does not exist in the database."

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        if column_name not in columns:
            return None, f"The column '{column_name}' does not exist in the table '{table_name}'."

        # Choose between LIKE or = based on exact_match
        if exact_match:
            query = f"SELECT * FROM {table_name} WHERE {column_name} = ?"
        else:
            query = f"SELECT * FROM {table_name} WHERE {column_name} LIKE ?"

        # Use parameterized query to prevent SQL injection
        cursor.execute(query, ('%' + search_value + '%',) if not exact_match else (search_value,))
        
        # Fetch all rows
        results = cursor.fetchall()

        # Check if no results were found
        if len(results) == 0:
            return None, f"No records found for '{search_value}' in the column '{column_name}' of the table '{table_name}'."

        # If exactly one result is found, return it
        if len(results) == 1:
            return results[0], None  # Return the entire row

        # If multiple results are found, ask for clarification
        if len(results) > 1:
            return None, f"Multiple records found for '{search_value}' in the column '{column_name}' of the table '{table_name}':\n"
        
        # Process each result individually
        for i, row in enumerate(results, 1):
            result_str = f"{i}. {row}"
            clarification_message += f"\n{result_str}"

        return None, clarification_message

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None, f"An error occurred while querying the table '{table_name}'."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, "An unexpected error occurred."
