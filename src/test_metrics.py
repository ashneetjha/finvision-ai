from pathlib import Path
from src.agents.evaluation_agent import character_accuracy, word_accuracy

# ---------------- OFFLINE OCR EVALUATION SCRIPT ----------------

ocr_output = """
Table name daily historcal stoci prices volumes
Date Open High Close Last Volume
01Doi7 21.325.440
01/032017 62.58 20,655.190
...
"""

gt_path = Path("data/ground_truth/sample1.txt")
ground_truth = gt_path.read_text(encoding="utf-8")

char_acc = character_accuracy(ocr_output, ground_truth)
word_acc = word_accuracy(ocr_output, ground_truth)

print(f"Character Accuracy: {char_acc:.2f} %")
print(f"Word Accuracy: {word_acc:.2f} %")
