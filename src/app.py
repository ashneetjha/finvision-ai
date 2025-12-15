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


# -------------------------------
# DASHBOARD (MOBILE + WEB READY)
# -------------------------------
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
            text-align: center;
            padding: 30px;
        }
        .card {
            background: #1e293b;
            padding: 25px;
            border-radius: 14px;
            max-width: 420px;
            margin: auto;
            box-shadow: 0 0 20px rgba(0,0,0,0.4);
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
            margin-top: 15px;
            color: #22c55e;
            text-decoration: none;
        }
    </style>
</head>
<body>

<div class="card">
    <h2>📊 FinVision AI</h2>
    <p>Agentic AI for OCR & Financial Validation</p>

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


# -------------------------------
# UPLOAD + PROCESS
# -------------------------------
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    img_path = RAW_DIR / file.filename

    with open(img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    subprocess.run(["python", "src/ocr_pipeline.py"], check=True)
    subprocess.run(["python", "src/payment_engine.py"], check=True)

    return HTMLResponse("""
        <html>
        <body style="background:#0f172a;color:white;text-align:center;padding:40px">
            <h3>✅ Processing Complete</h3>
            <a href="/">⬅ Back to Dashboard</a>
        </body>
        </html>
    """)


# -------------------------------
# DOWNLOADS
# -------------------------------
@app.get("/download/ocr")
def download_ocr():
    if not OCR_FILE.exists():
        return {"error": "OCR file not found"}
    return FileResponse(
        path=OCR_FILE,
        filename="ocr.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.get("/download/payments")
def download_payments():
    if not PAYMENT_FILE.exists():
        return {"error": "Payments file not found"}
    return FileResponse(
        path=PAYMENT_FILE,
        filename="payments.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
