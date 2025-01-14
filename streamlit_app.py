import pandas as pd
import streamlit as st
import openai
from utils import load_chat_history, save_chat_history
from visualizations import generate_pie_chart, generate_bar_chart, preview_uploaded_file
from file_handlers import handle_uploaded_file

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
    st.title('🤖💬 CHATBOT')
    
    # Start new chat button
    with col1:
        if st.button('Start New Chat'):
            st.session_state.messages = []  
            save_chat_history(st.session_state.messages)  
            st.rerun()

    # Chart type dropdown
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
data, columns = handle_uploaded_file(uploaded_file)

# Initialize data selections
x_column = None
y_column = None
pie_column = None

# Visualization selections
if len(columns) > 0:
    if chart_type == "Bar Chart":
        x_column_index = st.selectbox("Select X-axis column", options=columns)
        x_column = data[x_column_index] if x_column_index else None

        y_column_index = st.selectbox("Select Y-axis column", options=columns)
        y_column = data[y_column_index] if y_column_index else None

    elif chart_type == "Pie Chart":
        pie_column_index = st.selectbox("Select column for Pie Chart", options=columns)
        pie_column = data[pie_column_index] if pie_column_index else None

# Bar chart range slider and generation
if chart_type == "Bar Chart" and x_column is not None and y_column is not None:
    start_value, end_value = st.slider(
        "Select range of data to visualize",
        min_value=0,
        max_value=len(x_column),
        value=(0, min(10, len(x_column))),
        step=1,
        help="Select the start and end range for the data"
    )

    if st.button("Generate Bar Chart"):
        generate_bar_chart(data, x_column.name, y_column.name, start_value, end_value)

# Pie chart generation
if chart_type == "Pie Chart" and pie_column is not None:
    start_value, end_value = st.slider(
        "Select range of data for Pie Chart",
        min_value=0,
        max_value=len(data),
        value=(0, min(10, len(data))),
        step=1,
        help="Select the range of data for the Pie Chart"
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
            system_message = {"role": "system", "content": "You are a helpful assistant."}
            conversation = [system_message, {"role": "user", "content": prompt}]
            if uploaded_file:
                conversation.append({"role": "user", "content": prompt + "\n\n" + str(data)})
            conversation.extend(st.session_state.messages)

            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=conversation,
                max_tokens=MAX_TOKENS
            )

            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            message_placeholder.markdown(f"Error: {str(e)}")

# Save updated chat history
save_chat_history(st.session_state.messages)
