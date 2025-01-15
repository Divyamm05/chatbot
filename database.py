import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to the database
def connect_to_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        logging.info("Connected to the database.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Connection error: {e}")
        return None

# Fetch all users
def fetch_users(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_details")
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error fetching users: {e}")
        return []

# Fetch a user by ID
def fetch_user_by_id(conn, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_details WHERE id = ?", (user_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error fetching user by ID: {e}")
        return None

# Fetch users by gender
def fetch_users_by_gender(conn, gender):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_details WHERE gender = ?", (gender,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error fetching users by gender: {e}")
        return []

# Fetch active users (assuming active status is stored as a column `active`)
def fetch_active_users(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_details WHERE active = 1")
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error fetching active users: {e}")
        return []
