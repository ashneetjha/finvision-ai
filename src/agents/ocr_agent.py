import cv2
import easyocr
import numpy as np

# ---------------- OCR AGENT (ML PERCEPTION) ----------------

# Initialize EasyOCR once (CPU, Render-safe)
reader = easyocr.Reader(
    ['en'],
    gpu=False,
    verbose=False
)

def preprocess_image(image_path):
    """
    OCR Agent preprocessing:
    - grayscale
    - resize
    - noise reduction
    - adaptive threshold
    """

    img = cv2.imread(str(image_path))
    if img is None:
        return None

    # 1. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Resize for better OCR accuracy
    scale_percent = 150
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

    # 3. Noise reduction
    blurred = cv2.GaussianBlur(resized, (5, 5), 0)

    # 4. Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    return thresh

def run_ocr(image_path):
    """
    Executes ML-based OCR using EasyOCR.
    Returns line-wise extracted text with confidence scores.
    """

    processed_img = preprocess_image(image_path)
    if processed_img is None:
        return []

    results = reader.readtext(
        processed_img,
        detail=1,
        paragraph=False,
        contrast_ths=0.4,
        adjust_contrast=0.7,
        text_threshold=0.6,
        low_text=0.3
    )

    ocr_rows = []
    line_no = 1

    for _, text, confidence in results:
        clean_text = text.strip()
        if len(clean_text) < 2:
            continue

        ocr_rows.append({
            "page_no": 1,
            "line_no": line_no,
            "extracted_text": clean_text,
            "confidence": round(float(confidence), 4)
        })
        line_no += 1

    return ocr_rows
