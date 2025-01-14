import pandas as pd
import PyPDF2
import docx
from PIL import Image
import io
from pdf2image import convert_from_path

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

        # Handle PDF file content (text extraction)
        elif uploaded_file.type == "application/pdf":
            pdf_file = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_file.pages:
                pdf_text += page.extract_text()
            data = pdf_text  # Directly return the extracted text

            # Extract images from PDF using pdf2image
            images = convert_from_path(uploaded_file)
            img_files = []
            for idx, img in enumerate(images):
                # Save each image (optional, you can also process them here)
                img_path = f"page_{idx + 1}.jpg"
                img.save(img_path, 'JPEG')
                img_files.append(img_path)
            # Optionally, return the list of image paths or handle the images
            data = {"text": pdf_text, "images": img_files}

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
