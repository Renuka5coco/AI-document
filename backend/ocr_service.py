from pdf2image import convert_from_path
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\RENUKA\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def extract_text(file_path):
    text = ""

    try:
        if file_path.lower().endswith(".pdf"):
            images = convert_from_path(
                file_path,
                poppler_path=r"C:\Users\RENUKA\Desktop\Release-25.12.0-0\poppler-25.12.0\Library\bin"
            )
            for img in images:
                text += pytesseract.image_to_string(img)
        else:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)

        return text

    except Exception as e:
        return str(e)
