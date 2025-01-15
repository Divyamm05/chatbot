import openai
import streamlit as st
import sqlite3
import os
from datetime import datetime

# Set OpenAI API key
openai.api_key = 'your-openai-api-key-here'

# Connect to SQLite database
def connect_to_db():
    conn = sqlite3.connect("chat_history.db")
    return conn

# Create the table if it doesn't exist
def create_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Fetch all users from the database
def fetch_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Save chat history to database
def save_chat_history(messages):
    conn = connect_to_db()
    cursor = conn.cursor()
    for message in messages:
        cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)",
                       (message["role"], message["content"]))
    conn.commit()
    conn.close()

# Get OpenAI response (using the new API format)
def get_openai_response(conversation):
    response = openai.completions.create(
        model="gpt-3.5-turbo",  # Specify the model
        messages=conversation,
        max_tokens=2500  # Adjust token limit as needed
    )
    return response['choices'][0]['message']['content']

# Create table if not already created
create_table()

# Streamlit chat UI
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Enter prompt:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with message_placeholder:
            st.markdown("**Generating response...**")
            st.spinner("Thinking...")

        try:
            # Construct the conversation history as a list of messages
            system_message = {"role": "system", "content": "You are a helpful assistant."}
            conversation = [system_message, {"role": "user", "content": prompt}]

            # Connect to the database and check for queries related to user data
            conn = connect_to_db()

            # If the prompt contains a request for a user ID (e.g., "Give me user id of john")
            if "user id of" in prompt.lower():
                user_name = prompt.split("user id of")[-1].strip()  # Extract the user name from the prompt
                users = fetch_users(conn)
                user_id = None
                for user in users:
                    if user_name.lower() in user[1].lower():  # Assuming the name is in the second column
                        user_id = user[0]  # Assuming the ID is in the first column
                        break

                if user_id:
                    message_placeholder.markdown(f"The user ID of {user_name} is {user_id}.")
                else:
                    message_placeholder.markdown(f"User {user_name} not found in the database.")
            else:
                # Get response from OpenAI using the new API method
                response_message = get_openai_response(conversation)
                st.markdown(response_message)
                st.session_state.messages.append({"role": "assistant", "content": response_message})
                save_chat_history(st.session_state.messages)  # Save to history after response

        except Exception as e:
            message_placeholder.markdown(f"An error occurred: {str(e)}")



# Save the updated chat history to the file
save_chat_history(st.session_state.messages)
