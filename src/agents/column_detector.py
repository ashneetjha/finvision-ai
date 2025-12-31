import cv2
import numpy as np

# ---------------- COLUMN DETECTOR (PRODUCTION-GRADE) ----------------

def detect_columns(image_path, expected_cols=6):
    """
    Detect vertical column regions for financial tables.
    Robust for:
    - Scanned PDFs
    - Camera images
    - PSU / bank statements

    Returns: List[(x, y, w, h)] ordered left → right
    """

    img = cv2.imread(str(image_path))
    if img is None:
        return []

    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Strong adaptive threshold (camera-safe)
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        5
    )

    # Remove horizontal noise
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (25, 1)
    )
    binary = cv2.morphologyEx(
        binary, cv2.MORPH_OPEN, horizontal_kernel
    )

    # Vertical projection
    vertical_density = np.sum(binary > 0, axis=0)

    # Smooth projection (critical)
    kernel = np.ones(25) / 25
    vertical_density = np.convolve(vertical_density, kernel, mode="same")

    threshold = 0.2 * np.max(vertical_density)

    active = vertical_density > threshold

    segments = []
    start = None

    for i, val in enumerate(active):
        if val and start is None:
            start = i
        elif not val and start is not None:
            if i - start > 20:   # minimum column width
                segments.append((start, i))
            start = None

    if start and (w - start) > 20:
        segments.append((start, w))

    if len(segments) < expected_cols:
        # 🔁 Fallback: even split (never return empty)
        col_width = w // expected_cols
        segments = [
            (i * col_width, (i + 1) * col_width)
            for i in range(expected_cols)
        ]

    # Keep best columns
    segments = sorted(segments, key=lambda x: x[0])
    segments = segments[:expected_cols]

    columns = [(x1, 0, x2 - x1, h) for x1, x2 in segments]
    return columns
