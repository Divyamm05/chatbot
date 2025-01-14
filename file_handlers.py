import pandas as pd
import PyPDF2
import docx
from PIL import Image
import io

def handle_uploaded_file(uploaded_file):
    data = None
    columns = []

    if uploaded_file is not None:
        # Check if the uploaded file has content
        if uploaded_file.size == 0:
            raise ValueError("Uploaded file is empty. Please upload a valid file.")

        # Handle CSV file content
        if uploaded_file.type == "text/csv":
            try:
                df = pd.read_csv(uploaded_file)
                if df.empty:
                    raise ValueError("CSV file is empty. Please upload a valid CSV file.")
                data = df
                columns = df.columns.tolist()
            except pd.errors.EmptyDataError:
                raise ValueError("CSV file is empty. Please upload a valid CSV file.")
            except Exception as e:
                raise ValueError(f"Error reading CSV file: {str(e)}")

        # Handle Excel file content
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            try:
                df = pd.read_excel(uploaded_file)
                if df.empty:
                    raise ValueError("Excel file is empty. Please upload a valid Excel file.")
                data = df
                columns = df.columns.tolist()
            except Exception as e:
                raise ValueError(f"Error reading Excel file: {str(e)}")

        # Handle TXT file content
        elif uploaded_file.type == "text/plain":
            try:
                text_content = uploaded_file.getvalue().decode("utf-8")
                data = pd.Series([text_content])  # Convert text to pandas Series
            except Exception as e:
                raise ValueError(f"Error reading TXT file: {str(e)}")

        # Handle PDF file content
        elif uploaded_file.type == "application/pdf":
            try:
                pdf_file = PyPDF2.PdfReader(uploaded_file)
                pdf_text = ""
                for page in pdf_file.pages:
                    pdf_text += page.extract_text()
                data = pd.Series([pdf_text])  # Convert text to pandas Series
            except Exception as e:
                raise ValueError(f"Error reading PDF file: {str(e)}")

        # Handle DOCX file content
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                docx_file = io.BytesIO(uploaded_file.getvalue())
                doc = docx.Document(docx_file)
                doc_text = ""
                for para in doc.paragraphs:
                    doc_text += para.text + "\n"
                data = pd.Series([doc_text])  # Convert text to pandas Series
            except Exception as e:
                raise ValueError(f"Error reading DOCX file: {str(e)}")

        # Handle image files
        elif uploaded_file.type in ["image/jpeg", "image/png"]:
            try:
                img = Image.open(uploaded_file)
                img = img.convert('L')  # Convert image to grayscale
                df = pd.DataFrame(img.getdata(), columns=['pixel'])
                data = df.iloc[:, 0]  # Extract pixel data (one column)
            except Exception as e:
                raise ValueError(f"Error processing image file: {str(e)}")

        else:
            raise ValueError("Unsupported file type")

    return data, columns
