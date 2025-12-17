from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pathlib import Path
import shutil
import pandas as pd
from datetime import datetime
import random

app = FastAPI(title="FinVision AI")

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "output"

OCR_FILE = OUT_DIR / "ocr.xlsx"
PAYMENT_FILE = OUT_DIR / "payments.xlsx"

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- DASHBOARD ----------------
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>FinVision AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .card {
            background: #1e293b;
            padding: 30px;
            border-radius: 14px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        }
        input, button {
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            border-radius: 8px;
            border: none;
        }
        button {
            background: #38bdf8;
            font-weight: bold;
            cursor: pointer;
        }
        a {
            display: block;
            margin-top: 14px;
            color: #22c55e;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>📊 FinVision AI</h2>
        <p>Agentic Document Digitization & Financial Validation</p>

        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload & Process</button>
        </form>

        <a href="/download/ocr">⬇ Download OCR Excel</a>
        <a href="/download/payments">⬇ Download Payments Excel</a>
    </div>
</body>
</html>
"""

# ---------------- UPLOAD ----------------
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    img_path = RAW_DIR / file.filename

    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    upload_time = datetime.utcnow()

    # -------- OCR SIMULATION --------
    sample_lines = [
        "Indian Oil Corporation Limited",
        "Invoice No: IOCL-2024-INV-001",
        "Total Amount Payable: ₹1000",
        "Authorized Signature"
    ]

    ocr_rows = []
    for i, line in enumerate(sample_lines, start=1):
        ocr_rows.append({
            "file": file.filename,
            "page_no": 1,
            "line_no": i,
            "extracted_text": line,
            "confidence": round(random.uniform(0.90, 0.99), 2),
            "timestamp": upload_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    ocr_df = pd.DataFrame(ocr_rows)

    # -------- PAYMENT ENGINE --------
    payment_df = pd.DataFrame([{
        "file": file.filename,
        "invoice_no": "IOCL-2024-INV-001",
        "amount_detected": 1000,
        "currency": "INR",
        "signature_present": True,
        "fraud_risk_score": 0.08,
        "final_status": "APPROVED",
        "processed_utc": upload_time.strftime("%Y-%m-%d %H:%M:%S")
    }])

    ocr_df.to_excel(OCR_FILE, index=False)
    payment_df.to_excel(PAYMENT_FILE, index=False)

    return RedirectResponse(url="/", status_code=303)

# ---------------- DOWNLOADS ----------------
@app.get("/download/ocr")
def download_ocr():
    return FileResponse(OCR_FILE, filename="ocr.xlsx")

@app.get("/download/payments")
def download_payments():
    return FileResponse(PAYMENT_FILE, filename="payments.xlsx")
