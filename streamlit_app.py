import sqlite3
import streamlit as st

# Function to connect to the SQLite database
def connect_to_db():
    try:
        conn = sqlite3.connect('database.db')  # Database file in the repository
        st.success("Successfully connected to the database!")
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Streamlit app interface
st.title("Streamlit App with Database on Streamlit Cloud")

if st.button("Connect to Database"):
    conn = connect_to_db()
    if conn:
        st.write("Database connection is successful!")
        # Example query to check if everything is working
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if tables:
            st.write("Available tables:")
            for table in tables:
                st.write(f"- {table[0]}")
        else:
            st.write("No tables found.")