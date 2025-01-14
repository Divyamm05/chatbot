import pandas as pd
import streamlit as st
import openai
import sqlite3
import os
from utils import load_chat_history, save_chat_history
from visualizations import generate_pie_chart, generate_bar_chart, preview_uploaded_file  # Updated import
from file_handlers import handle_uploaded_file

# Load API key from Streamlit's secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Set model parameters
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 500

# File to store chat history
CHAT_HISTORY_FILE = 'chat_history.json'

# SQLite Database path
DB_PATH = "/home/vr-dt-100/Desktop/your_database_name.db"  # Update with your actual database path

# Function to connect to SQLite database
def connect_to_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        print("Connected to SQLite database")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Function to fetch user details from the database
def fetch_user_details(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_details WHERE username=?", (username,))
    user = cursor.fetchone()  # Fetch one user record
    return user

# Function to process chat input and query the database
def process_chat_input(prompt, db_path=DB_PATH):
    conn = connect_to_db(db_path)
    user_data = None
    if conn:
        # Extract username from the user input or chat context
        username = extract_username_from_prompt(prompt)  # Function to dynamically extract the username
        if username is None:
            username = "johndoe"  # Fallback if username is not extracted from the prompt

        # Query user details
        user_data = fetch_user_details(conn, username)
        conn.close()

    # Process the chat input
    if user_data:
        response = f"Hello, {user_data[2]} {user_data[3]}! How can I assist you today?"
    else:
        response = "User not found. Would you like to upload a file for chart generation instead?"

    return response

# Function to extract username from the prompt (simple example)
def extract_username_from_prompt(prompt):
    # Example: If the prompt contains a username, extract it
    if "my username is" in prompt.lower():
        return prompt.split("my username is")[-1].strip()
    return None

# Function to interact with OpenAI's GPT model (updated for OpenAI's new API)
def ask_openai(prompt):
    try:
        # Define the conversation structure
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        
        # Call OpenAI's new chat_completions.create method for v1.0.0 and above
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use other available models here
            messages=messages,  # Send the conversation messages
            max_tokens=MAX_TOKENS
        )
        
        # Get the response content
        return response['choices'][0]['message']['content'].strip()  # Fetch the assistant's reply
    except Exception as e:
        return f"Error: {str(e)}"

# Load the previous chat history if available
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar for chart selection and file attachment
with st.sidebar:
    col1, col2 = st.columns([3, 1])  # Create two columns in the sidebar for layout
    
    # Sidebar: Add a dropdown menu for selecting chart type
    st.title('🤖💬 CHATBOT')
    
    with col1:
        # Sidebar: Add the "Start New Chat" button next to the title
        if st.button('Start New Chat'):
            st.session_state.messages = []  # Clears the chat history
            save_chat_history(st.session_state.messages)  # Save the empty history
            st.rerun()  # Rerun the app to refresh the interface

    # Sidebar: Add a dropdown menu for selecting chart type
    chart_type = st.selectbox(
        "Select a chart type for visualization",
        ("Select a chart", "Pie Chart", "Bar Chart")
    )

    # File uploader for attachments (moved below the chart selection and slider)
    uploaded_file = st.file_uploader("Upload an attachment (optional)", type=["txt", "csv", "xlsx", "pdf", "jpg", "png", "docx"])

# Handle file uploads and visualization-related tasks
data, columns = handle_uploaded_file(uploaded_file)

# Initialize data to None by default
x_column = None
y_column = None
pie_column = None  # Variable to store selected Pie Chart column
if len(columns) > 0:
    # Pie chart and bar chart options for selecting columns
    if chart_type == "Bar Chart":
        x_column_index = st.selectbox("Select X-axis column", options=columns)
        x_column = data[x_column_index] if x_column_index else None

        y_column_index = st.selectbox("Select Y-axis column", options=columns)
        y_column = data[y_column_index] if y_column_index else None

    elif chart_type == "Pie Chart":
        # Add the column selection for Pie Chart using dropdown
        pie_column_index = st.selectbox("Select column for Pie Chart", options=columns)
        pie_column = data[pie_column_index] if pie_column_index else None

# Conditionally display the sliders for range values for both axes
if chart_type == "Bar Chart" and x_column is not None and y_column is not None:
    # Single slider for both X and Y axis
    start_value, end_value = st.slider(
        "Select range of values to visualize",
        min_value=0,
        max_value=len(x_column),  # Set max value to the length of the data
        value=(0, min(10, len(x_column))),  # Default range (start from 0 to 10 or data length)
        step=1,
        help="Select the start and end values for both X and Y axes"
    )

    if st.button("Generate Bar Chart"):
        # Pass column names as strings (use .name to get the column name)
        generate_bar_chart(data, x_column.name, y_column.name, start_value, end_value, start_value, end_value)


# Pie chart dropdown functionality
if chart_type == "Pie Chart" and pie_column is not None:
    # Dropdown for Pie Chart column selection
    start_value, end_value = st.slider(
        "Select range of data for Pie Chart",
        min_value=0,
        max_value=len(data),  # Set max value to the length of the data
        value=(0, min(10, len(data))),  # Default range (start from 0 to 10 or data length)
        step=1,
        help="Select the range of data for the Pie Chart"
    )

    if st.button("Generate Pie Chart"):
        # Ensure that pie_column is not empty or None
        if pie_column is not None and not pie_column.empty:
            generate_pie_chart(data, pie_column.name, start_value, end_value)
        else:
            st.error("Please select a valid column for the Pie Chart")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input for the prompt
if prompt := st.chat_input(f"Enter prompt "):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with message_placeholder:
            st.markdown("**Generating response...**")
            st.spinner("Thinking...")

        try:
            # Process the chat input
            response = process_chat_input(prompt, DB_PATH)
            message_placeholder.markdown(response)

            # Ask OpenAI for response (updated for v1.0.0 API)
            openai_response = ask_openai(prompt)
            message_placeholder.markdown(f"**Response from AI**: {openai_response}")

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            message_placeholder.markdown(f"Error: {str(e)}")

# Save the updated chat history to the file
save_chat_history(st.session_state.messages)
