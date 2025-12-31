import sys
import os
from pathlib import Path
import pandas as pd
import Levenshtein  # pip install python-Levenshtein

# ---------------- PATH FIX ----------------
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.agents.ocr_agent import OCRAgent

# ---------------- CONFIGURATION ----------------
RAW_DIR = ROOT / "data" / "raw"
GT_DIR = ROOT / "data" / "ground_truth"

def load_ground_truth(filename):
    base_name = os.path.splitext(filename)[0]
    gt_path = GT_DIR / f"{base_name}.txt"
    if not gt_path.exists():
        return None
    with open(gt_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def calculate_accuracy(ocr_text, gt_text):
    if not gt_text: return 0.0, 0.0

    # 1. Character Accuracy
    char_dist = Levenshtein.distance(ocr_text, gt_text)
    char_acc = max(0, (1 - char_dist / len(gt_text))) * 100

    # 2. Word Accuracy (Set Intersection Method - Fairer for Tables)
    # This ignores "order" and checks if the correct words exist ANYWHERE
    ocr_words = set(ocr_text.split())
    gt_words = set(gt_text.split())
    
    common = ocr_words.intersection(gt_words)
    word_acc = (len(common) / len(gt_words)) * 100 if gt_words else 0

    return round(char_acc, 2), round(word_acc, 2)

def run_test():
    print("\n" + "="*50)
    print(" 📊 FINVISION AI - DIAGNOSTIC ACCURACY TEST")
    print("="*50)

    try:
        agent = OCRAgent()
    except Exception as e:
        print(f"❌ Failed: {e}")
        return

    files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(('.png', '.jpg'))]
    
    for file in files:
        print(f"\n 🔹 Testing: {file}")
        
        file_path = RAW_DIR / file
        df = agent.extract_structured_data(file_path)
        
        # Flatten and Clean
        extracted_text = " ".join(df.astype(str).values.flatten())
        extracted_text = " ".join(extracted_text.split()) 

        gt_text = load_ground_truth(file)

        if gt_text:
            gt_text = " ".join(gt_text.split())
            c_acc, w_acc = calculate_accuracy(extracted_text, gt_text)
            
            print(f"    ✅ Char Acc: {c_acc}% | Word Acc (Bag-of-Words): {w_acc}%")
            
            # --- DEBUG VIEW: SHOW ME THE DIFFERENCE ---
            print("\n   COMPARISON (First 100 chars):")
            print(f"    [EXPECTED]: {gt_text[:100]}...")
            print(f"    [ACTUAL]  : {extracted_text[:100]}...")
            print("-" * 50)
        else:
            print(f"    ⚠️ Skipped (No .txt found)")

if __name__ == "__main__":
    run_test()