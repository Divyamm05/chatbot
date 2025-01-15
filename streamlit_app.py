import openai
import streamlit as st
from utils import load_chat_history, save_chat_history
from visualizations import generate_pie_chart, generate_bar_chart
from file_handlers import handle_uploaded_file
from database import connect_to_db, execute_dynamic_query

# Load API key from Streamlit's secrets
openai.api_key = st.secrets["openai"]["api_key"]
db_path = "/home/vr-dt-100/Desktop/database2.db"

# Set model parameters
OPENAI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 2500

# File to store chat history
CHAT_HISTORY_FILE = 'chat_history.json'

# Load previous chat history if available
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar: Chart selection and file upload
st.sidebar.title('🤖💬 CHATBOT')

# Button to clear chat history and refresh interface
if st.sidebar.button('Start New Chat'):
    st.session_state.messages = []
    save_chat_history(st.session_state.messages)
    st.experimental_rerun()

# Chart selection dropdown and file uploader
chart_type = st.sidebar.selectbox(
    "Select a chart type for visualization",
    ("Select a chart", "Pie Chart", "Bar Chart")
)
uploaded_file = st.sidebar.file_uploader(
    "Upload an attachment (optional)",
    type=["txt", "csv", "xlsx", "pdf", "jpg", "png", "docx"]
)

# Handle file uploads and visualization tasks
data, columns = handle_uploaded_file(uploaded_file)
x_column, y_column, pie_column = None, None, None

# Visualization selections based on chart type
if len(columns) > 0:
    if chart_type == "Bar Chart":
        x_column = st.selectbox("Select X-axis column", columns)
        y_column = st.selectbox("Select Y-axis column", columns)
        if x_column and y_column:
            start_value, end_value = st.slider(
                "Select range for visualization",
                min_value=0, max_value=len(data),
                value=(0, min(10, len(data))),
                step=1
            )
            if st.button("Generate Bar Chart"):
                generate_bar_chart(data, x_column, y_column, start_value, end_value)

    elif chart_type == "Pie Chart":
        pie_column = st.selectbox("Select column for Pie Chart", columns)
        if pie_column:
            start_value, end_value = st.slider(
                "Select data range for Pie Chart",
                min_value=0, max_value=len(data),
                value=(0, min(10, len(data))),
                step=1
            )
            if st.button("Generate Pie Chart"):
                generate_pie_chart(data, pie_column, start_value, end_value)

# Database interaction: Connect and execute queries
if db_path:
    conn = connect_to_db(db_path)
    if conn:
        table_name = 'your_table'  # Example table name
        column_name = 'your_column'  # Example column name
        search_value = 'search_term'  # Example search value
        result, error = execute_dynamic_query(conn, table_name, column_name, search_value)
        if error:
            st.error(f"Database Error: {error}")
        else:
            st.write(f"Database Result: {result}")
    else:
        st.error("Could not connect to the database. Please check the database path.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Enter prompt"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("**Generating response...**")

        try:
            # Construct the conversation history for OpenAI request
            conversation = [{"role": "system", "content": "You are a helpful assistant."}]
            conversation.extend(st.session_state.messages)

            # Request completion from OpenAI API
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=conversation,
                max_tokens=MAX_TOKENS
            )

            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_message = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            message_placeholder.markdown(error_message)

# Save updated chat history
save_chat_history(st.session_state.messages)
