from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from pathlib import Path
import shutil
import subprocess

app = FastAPI(title="FinVision AI")

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "output"

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
                padding: 20px;
            }
            .card {
                background: #1e293b;
                padding: 20px;
                border-radius: 12px;
                max-width: 400px;
                margin: auto;
            }
            button {
                background: #38bdf8;
                border: none;
                padding: 10px;
                width: 100%;
                border-radius: 8px;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>FinVision AI</h2>
            <p>Upload a document to process OCR & payment validation.</p>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required><br><br>
                <button type="submit">Process</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    img_path = RAW_DIR / file.filename
    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["python", "src/ocr_pipeline.py"])
    subprocess.run(["python", "src/payment_engine.py"])

    return {
        "status": "success",
        "ocr": "data/output/ocr.xlsx",
        "payments": "data/output/payments.xlsx"
    }
