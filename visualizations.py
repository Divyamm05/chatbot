import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def preview_uploaded_file(data, num_rows=5):
    """
    Display the first few rows of the uploaded data to give the user a preview.
    
    Args:
        data (pd.DataFrame): The uploaded dataset to preview.
        num_rows (int): The number of rows to preview.
    """
    st.write("Dataset preview:")
    st.dataframe(data.head(num_rows))

def generate_pie_chart(data, column_name, start_value, end_value):
    """
    Generate a pie chart based on a selected column from the dataset.
    Only the data in the range [start_value, end_value] will be visualized.

    Args:
        data (pd.DataFrame): The dataset.
        column_name (str): The column name for the pie chart.
        start_value (int): The starting index for the data range.
        end_value (int): The ending index for the data range.
    """
    selected_data = data[column_name].iloc[start_value:end_value]
    value_counts = selected_data.value_counts()

    fig, ax = plt.subplots()
    ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    st.pyplot(fig)

def generate_bar_chart(data, x_column, y_column, value_range):
    """
    Generate a bar chart based on selected columns with a single range selection.

    Args:
        data (pd.DataFrame): The dataset.
        x_column (str): The column for the X-axis.
        y_column (str): The column for the Y-axis.
        value_range (tuple): The range of indices for the data selection.
    """
    if not isinstance(data, pd.DataFrame):
        st.error("The uploaded file is not a valid DataFrame.")
        return

    if x_column not in data.columns or y_column not in data.columns:
        st.error(f"Columns {x_column} and {y_column} not found in the dataset.")
        return

    selected_data_x = data[x_column].iloc[value_range[0]:value_range[1]]
    selected_data_y = data[y_column].iloc[value_range[0]:value_range[1]]

    fig, ax = plt.subplots()
    ax.bar(selected_data_x, selected_data_y)
    plt.xticks(rotation=45, ha='right')
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_title(f"Bar Chart: {y_column} vs {x_column}")
    st.pyplot(fig)

def bar_chart_ui(data):
    """
    Streamlit UI for selecting columns and generating a bar chart.
    """
    if data is not None:
        x_column = st.selectbox("Select X-axis column", data.columns)
        y_column = st.selectbox("Select Y-axis column", data.columns)
        max_range = len(data)

        value_range = st.slider(
            "Select range for bar chart",
            0, max_range, (0, min(10, max_range))
        )

        generate_bar_chart(data, x_column, y_column, value_range)

def handle_uploaded_file(uploaded_file):
    """
    Handles the file upload and loads the appropriate dataset.

    Args:
        uploaded_file: The file uploaded by the user.
    Returns:
        data: The dataset loaded as a pandas DataFrame.
        columns: The column names from the dataset.
    """
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == "csv":
            data = pd.read_csv(uploaded_file)
        elif file_extension in ["xls", "xlsx"]:
            data = pd.read_excel(uploaded_file)
        elif file_extension == "json":
            data = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format")
            return None, None
        
        preview_uploaded_file(data)
        return data, data.columns.tolist()
    else:
        st.error("Please upload a file first.")
        return None, None


