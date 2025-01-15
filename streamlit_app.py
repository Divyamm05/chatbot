import openai
import streamlit as st
import toml
import re
from utils import load_chat_history, save_chat_history
from visualizations import generate_pie_chart, generate_bar_chart
from file_handlers import handle_uploaded_file
from database import connect_to_db, execute_dynamic_query
import os

# Load API key from Streamlit's secrets
openai.api_key = st.secrets["openai"]["api_key"]
db_path = "/home/vr-dt-100/Desktop/my_database.db"

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

# Handle file uploads and visualization tasks
data, columns = handle_uploaded_file(uploaded_file)
x_column, y_column, pie_column = None, None, None

if len(columns) > 0:
    if chart_type == "Bar Chart":
        x_column_index = st.selectbox("Select X-axis column", options=columns)
        y_column_index = st.selectbox("Select Y-axis column", options=columns)

        x_column = data[x_column_index] if x_column_index else None
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

# Connect to the database
conn = connect_to_db(db_path)

if not conn:
    st.error("Could not connect to the database. Please check the database path and ensure the file exists.")

# Handle user prompt for database queries
def handle_user_prompt(prompt, conn):
    pattern = r"fetch (.*?) from (.*?) where (.*?) is (.*?)"
    match = re.search(pattern, prompt, re.IGNORECASE)

    if match:
        column_name, table_name, condition_column, condition_value = match.groups()

        result, error = execute_dynamic_query(
            conn, table_name.strip(), column_name.strip(), condition_value.strip(), exact_match=True
        )

        if error:
            return f"Error: {error}"
        return result or f"No results found for '{condition_value}' in '{table_name}'."
    else:
        return "I couldn't understand your request. Please try using 'fetch <column> from <table> where <column> is <value>'."

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input for prompt
if prompt := st.chat_input("Enter prompt"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with message_placeholder:
            st.markdown("**Generating response...**")

        try:
            if conn:
                db_response = handle_user_prompt(prompt, conn)
                message_placeholder.markdown(db_response)
            else:
                message_placeholder.markdown("Database connection is unavailable.")

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            message_placeholder.markdown(f"Error: {str(e)}")

# Save updated chat history
save_chat_history(st.session_state.messages)
