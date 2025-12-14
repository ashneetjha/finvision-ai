from pathlib import Path

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
