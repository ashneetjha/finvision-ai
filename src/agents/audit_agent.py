import pandas as pd
import numpy as np
# Switched from cv2 to PIL to prevent DLL/Installation errors
from PIL import Image, ImageOps

class AuditAgent:
    def __init__(self):
        pass

    def _detect_ink_density(self, image_path):
        """
        Detects ink density using PIL (Pillow) instead of OpenCV.
        This prevents the 'DLL load failed' error.
        """
        try:
            # 1. Open Image
            with Image.open(image_path) as img:
                # 2. Convert to Grayscale (L mode)
                gray = ImageOps.grayscale(img)
                
                # 3. Binarize (Thresholding)
                # Any pixel < 150 becomes 0 (Black/Ink), else 255 (White/Paper)
                # We count the black pixels.
                histogram = gray.histogram()
                
                # Sum of pixels with value < 150 (Dark pixels)
                ink_pixels = sum(histogram[:150])
                total_pixels = gray.width * gray.height

                if total_pixels == 0:
                    return False, 0.0

                ink_density_score = round(ink_pixels / total_pixels, 4)

                # Heuristic: If ink density > 1%, likely contains a signature/stamp
                signature_present = ink_density_score >= 0.01

                return signature_present, ink_density_score
                
        except Exception as e:
            print(f" [Audit Agent] Ink detection error: {e}")
            return False, 0.0

    def audit_dataframe(self, df, image_path=None):
        """
        Main Function called by App.py.
        """
        print(" [Audit Agent] Validating financial logs...")
        
        # 1. Image Level Audit (Physical Signature)
        sig_present = False
        ink_score = 0.0
        if image_path:
            sig_present, ink_score = self._detect_ink_density(image_path)
            print(f" [Audit Agent] Image Analysis: Signature={'Yes' if sig_present else 'No'} (Density: {ink_score})")

        if df.empty:
            return df, {"total": 0, "risk": 0, "safe": 0, "ink_score": ink_score}

        # 2. Row Level Audit (Data Integrity)
        def check_row_risk(row):
            for val in row:
                s_val = str(val).strip().lower()
                # Check for missing values, NaNs, or explicit "None" strings
                if s_val in ['', 'nan', 'none', 'null']:
                    return "Risk (Unsigned/Empty)"
            return "Verified"

        df["Audit Status"] = df.apply(check_row_risk, axis=1)
        
        # 3. Calculate Stats for the Dashboard
        total = len(df)
        risk_count = len(df[df["Audit Status"] == "Risk (Unsigned/Empty)"])
        safe_count = total - risk_count
        
        stats = {
            "total_rows": total,
            "unsigned_count": risk_count, 
            "verified_count": safe_count,
            "signature_detected": sig_present,
            "ink_density": ink_score
        }
        
        return df, stats