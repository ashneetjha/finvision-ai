# Use a lightweight Python version (Debian 12 Bookworm based)
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# 1. Install system dependencies
# We keep your correct fix for Debian Bookworm (libgl1 instead of libgl1-mesa-glx)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy dependencies first (for caching)
COPY requirements.txt .

# 3. Install Python libraries
# Force CPU-only PyTorch to save space and prevent memory crashes
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# CRITICAL FIX FOR HUGGING FACE SPACES
# ---------------------------------------------------------------------------
# 4. Create writable directories for EasyOCR
# Hugging Face runs as a restricted user (1000), so we must manually open permissions
RUN mkdir -p /app/data/raw /app/data/output /app/data/ground_truth /app/.EasyOCR && \
    chmod -R 777 /app

# 5. Tell EasyOCR to use our writable folder
ENV EASYOCR_MODULE_PATH=/app/.EasyOCR
# ---------------------------------------------------------------------------

# 6. Copy the rest of your app code
COPY . .

# 7. Command to run the app
# strictly use port 7860 for Hugging Face
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "7860"]