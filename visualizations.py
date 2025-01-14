import pandas as pd
import matplotlib.pyplot as plt
import io
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
        column_name (str): The column name for the Pie Chart.
        start_value (int): The starting index for the data range.
        end_value (int): The ending index for the data range.
    """
    # Slice the data to get the selected range
    selected_data = data[column_name].iloc[start_value:end_value]
    
    # Generate value counts (for pie chart)
    value_counts = selected_data.value_counts()

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Display the pie chart in Streamlit
    st.pyplot(fig)

def generate_bar_chart(data, x_column, y_column, start_x_value, end_x_value, start_y_value, end_y_value):
    """
    Generate a bar chart based on selected columns and range of data for both axes.
    
    Args:
        data (pd.DataFrame): The dataset.
        x_column (str): The column for the X-axis.
        y_column (str): The column for the Y-axis.
        start_x_value (int): The starting index for the X-axis range.
        end_x_value (int): The ending index for the X-axis range.
        start_y_value (int): The starting index for the Y-axis range.
        end_y_value (int): The ending index for the Y-axis range.
    """
    if not isinstance(data, pd.DataFrame):
        st.error("The uploaded file is not a valid DataFrame.")
        return

    # Validate if the x_column and y_column are in the dataframe
    if x_column not in data.columns or y_column not in data.columns:
        st.error(f"Columns {x_column} and {y_column} not found in the dataset.")
        return

    # Slice the data to get the selected range for both X and Y axes
    selected_data_x = data[x_column].iloc[start_x_value:end_x_value]
    selected_data_y = data[y_column].iloc[start_y_value:end_y_value]

    # Check if the lengths match
    if len(selected_data_x) != len(selected_data_y):
        st.error("The selected ranges for X and Y axes don't match in length.")
        return

    # Create the bar chart
    fig, ax = plt.subplots()
    ax.bar(selected_data_x, selected_data_y)

    # Rotate the x-axis labels to prevent clutter
    plt.xticks(rotation=45, ha='right')

    # Set chart labels and title
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_title(f"Bar Chart: {y_column} vs {x_column}")

    # Display the bar chart in Streamlit
    st.pyplot(fig)

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
        # Read the file based on its type (CSV, Excel, etc.)
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
        
        # Display a preview of the dataset
        preview_uploaded_file(data)

        # Return the loaded dataset and its columns
        return data, data.columns.tolist()
    else:
        st.error("Please upload a file first.")
        return None, None
