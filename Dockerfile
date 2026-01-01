# Use a lightweight Python version
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# 1. Install system dependencies required for OpenCV and EasyOCR
# This fixes the "libGL.so.1" missing error common on Cloud
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy dependencies first (for better caching)
COPY requirements.txt .

# 3. Install Python libraries
# We use --no-cache-dir to keep the image small
# We force CPU-only PyTorch to prevent memory crashes
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your app code
COPY . .

# 5. Command to run the app
CMD ["sh", "-c", "uvicorn src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]