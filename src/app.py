from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import shutil
import subprocess

app = FastAPI(title="FinVision AI")

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "output"

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

OCR_FILE = OUT_DIR / "ocr.xlsx"
PAYMENT_FILE = OUT_DIR / "payments.xlsx"


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <head>
        <title>FinVision AI</title>
        <style>
            body { font-family: Arial; background:#0f172a; color:white; text-align:center; }
            .box { margin-top:60px; }
            button { padding:12px 20px; font-size:16px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>FinVision AI</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <br><br>
                <button type="submit">Upload & Process</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    img_path = RAW_DIR / file.filename
    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["python", "src/ocr_pipeline.py"], check=True)
    subprocess.run(["python", "src/payment_engine.py"], check=True)

    return {
        "status": "success",
        "ocr": "/download/ocr",
        "payments": "/download/payments"
    }


@app.get("/download/ocr")
def download_ocr():
    return FileResponse(OCR_FILE, filename="ocr.xlsx")


@app.get("/download/payments")
def download_payments():
    return FileResponse(PAYMENT_FILE, filename="payments.xlsx")
