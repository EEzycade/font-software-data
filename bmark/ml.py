import cv2
import pytesseract
import os
import shutil

pytesseract.pytesseract.tesseract_cmd = os.environ.get("PYTESSERACT", pytesseract.pytesseract.tesseract_cmd)

def image_to_text(image_path):
    if shutil.which(pytesseract.pytesseract.tesseract_cmd) is None:
        raise Exception(f"Download Tesseract from 'https://tesseract-ocr.github.io/tessdoc/Home.html' and set the 'PYTESSERACT' environment variable to its path.")
    # Grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Morph open to remove noise and invert image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    invert = 255 - opening

    # Perform text extraction
    data = pytesseract.image_to_string(invert, lang='eng', config='--psm 6')
    return data

