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
    st.title('🤖💬 Chatbot')

    # Sidebar: Start New Chat button
    if st.button('Start New Chat'):
        st.session_state.messages = []  # Clears the chat history
        save_chat_history(st.session_state.messages)  # Save the empty history
        st.rerun()  # Rerun the app to refresh the interface

    # Sidebar: Select chart type
    chart_type = st.selectbox(
        "Select a chart type for visualization",
        ("Select a chart", "Pie Chart", "Bar Chart")
    )

    # File uploader for attachments
    uploaded_file = st.file_uploader(
        "Upload an attachment (optional)",
        type=["txt", "csv", "xlsx", "pdf", "jpg", "png", "docx"]
    )

# Handle file uploads and visualization-related tasks
from file_handlers import handle_uploaded_file
data, columns = handle_uploaded_file(uploaded_file)

# Initialize data to None by default
x_column = None
y_column = None
pie_column = None

if len(columns) > 0:
    # Visualization options based on chart type
    if chart_type == "Bar Chart":
        x_column_name = st.selectbox("Select X-axis column", options=columns)
        y_column_name = st.selectbox("Select Y-axis column", options=columns)

        if x_column_name and y_column_name:
            # Bar chart range slider for selecting data range
            data_length = len(data)
            value_range = st.slider(
                "Select data range for Bar Chart",
                0, data_length, (0, min(10, data_length)),
                step=1, help="Select range of rows for bar chart visualization"
            )

            if st.button("Generate Bar Chart"):
                generate_bar_chart(data, x_column_name, y_column_name, value_range)

    elif chart_type == "Pie Chart":
        pie_column_name = st.selectbox("Select column for Pie Chart", options=columns)

        if pie_column_name:
            data_length = len(data)
            value_range = st.slider(
                "Select range of data for Pie Chart",
                0, data_length, (0, min(10, data_length)),
                step=1, help="Select data range for pie chart visualization"
            )

            if st.button("Generate Pie Chart"):
                generate_pie_chart(data, pie_column_name, value_range[0], value_range[1])

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input for the prompt
if prompt := st.chat_input("Enter prompt"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with message_placeholder:
            st.markdown("**Generating response...**")
            st.spinner("Thinking...")

        try:
            # Construct the conversation history
            system_message = {"role": "system", "content": "You are a helpful assistant."}
            conversation = [system_message, {"role": "user", "content": prompt}]
            
            if uploaded_file:
                conversation.append({"role": "user", "content": prompt + "\n\n" + str(data)})
            
            conversation.extend(st.session_state.messages)

            # Request response from OpenAI API
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=conversation,
                max_tokens=MAX_TOKENS
            )
            
            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            message_placeholder.markdown(error_message)

# Save updated chat history
save_chat_history(st.session_state.messages)
