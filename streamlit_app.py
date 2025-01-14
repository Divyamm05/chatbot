import pandas as pd
import streamlit as st
import openai
import json
import os
from utils import load_chat_history, save_chat_history
from visualizations import generate_pie_chart, generate_bar_chart, preview_uploaded_file

# Load API key from Streamlit's secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Set model parameters
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 500

# File to store chat history
CHAT_HISTORY_FILE = 'chat_history.json'

# Load the previous chat history if available
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar for chart selection and file attachment
with st.sidebar:
    col1, col2 = st.columns([3, 1])

    # Sidebar: Add chatbot title
    st.title('🤖💬 CHATBOT')
    
    # "Start New Chat" button clears chat history
    with col1:
        if st.button('Start New Chat'):
            st.session_state.messages = []
            save_chat_history(st.session_state.messages)
            st.rerun()

    # Dropdown for chart selection
    chart_type = st.selectbox(
        "Select a chart type for visualization",
        ("Select a chart", "Pie Chart", "Bar Chart")
    )

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload an attachment (optional)",
        type=["txt", "csv", "xlsx", "pdf", "jpg", "png", "docx"]
    )

# Handle file uploads and visualization-related tasks
from file_handlers import handle_uploaded_file
data, columns = handle_uploaded_file(uploaded_file)

# Initialize variables
x_column = y_column = pie_column = None

if columns:
    if chart_type == "Bar Chart":
        x_column = st.selectbox("Select X-axis column", options=columns)
        y_column = st.selectbox("Select Y-axis column", options=columns)

    elif chart_type == "Pie Chart":
        pie_column = st.selectbox("Select column for Pie Chart", options=columns)

# Slider and chart generation logic
if chart_type == "Bar Chart" and x_column and y_column:
    start_value, end_value = st.slider(
        "Select data range for visualization",
        min_value=0,
        max_value=len(data),
        value=(0, min(10, len(data))),
        step=1
    )

    if st.button("Generate Bar Chart"):
        generate_bar_chart(data, x_column, y_column, start_value, end_value)

if chart_type == "Pie Chart" and pie_column:
    start_value, end_value = st.slider(
        "Select range of data for Pie Chart",
        min_value=0,
        max_value=len(data),
        value=(0, min(10, len(data))),
        step=1
    )

    if st.button("Generate Pie Chart"):
        generate_pie_chart(data, pie_column, start_value, end_value)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User prompt input
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
            # Prepare conversation for OpenAI API
            system_message = {"role": "system", "content": "You are a helpful assistant."}
            conversation = [system_message] + st.session_state.messages

            if uploaded_file:
                conversation.append({"role": "user", "content": str(data)})

            # OpenAI API call using correct interface
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=conversation,
                max_tokens=MAX_TOKENS
            )

            full_response = response["choices"][0]["message"]["content"]
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            message_placeholder.markdown(full_response)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            message_placeholder.markdown(error_message)

# Save updated chat history
save_chat_history(st.session_state.messages)
