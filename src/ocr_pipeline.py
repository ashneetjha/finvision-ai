import cv2
import pandas as pd
import pytesseract
from pathlib import Path
from config import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


records = []

for img_path in RAW_DIR.glob("*"):
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        continue

    _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh)

    for line in text.split("\n"):
        if line.strip():
            records.append({
                "file": img_path.name,
                "text": line.strip()
            })

df = pd.DataFrame(records)

out_file = OUTPUT_DIR / "ocr_output.xlsx"
df.to_excel(out_file, index=False)

print(f"✅ OCR saved to {out_file}")
