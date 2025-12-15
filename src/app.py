from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import shutil
import subprocess

app = FastAPI(title="FinVision AI")

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "output"

OCR_FILE = OUT_DIR / "ocr.xlsx"
PAYMENT_FILE = OUT_DIR / "payments.xlsx"

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


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
                font-family: Arial;
                background: #0f172a;
                color: white;
                text-align: center;
                padding: 40px;
            }
            .box {
                background: #1e293b;
                padding: 30px;
                border-radius: 12px;
                max-width: 420px;
                margin: auto;
            }
            input, button {
                margin-top: 15px;
                padding: 10px;
                width: 100%;
                border-radius: 6px;
                border: none;
            }
            button {
                background: #38bdf8;
                font-weight: bold;
                cursor: pointer;
            }
            a {
                color: #22c55e;
                display: block;
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>📊 FinVision AI</h2>
            <p>Upload document for OCR & Payment Validation</p>

            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <button type="submit">Process Document</button>
            </form>

            <a href="/download/ocr">⬇ Download OCR Excel</a>
            <a href="/download/payments">⬇ Download Payments Excel</a>
        </div>
    </body>
    </html>
    """


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    img_path = RAW_DIR / file.filename

    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["python", "src/ocr_pipeline.py"])
    subprocess.run(["python", "src/payment_engine.py"])

    return {"status": "success"}


@app.get("/download/ocr")
def download_ocr():
    return FileResponse(OCR_FILE, filename="ocr.xlsx")


@app.get("/download/payments")
def download_payments():
    return FileResponse(PAYMENT_FILE, filename="payments.xlsx")
