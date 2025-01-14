import openai
import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import PyPDF2
import docx
import io
from PIL import Image
from io import BytesIO

# Load API key from Streamlit's secrets
openai.api_key = st.secrets["openai"]["api_key"]

# Set model parameters
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 500

# File to store chat history
CHAT_HISTORY_FILE = 'chat_history.json'

# Function to load chat history from the file
def load_chat_history():
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r') as file:
                return json.load(file)  # Load the JSON file content
        return []  # Return an empty list if the file doesn't exist
    except json.JSONDecodeError as e:
        st.error(f"Error loading chat history: {e}. The file might be corrupted.")
        return []  # Return an empty list if the file is corrupted

# Function to save chat history to the file
def save_chat_history(messages):
    with open(CHAT_HISTORY_FILE, 'w') as file:
        json.dump(messages, file)

# Function to generate a textual description of the chart
def generate_chart_description(chart_type, data):
    if isinstance(data, pd.Series):
        values = data.tolist()
        categories = data.index.tolist()
    else:
        categories = list(data.columns)
        values = data.iloc[0].tolist()  # Assumes the first row of the DataFrame contains the values

    if chart_type == "pie":
        total = sum(values)
        percentages = [f"{value:.1f}% ({value}/{total})" for value in values]
        description = f"Pie Chart: {', '.join([f'{category}: {percentage}' for category, percentage in zip(categories, percentages)])}"
    elif chart_type == "bar":
        description = f"Bar Chart: Values for categories: {', '.join([f'{category}: {value}' for category, value in zip(categories, values)])}"
    else:
        description = "Chart type not supported."

    return description

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

# Initialize data to None by default
data = None
columns = []

if uploaded_file is not None:
    st.write("Uploaded file:", uploaded_file.name)

    # Handle CSV file content
    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
        st.write("CSV File Content:")
        st.dataframe(df.head())
        data = df
        columns = df.columns.tolist()

    # Handle Excel file content
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(uploaded_file)
        st.write("Excel File Content:")
        st.dataframe(df.head())
        data = df
        columns = df.columns.tolist()

    # Handle TXT file content
    elif uploaded_file.type == "text/plain":
        text_content = uploaded_file.getvalue().decode("utf-8")
        st.write("Text File Content:")
        st.text(text_content)
        data = pd.Series([text_content])  # Convert text to pandas Series

    # Handle PDF file content
    elif uploaded_file.type == "application/pdf":
        pdf_file = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_file.pages:
            pdf_text += page.extract_text()
        st.write("PDF File Content:")
        st.text(pdf_text)
        data = pd.Series([pdf_text])  # Convert text to pandas Series

    # Handle DOCX file content
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        docx_file = io.BytesIO(uploaded_file.getvalue())
        doc = docx.Document(docx_file)
        doc_text = ""
        for para in doc.paragraphs:
            doc_text += para.text + "\n"
        st.write("DOCX File Content:")
        st.text(doc_text)
        data = pd.Series([doc_text])  # Convert text to pandas Series

    # Handle image files
    elif uploaded_file.type in ["image/jpeg", "image/png"]:
        img = Image.open(uploaded_file)
        img = img.convert('L')
        df = pd.DataFrame(img.getdata(), columns=['pixel'])
        data = df.iloc[:, 0]

    else:
        st.warning("Unsupported file type. Please upload a TXT, PDF, DOCX, or image file.")

# Add a slider for selecting the column to visualize
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
else:
    column_name = None
    data_column = None

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
else:
    start_value, end_value = 1, 1  # Default values when no data is available

# Add a button to directly generate Pie Chart
if chart_type == "Pie Chart" and data_column is not None:
    if st.button("Generate Pie Chart"):
        # Slice the data based on the selected range
        selected_data = data_column.iloc[start_value-1:end_value]  # Adjusting to 0-based index
        
        # Count the occurrences of each category (e.g., country) in the sliced data
        category_counts = selected_data.value_counts()
        
        # Generate the pie chart based on category counts
        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%')
        ax.legend(wedges, category_counts.index,
                  title="Categories",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        st.pyplot(fig)

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

            # Request response from OpenAI's API using `openai.Completion.create()` or `openai.ChatCompletion.create()`
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=MAX_TOKENS
            )

            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            message_placeholder.markdown(f"Error: {str(e)}")

# Save the updated chat history to the file
save_chat_history(st.session_state.messages)
