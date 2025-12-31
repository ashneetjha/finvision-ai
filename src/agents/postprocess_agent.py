import cv2
import re
from pathlib import Path
from typing import List, Dict

from src.agents.column_detector import detect_columns
from src.agents.ocr_agent import reader

# ---------------- POST-OCR STRUCTURE RECOVERY ----------------

DATE_REGEX = re.compile(r"\d{2}[\/\-]\d{2}[\/\-]\d{4}")

def normalize_date(text: str):
    match = DATE_REGEX.search(text)
    return match.group(0) if match else None


def clean_number(text: str):
    text = text.replace(",", "")
    if text.count(".") > 1:
        text = text.replace(".", "")
    try:
        return float(text)
    except:
        return None


def ocr_column(image, col_box):
    """
    OCR a single column and return cleaned text lines.
    """
    x, y, w, h = col_box
    roi = image[y:y+h, x:x+w]

    results = reader.readtext(
        roi,
        detail=0,
        paragraph=False
    )

    cleaned = [r.strip() for r in results if len(r.strip()) > 1]
    return cleaned


def parse_columns_to_table(image_path: Path) -> List[Dict]:
    """
    Image → Column detection → OCR per column → Row reconstruction
    """

    image = cv2.imread(str(image_path))
    if image is None:
        return []

    columns = detect_columns(image_path)
    if len(columns) < 6:
        return []

    # OCR each column independently
    column_texts = [ocr_column(image, col) for col in columns]

    date_col = column_texts[0]
    open_col = column_texts[1]
    high_col = column_texts[2]
    low_col = column_texts[3]
    close_col = column_texts[4]
    vol_col = column_texts[5]

    rows = []

    for i in range(len(date_col)):
        date = normalize_date(date_col[i])
        if not date:
            continue

        try:
            open_p = clean_number(open_col[i])
            high_p = clean_number(high_col[i])
            low_p = clean_number(low_col[i])
            close_p = clean_number(close_col[i])
            volume = clean_number(vol_col[i])
        except:
            continue

        if None in (open_p, high_p, low_p, close_p, volume):
            continue

        rows.append({
            "Date": date,
            "Open": round(open_p, 2),
            "High": round(high_p, 2),
            "Low": round(low_p, 2),
            "Close": round(close_p, 2),
            "Volume": int(volume)
        })

    return rows
