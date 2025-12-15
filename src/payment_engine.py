import pandas as pd
from pathlib import Path

def run_payment(ocr_file: Path, out_file: Path):
    df = pd.read_excel(ocr_file)

    df["signature_present"] = df["text"].str.contains("signature|signed", case=False)
    df["amount"] = 1000
    df["payable"] = df["signature_present"]

    df[["file", "signature_present", "amount", "payable"]].to_excel(out_file, index=False)
