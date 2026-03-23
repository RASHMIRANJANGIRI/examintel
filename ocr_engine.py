import cv2
import numpy as np
from PIL import Image
import pytesseract
from config import TESSERACT_CMD

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def preprocess_image(pil_image):
    img = np.array(pil_image)

    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img

    gray = cv2.resize(gray, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    return thresh

def extract_text_from_image(pil_image):
    processed = preprocess_image(pil_image)
    text = pytesseract.image_to_string(processed, config="--oem 3 --psm 6")
    return text, processed