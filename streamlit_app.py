import pandas as pd
import streamlit as st
import openai
import json
import sqlite3
from utils import load_chat_history, save_chat_history
from visualizations import generate_pie_chart, generate_bar_chart, preview_uploaded_file
from file_handlers import handle_uploaded_file
from database import connect_to_db, fetch_users, fetch_user_by_id, fetch_users_by_gender, fetch_active_users

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
    col1, col2 = st.columns([3, 1])

    st.title('🤖💬 CHATBOT')

    with col1:
        if st.button('Start New Chat'):
            st.session_state.messages = []
            save_chat_history(st.session_state.messages)
            st.rerun()

    chart_type = st.selectbox(
        "Select a chart type for visualization",
        ("Select a chart", "Pie Chart", "Bar Chart")
    )

    uploaded_file = st.file_uploader("Upload an attachment (optional)", type=["txt", "csv", "xlsx", "pdf", "jpg", "png", "docx"])

# Handle file uploads and visualization-related tasks
data, columns = handle_uploaded_file(uploaded_file)

# Database connection
DB_PATH = "/home/vr-dt-100/Desktop/database.db"
conn = connect_to_db(DB_PATH)

user_dict = {}
if conn:
    users = fetch_users(conn)
    user_dict = {user[0]: {"username": user[1], "first_name": user[2], "last_name": user[3]} for user in users}
    conn.close()

# Initialize data to None by default
x_column = None
y_column = None
pie_column = None

if len(columns) > 0:
    if chart_type == "Bar Chart":
        x_column_index = st.selectbox("Select X-axis column", options=columns)
        x_column = data[x_column_index] if x_column_index else None

        y_column_index = st.selectbox("Select Y-axis column", options=columns)
        y_column = data[y_column_index] if y_column_index else None

    elif chart_type == "Pie Chart":
        pie_column_index = st.selectbox("Select column for Pie Chart", options=columns)
        pie_column = data[pie_column_index] if pie_column_index else None

if chart_type == "Bar Chart" and x_column is not None and y_column is not None:
    start_value, end_value = st.slider(
        "Select range of values to visualize",
        min_value=0,
        max_value=len(x_column),
        value=(0, min(10, len(x_column))),
        step=1
    )

    if st.button("Generate Bar Chart"):
        generate_bar_chart(data, x_column.name, y_column.name, start_value, end_value)

if chart_type == "Pie Chart" and pie_column is not None:
    start_value, end_value = st.slider(
        "Select range of data for Pie Chart",
        min_value=0,
        max_value=len(data),
        value=(0, min(10, len(data))),
        step=1
    )

    if st.button("Generate Pie Chart"):
        if pie_column is not None and not pie_column.empty:
            generate_pie_chart(data, pie_column.name, start_value, end_value)
        else:
            st.error("Please select a valid column for the Pie Chart")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to handle database queries

def handle_database_queries(prompt, conn):
    prompt = prompt.lower()

    if "list all users" in prompt:
        users = fetch_users(conn)
        if users:
            st.write("### User List")
            for user in users:
                st.write(f"User ID: {user[0]}, Username: {user[1]}, Name: {user[2]} {user[3]}")
        else:
            st.write("No users found.")

    elif "details of user" in prompt:
        user_id = prompt.split()[-1]
        user = fetch_user_by_id(conn, user_id)
        if user:
            st.write(f"User ID: {user[0]}, Username: {user[1]}, Name: {user[2]} {user[3]}")
        else:
            st.write(f"User with ID {user_id} not found.")

    elif "active users" in prompt:
        active_users = fetch_active_users(conn)
        if active_users:
            st.write("### Active Users")
            for user in active_users:
                st.write(f"User ID: {user[0]}, Name: {user[2]} {user[3]}")
        else:
            st.write("No active users found.")

    else:
        st.write("I'm sorry, I didn't understand that query.")

# User input for the prompt
if prompt := st.chat_input("Enter prompt"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("**Generating response...**")

        try:
            conn = connect_to_db(DB_PATH)
            if conn:
                handle_database_queries(prompt, conn)
                conn.close()
            else:
                st.error("Database connection failed.")

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            message_placeholder.markdown(f"Error: {str(e)}")

# Save the updated chat history
save_chat_history(st.session_state.messages)
