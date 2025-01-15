import sqlite3
import pandas as pd

DB_PATH = '/home/vr-dt-100/Desktop/database.db'

# Function to connect to the database
def connect_to_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Function to fetch users from the database
def fetch_users():
    conn = connect_to_db()
    query = "SELECT * FROM users"  # Replace 'users' with your actual table name
    users_df = pd.read_sql(query, conn)
    conn.close()
    return users_df

# Function to fetch user by name (e.g., "John")
def fetch_user_by_name(name):
    conn = connect_to_db()
    query = "SELECT * FROM users WHERE name = ?"  # Replace 'users' with your table name and 'name' with the column name for user names
    user_data = pd.read_sql(query, conn, params=(name,))
    conn.close()
    return user_data
