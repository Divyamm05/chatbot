# Move the preview_uploaded_file function definition here
def preview_uploaded_file(uploaded_file):
    """Preview the content of the uploaded file based on its type."""
    if uploaded_file.type == "text/csv":
        # Display the preview of CSV file
        df = pd.read_csv(uploaded_file)
        st.write("CSV File Content:")
        st.dataframe(df.head())  # Show first 5 rows of CSV
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        # Display the preview of Excel file
        df = pd.read_excel(uploaded_file)
        st.write("Excel File Content:")
        st.dataframe(df.head())  # Show first 5 rows of Excel
    elif uploaded_file.type == "text/plain":
        # Display the preview of TXT file
        text_content = uploaded_file.getvalue().decode("utf-8")
        st.write("Text File Content:")
        st.text(text_content)  # Display the text
    elif uploaded_file.type == "application/pdf":
        # Display the preview of PDF file
        pdf_reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        st.write("PDF File Content:")
        st.text(pdf_text)  # Display the PDF content
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # Display the preview of DOCX file
        docx_file = io.BytesIO(uploaded_file.getvalue())
        doc = docx.Document(docx_file)
        doc_text = ""
        for para in doc.paragraphs:
            doc_text += para.text + "\n"
        st.write("DOCX File Content:")
        st.text(doc_text)  # Display DOCX content
    elif uploaded_file.type in ["image/jpeg", "image/png"]:
        # Display the preview of image file
        img = Image.open(uploaded_file)
        st.image(img, caption='Uploaded Image', use_column_width=True)
    else:
        st.warning("Unsupported file type. Please upload a TXT, CSV, DOCX, PDF, or image file.")

# Now you can use the preview_uploaded_file function as intended
import openai
import streamlit as st
import json
import os
from utils import load_chat_history, save_chat_history, generate_chart_description
from visualizations import generate_pie_chart
from file_handlers import handle_uploaded_file
import pandas as pd
import io
from PyPDF2 import PdfReader
import docx
from PIL import Image

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

    if uploaded_file is not None:
        st.write("Uploaded file:", uploaded_file.name)
        # Call the preview function to display content of uploaded file
        preview_uploaded_file(uploaded_file)  

# Handle file uploads and visualization-related tasks
data, columns = handle_uploaded_file(uploaded_file)

# Initialize data to None by default
data_column = None
if len(columns) > 0 and chart_type in ["Pie Chart", "Bar Chart"]:
    selected_column = st.slider(
        "Select a column to visualize",
        min_value=1,
        max_value=len(columns),
        value=1,
        step=1,
        format="%s"
    )
    column_name = columns[selected_column - 1]
    data_column = data[column_name]

# Conditionally display the slider for the number of values to visualize
if chart_type in ["Pie Chart", "Bar Chart"] and data_column is not None:
    start_value, end_value = st.slider(
        "Select range of values to visualize",
        min_value=1, 
        max_value=len(data_column),  # Set max value to the length of the data
        value=(1, min(10, len(data_column))),  # Default range (start from 1 to 10 or data length)
        step=1,
        help="Select the start and end values to visualize the chart"
    )

# Add a button to directly generate Pie Chart
if chart_type == "Pie Chart" and data_column is not None:
    if st.button("Generate Pie Chart"):
        generate_pie_chart(data_column, start_value, end_value)

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
            # Construct the conversation history as a list of messages
            system_message = {"role": "system", "content": "You are a helpful assistant."}
            conversation = [system_message, {"role": "user", "content": prompt}]

            # If an Excel, CSV, or any other file is uploaded, include it in the conversation
            if uploaded_file:
                conversation.append({"role": "user", "content": prompt + "\n\n" + str(data)})

            conversation.extend(st.session_state.messages)  # Add the entire conversation history

            # Request response from OpenAI's API using `openai.ChatCompletion.create()`
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
