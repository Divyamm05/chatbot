import pandas as pd
import streamlit as st
import openai
import sqlite3
from utils import load_chat_history, save_chat_history
from visualizations import generate_pie_chart, generate_bar_chart  # Import visualization functions
from file_handlers import handle_uploaded_file
from database import connect_to_db, execute_sql_query, fetch_columns, fetch_data_by_user_id  # Import necessary database functions

# Load API key from Streamlit's secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Set model parameters
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 2500

# File to store chat history
CHAT_HISTORY_FILE = 'chat_history.json'

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
        generate_bar_chart(data, x_column.name, y_column.name, start_value, end_value)

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
if prompt := st.chat_input(f"Enter SQL query or a message: "):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with message_placeholder:
            st.markdown("**Processing your query...**")
            st.spinner("Thinking...")

        try:
            # Connect to the database
            conn = connect_to_db()  # Connect to the database

            # Check if the prompt is a raw SQL query
            if "select" in prompt.lower() or "insert" in prompt.lower() or "update" in prompt.lower() or "delete" in prompt.lower():
                # Execute the query dynamically
                result = execute_sql_query(conn, prompt)
                
                if result is not None:
                    message_placeholder.markdown(f"Query result: {result}")
                else:
                    message_placeholder.markdown(f"Query executed successfully but no result to show.")
            
            # If the query requests column information from a table
            elif "columns of" in prompt.lower():
                table_name = prompt.split("columns of")[-1].strip()
                columns = fetch_columns(conn, table_name)
                message_placeholder.markdown(f"Columns of {table_name}: {columns}")
            
            # If the query requests user data by user ID
            elif "user_id =" in prompt.lower():
                user_id = int(prompt.split("user_id =")[-1].strip())
                user_data = fetch_data_by_user_id(conn, user_id)
                if user_data:
                    message_placeholder.markdown(f"User Data for ID {user_id}: {user_data}")
                else:
                    message_placeholder.markdown(f"No user found with ID {user_id}.")
            
            else:
                # If it's not a SQL query, use OpenAI API for regular queries
                conversation = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
                response = openai.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=conversation,
                    max_tokens=MAX_TOKENS
                )
                full_response = response.choices[0].message.content
                message_placeholder.markdown(full_response)

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            message_placeholder.markdown(f"Error: {str(e)}")

# Save the updated chat history to the file
save_chat_history(st.session_state.messages)
