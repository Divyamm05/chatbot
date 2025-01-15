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


def execute_dynamic_query(conn, table_name, column_name, search_value):
    """
    Executes a dynamic SQL query to search for a value in a specified column of a specified table.
    After querying, it verifies the results and handles ambiguity by requesting clarification if needed.
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

        # Query with LIKE to find matching values
        query = f"SELECT * FROM {table_name} WHERE {column_name} LIKE ?"
        cursor.execute(query, ('%' + search_value + '%',))
        results = cursor.fetchall()

        # If no results are found
        if len(results) == 0:
            return None, f"No records found for '{search_value}' in the column '{column_name}' of the table '{table_name}'."

        # If exactly one result is found, return it
        if len(results) == 1:
            return results[0], None  # Return the entire row (or specific column data if needed)

        # If multiple results are found, ask for clarification
        clarification_message = f"Multiple records found for '{search_value}' in the column '{column_name}' of the table '{table_name}':\n"
        for i, result in enumerate(results, 1):
            clarification_message += f"{i}. {result}\n"

        clarification_message += f"Please provide more details (e.g., another keyword or ID) to narrow down the search."

        return None, clarification_message

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None, f"An error occurred while querying the table '{table_name}'."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, "An unexpected error occurred."
    finally:
        cursor.close()  # Ensure the cursor is closed after usage
        conn.close()  # Optionally close the connection if no longer needed

