import pandas as pd
import PyPDF2
import docx
from PIL import Image
import io

def handle_uploaded_file(uploaded_file):
    data = None
    columns = []

    if uploaded_file is not None:
        # Handle CSV file content
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            data = df
            columns = df.columns.tolist()

        # Handle Excel file content
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file)
            data = df
            columns = df.columns.tolist()

        # Handle TXT file content
        elif uploaded_file.type == "text/plain":
            text_content = uploaded_file.getvalue().decode("utf-8")
            data = text_content  # Directly return the text content

        # Handle PDF file content
        elif uploaded_file.type == "application/pdf":
            pdf_file = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_file.pages:
                pdf_text += page.extract_text()
            data = pdf_text  # Directly return the extracted text

        # Handle DOCX file content
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            docx_file = io.BytesIO(uploaded_file.getvalue())
            doc = docx.Document(docx_file)
            doc_text = ""
            for para in doc.paragraphs:
                doc_text += para.text + "\n"
            data = doc_text  # Directly return the extracted text

        # Handle image files
        elif uploaded_file.type in ["image/jpeg", "image/png"]:
            img = Image.open(uploaded_file)
            img = img.convert('L')
            df = pd.DataFrame(img.getdata(), columns=['pixel'])
            data = df.iloc[:, 0]  # Just return pixel data if necessary, or analyze image as needed

        else:
            raise ValueError("Unsupported file type")

    return data, columns
