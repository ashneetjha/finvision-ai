# Use a lightweight Python version (Debian 12 Bookworm based)
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# 1. Install system dependencies
# FIX: 'libgl1-mesa-glx' is renamed to 'libgl1' in newer Debian versions
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy dependencies first (for caching)
COPY requirements.txt .

# 3. Install Python libraries
# Force CPU-only PyTorch to save space and prevent memory crashes
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of your app code
COPY . .

# 5. Command to run the app
CMD ["sh", "-c", "uvicorn src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]