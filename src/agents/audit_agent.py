import cv2
import numpy as np
from pathlib import Path

# ---------------- AUDIT AGENT (DECISION + COMPLIANCE) ----------------

def _detect_signature_and_ink(image_path):
    """
    Detects ink density and infers signature presence.
    Deterministic, explainable, audit-safe.
    """

    signature_present = False
    ink_density_score = 0.0

    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return signature_present, ink_density_score

    # Binary threshold to isolate ink regions
    _, binary = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)

    ink_pixels = np.count_nonzero(binary)
    total_pixels = binary.size

    ink_density_score = round(ink_pixels / total_pixels, 4)

    # Heuristic threshold (tunable, explainable)
    signature_present = ink_density_score >= 0.01

    return signature_present, ink_density_score


def evaluate_payment(file_name, ocr_df, avg_confidence, processed_time):
    """
    Audit Agent:
    - Signature & ink validation
    - Amount extraction
    - Fraud risk estimation
    - Final payment decision (NO auto-approval)
    """

    # ---------------- SIGNATURE / INK ANALYSIS ----------------
    image_path = Path(__file__).resolve().parents[2] / "data" / "raw" / file_name
    signature_present, ink_density_score = _detect_signature_and_ink(image_path)

    # ---------------- AMOUNT EXTRACTION (OCR-ASSISTED) ----------------
    detected_amount = 0

    for text in ocr_df["extracted_text"]:
        digits = "".join(ch for ch in text if ch.isdigit())
        if len(digits) >= 3:
            detected_amount = int(digits)
            break

    # ---------------- AUDIT DECISION LOGIC ----------------
    audit_remarks = []
    final_status = "ON_HOLD"
    fraud_risk_score = 0.0

    if not signature_present:
        audit_remarks.append("Signature missing or ink density below threshold")

    if avg_confidence < 0.6:
        audit_remarks.append("Low OCR confidence")

    if detected_amount <= 0:
        audit_remarks.append("Amount not reliably detected")

    if not audit_remarks:
        final_status = "READY_FOR_PAYMENT"
        fraud_risk_score = 0.02
    else:
        fraud_risk_score = round(0.3 + (0.1 * len(audit_remarks)), 2)

    return {
        "file_name": file_name,
        "amount_detected": detected_amount,
        "currency": "INR",
        "signature_present": signature_present,
        "ink_density_score": ink_density_score,
        "avg_ocr_confidence": avg_confidence,
        "fraud_risk_score": fraud_risk_score,
        "final_status": final_status,
        "audit_remarks": "; ".join(audit_remarks),
        "processed_utc": processed_time
    }
