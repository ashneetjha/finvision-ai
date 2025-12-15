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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial;
                background: #0f172a;
                color: white;
                padding: 20px;
            }
            .box {
                background: #111827;
                padding: 20px;
                border-radius: 10px;
                max-width: 400px;
                margin: auto;
            }
            input, button {
                width: 100%;
                padding: 10px;
                margin-top: 10px;
                border-radius: 6px;
            }
            button {
                background: #2563eb;
                color: white;
                border: none;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>FinVision AI</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required />
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

    subprocess.run(["python", "src/ocr_pipeline.py"])
    subprocess.run(["python", "src/payment_engine.py"])

    return {
        "status": "processed",
        "file": file.filename,
        "outputs": [
            "data/output/ocr.xlsx",
            "data/output/payments.xlsx"
        ]
    }
