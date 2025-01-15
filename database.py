import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to connect to the SQLite database
def connect_to_db(db_path):
    try:
        conn = sqlite3.connect(db_path)  # Connect to the SQLite database
        logging.info("Connected to SQLite database successfully.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None

# Function to fetch users from the database
def fetch_users(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_details")  # Query to fetch all users
        users = cursor.fetchall()  # Fetch all records
        logging.info(f"Fetched {len(users)} user(s) from the database.")
        return users
    except sqlite3.Error as e:
        logging.error(f"Error fetching users: {e}")
        return []

# Function to format user data as a dictionary for easy access
def format_user_data(users):
    user_dict = {}
    for user in users:
        user_dict[user[0]] = {  # Assuming the first column is user ID
            'username': user[1],
            'first_name': user[2],
            'last_name': user[3]
        }
    return user_dict

# Main function to execute the chatbot logic and fetch user data
def main(db_path):
    conn = connect_to_db(db_path)

    if conn:
        try:
            users = fetch_users(conn)
            if users:
                formatted_users = format_user_data(users)
                logging.info(f"Fetched and formatted users: {formatted_users}")
            else:
                logging.warning("No users found or error fetching data.")
        finally:
            conn.close()  # Ensure connection is closed
            logging.info("Database connection closed.")
    else:
        logging.error("Failed to connect to the database.")

if __name__ == "__main__":
    # Dynamically set the database path or pass it directly
    db_path = "/home/vr-dt-100/Desktop/your_database_name.db"  # Path to your SQLite database
    main(db_path)
