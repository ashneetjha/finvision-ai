from difflib import SequenceMatcher
import re

# ---------------- EVALUATION AGENT (ML METRICS) ----------------

def normalize(text: str) -> str:
    """
    Normalizes text for fair OCR comparison.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def character_accuracy(pred: str, gt: str) -> float:
    """
    Character-level OCR accuracy (%).
    """
    return SequenceMatcher(None, pred, gt).ratio() * 100

def word_accuracy(pred: str, gt: str) -> float:
    """
    Word-level OCR accuracy (%).
    """
    pred_words = normalize(pred).split()
    gt_words = normalize(gt).split()
    matches = sum(1 for w in pred_words if w in gt_words)
    return (matches / max(len(gt_words), 1)) * 100
