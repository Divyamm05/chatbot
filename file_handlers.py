import pandas as pd
import PyPDF2
import docx
from PIL import Image
import io
from pdf2image import convert_from_path
import fitz  # PyMuPDF

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

        # Handle PDF file content (text extraction with PyPDF2)
        elif uploaded_file.type == "application/pdf":
            pdf_file = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_file.pages:
                pdf_text += page.extract_text()
            data = {"text": pdf_text}  # Store text in a dictionary

            # Extract images from PDF pages using pdf2image
            images = convert_from_path(uploaded_file)
            img_files = []
            for idx, img in enumerate(images):
                # Save each image (optional, you can also process them here)
                img_path = f"page_{idx + 1}.jpg"
                img.save(img_path, 'JPEG')
                img_files.append(img_path)
            data["page_images"] = img_files  # Store the page images in the dictionary

            # Optionally, extract embedded images from PDF using PyMuPDF
            embedded_images = extract_images_from_pdf(uploaded_file)
            data["embedded_images"] = embedded_images  # Store embedded images

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


def extract_images_from_pdf(pdf_file):
    """Extract embedded images from a PDF using PyMuPDF."""
    doc = fitz.open(pdf_file)
    image_list = []
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        img_list = page.get_images(full=True)
        
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]  # This is a byte stream of the image
            image_list.append(image_data)  # You can process or save this image
            
    return image_list
