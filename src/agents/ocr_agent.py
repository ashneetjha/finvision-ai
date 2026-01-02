import pandas as pd
import numpy as np
import easyocr
import cv2
import sys
from pdf2image import convert_from_path #
import warnings

warnings.filterwarnings("ignore")

class OCRAgent:
    def __init__(self):
        self.reader = None
        self.demo_mode = False
        
        print(" [OCR Agent] Initializing...")
        try:
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False) 
            print(" [OCR Agent] ✅ EasyOCR (ML Engine) Loaded Successfully.")
        except ImportError as e:
            print(f" [OCR Agent] ⚠️  Dependency Error: {e}")
            self.demo_mode = True
        except Exception as e:
            print(f" [OCR Agent] ⚠️  Unexpected Init Error: {e}")
            self.demo_mode = True

    def _preprocess_image(self, img_array):
        """
        Enhances image for better OCR accuracy.
        Applies: Grayscale -> Gaussian Blur -> Adaptive Thresholding
        """
        try:
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_array

            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            return binary
        except Exception as e:
            print(f" [OCR Agent] Preprocessing warning: {e}. Using raw image.")
            return img_array

    def _results_to_dataframe(self, results):
        """
        Converts raw EasyOCR results [(bbox, text, conf), ...] into a 
        structured DataFrame using Y-coordinate clustering.
        """
        if not results:
            return pd.DataFrame()

        results.sort(key=lambda x: x[0][0][1]) 

        rows = []
        current_row = []
        y_tolerance = 20 

        previous_y = results[0][0][0][1]

        for bbox, text, conf in results:
            current_y = bbox[0][1]

            if abs(current_y - previous_y) > y_tolerance:
                current_row.sort(key=lambda x: x['x'])
                rows.append([item['text'] for item in current_row])
                
                current_row = []
                previous_y = current_y
            current_row.append({'text': text.strip(), 'x': bbox[0][0]})

        if current_row:
            current_row.sort(key=lambda x: x['x'])
            rows.append([item['text'] for item in current_row])

        max_cols = max([len(r) for r in rows]) if rows else 0
        padded_rows = [row + [''] * (max_cols - len(row)) for row in rows]
        df = pd.DataFrame(padded_rows)
        
        if not df.empty and len(df) > 1:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            
        return df

    def extract_structured_data(self, file_path):
        """
        Main Entry Point: Handles both Images (.png/.jpg) and PDFs.
        """
        print(f" [OCR Agent] Scanning: {file_path}")

        if self.demo_mode:
            return self._get_demo_data()

        try:
            str_path = str(file_path)
            all_dfs = []

            # --- CASE A: PDF DOCUMENT ---
            if str_path.lower().endswith('.pdf'):
                print(" [OCR Agent] 📄 PDF detected. Converting pages to images...")
                
                # Convert PDF pages to list of PIL Images
                pil_images = convert_from_path(str_path)
                
                for i, pil_img in enumerate(pil_images):
                    print(f" [OCR Agent] Processing Page {i+1}/{len(pil_images)}...")
                    
                    # Convert PIL -> OpenCV (Numpy)
                    open_cv_image = np.array(pil_img)
                    open_cv_image = open_cv_image[:, :, ::-1].copy() # Convert RGB to BGR
                    
                    # Preprocess & Inference
                    processed_img = self._preprocess_image(open_cv_image)
                    results = self.reader.readtext(processed_img, detail=1)
                    
                    # Structure Data
                    page_df = self._results_to_dataframe(results)
                    all_dfs.append(page_df)
                
                # Combine all pages into one big table
                if all_dfs:
                    final_df = pd.concat(all_dfs, ignore_index=True)
                    return final_df
                else:
                    return pd.DataFrame()

            # --- CASE B: STANDARD IMAGE ---
            else:
                # Read image using OpenCV
                img = cv2.imread(str_path)
                if img is None:
                    # Fallback if cv2 fails to read path
                    results = self.reader.readtext(str_path, detail=1)
                else:
                    processed_img = self._preprocess_image(img)
                    results = self.reader.readtext(processed_img, detail=1)
                
                return self._results_to_dataframe(results)

        except Exception as e:
            print(f" [OCR Agent] ❌ Inference failed: {e}. Returning fallback.")
            return self._get_demo_data()

    def _get_demo_data(self):
        """
        Returns structured data for testing/demo if ML engine fails.
        """
        print(" [OCR Agent] ℹ️  Using Fallback Data (Demo Mode)")
        data = {
            "Date": ["01/04/2017", "01/03/2017", "12/30/2016", "12/29/2016", "12/28/2016"],
            "Open": [62.48, 62.79, 62.96, 62.86, 63.40],
            "High": [62.75, 62.84, 62.99, 63.20, 63.40],
            "Low": [62.12, 62.125, 62.03, 62.73, 62.83],
            "Close / Last": [62.30, 62.58, 62.14, 62.90, 62.99],
            "Volume": ["21,325,140", "20,655,190", "25,575,720", "10,248,460", "14,348,340"]
        }
        return pd.DataFrame(data)