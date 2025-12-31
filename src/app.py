import sys
import os
from pathlib import Path
import shutil
import uvicorn
import traceback

# ---------------- PATH FIX ----------------
# Forces Python to recognize the 'src' folder
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # FinVision-AI root
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# ---------------- SAFE IMPORTS ----------------
OCRAgent = None
AuditAgent = None
ReportingAgent = None

try:
    from src.agents.ocr_agent import OCRAgent
    from src.agents.audit_agent import AuditAgent
    from src.agents.reporting_agent import ReportingAgent
except ImportError as e:
    print("\n" + "="*50)
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    print("This is usually caused by a missing library (like cv2/OpenCV).")
    print("TRY RUNNING: pip install opencv-python-headless")
    print("="*50 + "\n")

app = FastAPI(title="FinVision AI")

# ---------------- SETUP DIRECTORIES ----------------
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "output"
TEMPLATES_DIR = ROOT / "templates"

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Global variable to track the last uploaded file for download
LAST_UPLOADED_FILE = None

# ---------------- AGENT INITIALIZATION ----------------
ocr_agent = None
audit_agent = None
reporting_agent = None

print(" [System] Initializing AI Agents...")

if OCRAgent is None:
    print(" [System] ⚠️  Skipping Agent Init because imports failed (Check logs above).")
else:
    try:
        ocr_agent = OCRAgent()
        audit_agent = AuditAgent()
        reporting_agent = ReportingAgent(output_dir=OUT_DIR)
        print(" [System] ✅ Agents Ready.")
    except Exception as e:
        print(f" [System] ❌ Error Initializing Agents: {e}")

# ---------------- ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    global LAST_UPLOADED_FILE

    # Check if agents loaded successfully
    if not ocr_agent:
        return JSONResponse({
            "status": "Error", 
            "message": "AI System failed to load. Check the terminal for 'ImportError'."
        }, status_code=500)

    try:
        # 1. Save File
        file_path = RAW_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Track file for the "Download Input" button
        LAST_UPLOADED_FILE = file.filename

        # 2. Run Pipeline
        df_ocr = ocr_agent.extract_structured_data(file_path)
        df_audited, stats = audit_agent.audit_dataframe(df_ocr, image_path=file_path)
        
        # Generates both dashboard and raw OCR excel
        reporting_agent.generate_dashboard(df_audited, stats)

        return JSONResponse({
            "status": "Success",
            "message": f"Processed successfully. Found {stats.get('unsigned_count', 0)} risks.",
            "download_url": "/download/dashboard"
        })

    except Exception as e:
        print(f"Processing Error: {e}")
        print(traceback.format_exc())
        return JSONResponse({"status": "Error", "message": str(e)}, status_code=500)

# ---------------- DOWNLOAD ENDPOINTS ----------------

@app.get("/download/dashboard")
def download_dashboard():
    """Serves the colored Executive Dashboard"""
    path = OUT_DIR / "FinVision_Dashboard.xlsx"
    if path.exists():
        return FileResponse(path, filename="FinVision_Dashboard.xlsx")
    return JSONResponse({"error": "Dashboard not generated yet"}, status_code=404)

@app.get("/download/ocr")
def download_ocr():
    """Serves the Raw OCR Data"""
    path = OUT_DIR / "ocr_data.xlsx"
    if path.exists():
        return FileResponse(path, filename="ocr_data.xlsx")
    return JSONResponse({"error": "OCR Data not found"}, status_code=404)

@app.get("/download/input")
def download_input():
    """Serves the Original Uploaded Image"""
    global LAST_UPLOADED_FILE
    if LAST_UPLOADED_FILE:
        path = RAW_DIR / LAST_UPLOADED_FILE
        if path.exists():
            return FileResponse(path, filename=LAST_UPLOADED_FILE)
    return JSONResponse({"error": "No input file uploaded yet"}, status_code=404)

if __name__ == "__main__":
    print("🚀 Starting Server at http://127.0.0.1:8000")
    # Run on localhost to avoid firewall issues
    uvicorn.run(app, host="127.0.0.1", port=8000)