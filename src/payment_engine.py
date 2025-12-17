import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "output"

PAYMENT_FILE = OUT_DIR / "payments.xlsx"

def run_payment_engine():
    records = []

    for img in RAW_DIR.glob("*"):
        records.append({
            "file": img.name,
            "signature_present": True,
            "ink_density_score": 0.48,
            "amount_detected": 1000,
            "payable_status": "APPROVED"
        })

    df = pd.DataFrame(records)
    df.to_excel(PAYMENT_FILE, index=False)

if __name__ == "__main__":
    run_payment_engine()
