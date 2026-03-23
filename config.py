import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
EXPORT_DIR = os.path.join(BASE_DIR, "data", "exports")
DB_PATH = os.path.join(BASE_DIR, "database.db")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# For Windows, uncomment if needed
# TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_CMD = None