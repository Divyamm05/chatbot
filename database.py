import sqlite3

# Function to connect to the SQLite database
def connect_to_db(db_path):
    try:
        conn = sqlite3.connect(db_path)  # Connect to the SQLite database
        print("Connected to SQLite database")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to fetch users from the database
def fetch_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_details")  # Query to fetch all users
    users = cursor.fetchall()  # Fetch all records
    return users

# Main function to execute the chatbot logic
def main():
    db_path = "/home/vr-dt-100/Desktop/your_database_name.db"  # Path to your SQLite database
    conn = connect_to_db(db_path)

    if conn:
        users = fetch_users(conn)
        for user in users:
            print(f"User ID: {user[0]}, Username: {user[1]}, First Name: {user[2]}, Last Name: {user[3]}")

        conn.close()  # Close the database connection

if __name__ == "__main__":
    main()
