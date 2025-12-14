from pathlib import Path
import cv2
import pandas as pd

INPUT_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/output/payments.xlsx")
OUTPUT_FILE.parent.mkdir(exist_ok=True)

records = []

for img_path in INPUT_DIR.glob("*"):
    img = cv2.imread(str(img_path), 0)

    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    ink_fraction = thresh.sum() / (255 * thresh.size)

    signature_present = ink_fraction > 0.02
    amount = 1000
    payable = signature_present

    records.append({
        "file": img_path.name,
        "signature_present": signature_present,
        "ink_fraction": round(ink_fraction, 4),
        "amount": amount,
        "payable": payable
    })

df = pd.DataFrame(records)
df.to_excel(OUTPUT_FILE, index=False)

print(f"Saved payment file: {OUTPUT_FILE}")
