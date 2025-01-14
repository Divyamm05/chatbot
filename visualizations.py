import pandas as pd
import matplotlib.pyplot as plt
import io
import streamlit as st

# Function to preview dataset after upload
def preview_uploaded_file(uploaded_file):
    # Handle CSV file content
    if uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
        st.write("CSV File Content:")
        st.dataframe(df.head())  # Preview the first 5 rows of the dataset

    # Handle Excel file content
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(uploaded_file)
        st.write("Excel File Content:")
        st.dataframe(df.head())  # Preview the first 5 rows of the dataset

    # Handle TXT file content
    elif uploaded_file.type == "text/plain":
        text_content = uploaded_file.getvalue().decode("utf-8")
        st.write("Text File Content:")
        st.text(text_content)  # Show the text content

    # Handle PDF file content
    elif uploaded_file.type == "application/pdf":
        import PyPDF2
        pdf_file = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_file.pages:
            pdf_text += page.extract_text()
        st.write("PDF File Content:")
        st.text(pdf_text)  # Show extracted text from PDF

    # Handle DOCX file content
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        import docx
        docx_file = io.BytesIO(uploaded_file.getvalue())
        doc = docx.Document(docx_file)
        doc_text = ""
        for para in doc.paragraphs:
            doc_text += para.text + "\n"
        st.write("DOCX File Content:")
        st.text(doc_text)  # Show the text content from DOCX

    # Handle image files (optional preview of images)
    elif uploaded_file.type in ["image/jpeg", "image/png"]:
        from PIL import Image
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)  # Preview image

    else:
        st.warning("Unsupported file type. Please upload a TXT, PDF, DOCX, or image file.")


def generate_pie_chart(data_column, start_value, end_value):
    """
    Generate a pie chart based on a selected column from the dataset.
    Only the data in the range [start_value, end_value] will be visualized.

    Args:
        data_column (pd.Series): The column to create the pie chart from.
        start_value (int): The starting index for the data range.
        end_value (int): The ending index for the data range.
    """
    # Slice the data to get the selected range
    selected_data = data_column[start_value-1:end_value]
    
    # Generate value counts (for pie chart)
    value_counts = selected_data.value_counts()

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Display the pie chart in Streamlit
    st.pyplot(fig)
