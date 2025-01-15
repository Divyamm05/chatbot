import openai
import streamlit as st
import requests  # Added for downloading the .db file from GitHub
import sqlite3
import os
from utils import load_chat_history, save_chat_history
from visualizations import generate_pie_chart, generate_bar_chart
from file_handlers import handle_uploaded_file
from database import connect_to_db, execute_dynamic_query

# Load API key from Streamlit's secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Set model parameters
OPENAI_MODEL = "gpt-3.5-turbo"  # Set the model you want to use
MAX_TOKENS = 2500  # Set the max token limit for the OpenAI API

# GitHub repository URL for the raw .db file
GITHUB_DB_URL = "https://github.com/Divyamm05/chatbot/raw/main/chinook.db"  # Raw link to GitHub file

# File to store chat history
CHAT_HISTORY_FILE = 'chat_history.json'

# Load the previous chat history if available
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Function to download the .db file from GitHub
def download_db_from_github():
    try:
        response = requests.get(GITHUB_DB_URL)
        if response.status_code == 200:
            # Save the database file temporarily in the current directory
            with open("database2.db", "wb") as f:
                f.write(response.content)
            if os.path.exists("database2.db") and os.path.getsize("database2.db") > 0:
                st.success("Downloaded database from GitHub successfully!")
            else:
                st.error("Downloaded database is empty or invalid.")
        else:
            st.error(f"Failed to download the database from GitHub. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error downloading database: {str(e)}")

# Download the .db file from GitHub every time the app runs
download_db_from_github()

# Function to connect to the SQLite database
def connect_to_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.DatabaseError as e:
        st.error(f"Database connection error: {e}")
        return None

# Function to get column names from a given table
def get_column_names(conn, table_name):
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        return [column[1] for column in columns]
    except sqlite3.DatabaseError as e:
        st.error(f"Error fetching column names: {e}")
        return []

# Initialize database connection
conn = connect_to_db("database2.db")
if conn is None:
    st.error("Failed to connect to the database. Please check the .db file.")

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

# Database interaction: Connect and execute queries directly
if conn:
    table_name = "sqlite_master"  # Default to the sqlite_master table for column names
    column_names = get_column_names(conn, table_name)  # Get the column names directly from the master table
    selected_column = st.selectbox("Select a column to query", column_names)
    search_value = st.text_input("Enter value to search for", "")

    if search_value:
        result, error = execute_dynamic_query(conn, table_name, selected_column, search_value)
        if error:
            st.error(error)
        else:
            st.write(result)
else:
    st.error("Could not connect to the database.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat handling and user prompt interaction
if prompt := st.chat_input(f"Enter your prompt "):
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
            system_message = {"role": "system", "content": "You are a helpful assistant that can help with database queries."}
            conversation = [{"role": "user", "content": prompt}]
            conversation.extend(st.session_state.messages)  # Add the entire conversation history

            # Request response from OpenAI's API
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=conversation,
                max_tokens=MAX_TOKENS
            )

            full_response = response.choices[0].message.content

            # Check if the response contains a database query instruction
            if "query:" in full_response:
                try:
                    # Extract the query details (e.g., table and column) from the response
                    query_details = full_response.split("query:")[1].strip()

                    # Ensure we split into 3 components: table_name, column_name, and search_value
                    query_parts = query_details.split("|")
                    if len(query_parts) == 3:
                        table_name, column_name, search_value = [part.strip() for part in query_parts]

                        # Execute the dynamic query
                        result, error = execute_dynamic_query(conn, table_name, column_name, search_value)
                        if error:
                            full_response = f"Error: {error}"
                        else:
                            full_response = f"Query results:\n{result}"
                    else:
                        full_response = "Error: Invalid query format returned by the model."

                except Exception as e:
                    full_response = f"Error: {str(e)}"

            # Display the response
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            message_placeholder.markdown(f"Error: {str(e)}")

# Save the updated chat history to the file
save_chat_history(st.session_state.messages)
