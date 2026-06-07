import os

import pytesseract

from PIL import Image
from pdf2image import convert_from_path
from docx import Document as DocxDocument



# ocr for image
def extract_text_from_image(file_path: str):

    image = Image.open(file_path)

    return pytesseract.image_to_string(image)


# ocr for pdf
def extract_text_from_pdf(file_path: str):

    pages = convert_from_path(file_path)

    text = ""

    for page in pages:

        page_text = pytesseract.image_to_string(page)

        text += page_text + "\n"

    return text


# DOCX

def extract_text_from_docx(file_path: str):

    doc = DocxDocument(file_path)

    text = ""

    for paragraph in doc.paragraphs:

        text += paragraph.text + "\n"

    return text



# TXT 

def extract_text_from_txt(file_path: str):

    with open(file_path, "r", encoding="utf-8") as f:

        return f.read()



def extract_text(file_path: str):

    extension = os.path.splitext(file_path)[1].lower()

    if extension in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(file_path)

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )