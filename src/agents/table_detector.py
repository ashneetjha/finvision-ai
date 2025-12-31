import cv2
from src.agents.ocr_agent import reader

# ---------------- TABLE DETECTOR (ROW-LEVEL, ROBUST) ----------------

def detect_table_rows(image_path):
    """
    Robust table row detector.
    Works for:
    - scanned PDFs
    - mobile camera images
    - screenshots
    - skewed documents (mild)
    """

    img = cv2.imread(str(image_path))
    if img is None:
        return []

    H, W = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ---------- PASS 1: MORPHOLOGICAL ROW BAND DETECTION ----------
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        15,
        3
    )

    # Kernel scaled to image size (CRITICAL)
    kernel_width = max(int(W * 0.15), 30)
    kernel_height = max(int(H * 0.004), 3)

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (kernel_width, kernel_height)
    )

    dilated = cv2.dilate(binary, kernel, iterations=1)

    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    row_boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # 🔑 RELATIVE filters (resolution-safe)
        if (
            h > H * 0.008 and          # row height
            h < H * 0.08 and
            w > W * 0.6                # near full-width row
        ):
            row_boxes.append((x, y, w, h))

    if row_boxes:
        row_boxes = sorted(row_boxes, key=lambda b: b[1])

        rows = []
        current = [row_boxes[0]]
        last_y = row_boxes[0][1]

        for box in row_boxes[1:]:
            if abs(box[1] - last_y) < max(box[3], H * 0.01):
                current.append(box)
            else:
                rows.append(current)
                current = [box]
                last_y = box[1]

        rows.append(current)
        return rows

    # ---------- PASS 2: OCR-BASED FALLBACK (LAST RESORT) ----------
    results = reader.readtext(img, detail=1, paragraph=False)
    if not results:
        return []

    text_boxes = []
    for bbox, _, conf in results:
        if conf < 0.5:
            continue
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        x, y = min(xs), min(ys)
        w, h = max(xs) - x, max(ys) - y
        text_boxes.append((x, y, w, h))

    if not text_boxes:
        return []

    text_boxes = sorted(text_boxes, key=lambda b: b[1])

    rows = []
    current = [text_boxes[0]]
    last_y = text_boxes[0][1]

    for box in text_boxes[1:]:
        if abs(box[1] - last_y) < max(box[3], H * 0.02):
            current.append(box)
        else:
            rows.append(current)
            current = [box]
            last_y = box[1]

    rows.append(current)
    return rows
