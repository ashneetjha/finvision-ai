import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import pandas as pd
from datetime import datetime

from src.agents.ocr_agent import run_ocr
from src.agents.audit_agent import evaluate_payment
from src.agents.reporting_agent import generate_dashboard

app = FastAPI(title="FinVision AI")

# ---------------- PATH SETUP (RENDER SAFE) ----------------
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "output"
REPORT_DIR = BASE_DIR / "reports"

OCR_FILE = OUT_DIR / "ocr.xlsx"
PAYMENT_FILE = OUT_DIR / "payments.xlsx"
DASHBOARD_FILE = REPORT_DIR / "finvision_dashboard.xlsx"

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ---------------- DASHBOARD UI ----------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------------- UPLOAD & PROCESS ----------------
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    img_path = RAW_DIR / file.filename

    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    processed_time = datetime.utcnow()

    # -------- OCR AGENT (ML PERCEPTION) --------
    ocr_rows = run_ocr(img_path)

    ocr_df = pd.DataFrame([
        {
            "file_name": file.filename,
            "page_no": row["page_no"],
            "line_no": row["line_no"],
            "extracted_text": row["extracted_text"],
            "confidence": row["confidence"],
            "processed_utc": processed_time
        }
        for row in ocr_rows
    ])

    # -------- DATA QUALITY AGENT --------
    avg_confidence = round(ocr_df["confidence"].mean(), 3) if not ocr_df.empty else 0.0
    data_quality_flag = "OK" if avg_confidence >= 0.6 else "LOW_CONFIDENCE"

    decision_stage = (
        "REQUIRES_MANUAL_REVIEW"
        if avg_confidence < 0.6
        else "AUTO_AUDIT_PASSED"
    )

    # -------- AUDIT AGENT --------
    payment_record = evaluate_payment(
        file_name=file.filename,
        ocr_df=ocr_df,
        avg_confidence=avg_confidence,
        processed_time=processed_time
    )

    payment_record["decision_stage"] = decision_stage
    payment_record["data_quality_flag"] = data_quality_flag

    payment_df = pd.DataFrame([payment_record])

    # -------- REPORTING DATA PERSISTENCE --------
    if OCR_FILE.exists():
        ocr_df = pd.concat([pd.read_excel(OCR_FILE), ocr_df], ignore_index=True)
    ocr_df.to_excel(OCR_FILE, index=False)

    if PAYMENT_FILE.exists():
        payment_df = pd.concat([pd.read_excel(PAYMENT_FILE), payment_df], ignore_index=True)
    payment_df.to_excel(PAYMENT_FILE, index=False)

    # -------- EXECUTIVE DASHBOARD GENERATION --------
    generate_dashboard()

    return JSONResponse({
        "status": "processed",
        "lines_detected": len(ocr_df),
        "avg_confidence": avg_confidence,
        "data_quality_flag": data_quality_flag,
        "decision_stage": decision_stage,
        "dashboard_generated": True
    })

# ---------------- DOWNLOAD ENDPOINTS ----------------
@app.get("/download/ocr")
def download_ocr():
    if not OCR_FILE.exists():
        return JSONResponse({"error": "OCR file not available"}, status_code=404)
    return FileResponse(OCR_FILE, filename="ocr.xlsx")

@app.get("/download/payments")
def download_payments():
    if not PAYMENT_FILE.exists():
        return JSONResponse({"error": "Payments file not available"}, status_code=404)
    return FileResponse(PAYMENT_FILE, filename="payments.xlsx")

@app.get("/download/dashboard")
def download_dashboard():
    if not DASHBOARD_FILE.exists():
        return JSONResponse(
            {"error": "Dashboard not available yet"},
            status_code=404
        )
    return FileResponse(
        DASHBOARD_FILE,
        filename="finvision_dashboard.xlsx"
    )
