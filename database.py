import sqlite3
import os
import streamlit as st

# Database path
db_path = "/home/vr-dt-100/Desktop/database2.db"

def connect_to_db(db_path):
    """
    Connect to the SQLite database at the given path. Returns the connection or None if an error occurs.
    """
    try:
        # Check if the database file exists
        if not os.path.exists(db_path):
            st.error(f"Database file not found at: {db_path}")
            return None
        
        # Establish connection to the database
        conn = sqlite3.connect(db_path)
        st.success(f"Successfully connected to the database at: {db_path}")
        return conn
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

# Streamlit App Layout
st.title("Database Connection Test")

# Button to test connection
if st.button("Test Database Connection"):
    conn = connect_to_db(db_path)
    
    if conn:
        st.write("Database connection is valid!")
        # Example query to fetch table names
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if tables:
                st.write("Available tables in the database:")
                for table in tables:
                    st.write(f"- {table[0]}")
            else:
                st.write("No tables found in the database.")
        except sqlite3.Error as e:
            st.error(f"Error fetching tables: {e}")
        finally:
            conn.close()
    else:
        st.error("Failed to connect to the database.")

# Display database path for reference
st.write(f"Database Path: `{db_path}`")

# Instructions for resolving common issues
st.info("""
### Troubleshooting Tips:
- Ensure the file path is correct and the database file exists.
- Verify file permissions for the database.
- Ensure the correct database format (SQLite).
""")
