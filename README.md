# 🦅 FinVision AI
### Intelligent Document Digitization & Financial Validation System

[![Deployment](https://img.shields.io/badge/Deployment-Hugging%20Face%20Spaces-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/ashneetjha/FinVision-AI)
[![Tech Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![AI Engine](https://img.shields.io/badge/AI-EasyOCR%20%2B%20PyTorch-EE4C2C?style=for-the-badge&logo=pytorch)](https://pytorch.org/)
[![Infrastructure](https://img.shields.io/badge/Container-Docker-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **Developed for Indian Oil Corporation Limited (IOCL) - Winter Internship 2025**
> *Transforming static financial documents into actionable, audited intelligence.*

---

### 📖 Project Overview

**FinVision AI** is an enterprise-grade Decision Support System (DSS) designed to automate the manual bottleneck of financial auditing. Unlike standard OCR tools that simply extract text, FinVision acts as an **intelligent auditor**. It ingests raw scanned images of financial instruments (invoices, payment logs, stock sheets), reconstructs their tabular structure, validates the mathematical integrity of the data, and exports audit-ready Excel reports.

Deployed as a cloud-native microservice, it leverages Deep Learning (CNN+RNN) for perception and deterministic algorithms for financial logic validation.

### 🚀 Key Features
* **📄 AI-Powered Digitization:** Extracts text and tables from non-standard, borderless scanned images using `EasyOCR`.
* **🧮 Automated Audit Logic:** Automatically verifies financial totals, flagging discrepancies (e.g., *Sum of rows ≠ Total Amount*).
* **📊 Structured Reporting:** Converts unstructured images into formatted `.xlsx` files with auto-generated headers.
* **☁️ Cloud-Native Architecture:** Fully containerized using **Docker** and deployed on **Hugging Face Spaces** (16GB RAM) for high-availability access.
* **⚡ Real-Time Dashboard:** A responsive web interface for instant document upload, analysis, and validation.

---

### 🛠️ Tech Stack & Architecture

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Core Framework** | **FastAPI** | High-performance async backend for handling API requests. |
| **AI Perception** | **EasyOCR (PyTorch)** | Deep Learning model for text detection and recognition. |
| **Image Processing** | **OpenCV** | Pre-processing, grayscale conversion, and noise reduction. |
| **Data Logic** | **Pandas & NumPy** | Tabular reconstruction and numeric validation algorithms. |
| **Infrastructure** | **Docker** | Containerization for consistent execution across OS. |
| **Deployment** | **Hugging Face** | Managed cloud hosting with Git LFS support. |

---


### ⚙️ Installation & Local Setup

Run FinVision AI on your local machine in minutes.

### Prerequisites
* Python 3.10+
* Git

### 1. Clone the Repository
```bash
git clone [https://github.com/ashneetjha/FinVision-AI.git](https://github.com/ashneetjha/FinVision-AI.git)
cd FinVision-AI

```

### 2. Create Virtual Environment (Recommended)

```bash
# Using Conda
conda create -n finvision python=3.10
conda activate finvision

```

### 3. Install Dependencies

```bash
# Note: This installs the CPU-only version of PyTorch to save space
pip install -r requirements.txt

```

### 4. Run the Application

```bash
uvicorn src.app:app --host 127.0.0.1 --port 8000 --reload

```

> Access the dashboard at: **http://127.0.0.1:8000**

---

## 🐳 Docker Deployment (The "Pro" Way)

FinVision is optimized for Docker. Build and run it anywhere without dependency issues.

```bash
# 1. Build the image
docker build -t finvision-ai .

# 2. Run the container (Maps port 7860 for consistency with HF Spaces)
docker run -p 7860:7860 finvision-ai

```

---

## 🌐 Live Demo

The project is deployed live on Hugging Face Spaces.

👉 **[Launch FinVision AI](https://huggingface.co/spaces/ashneetjha/FinVision-AI)**

---

## 🧠 How It Works (The "Real AI" Logic)

1. **Ingestion:** User uploads a scanned `.png` or `.jpg`.
2. **Pre-processing:** OpenCV converts the image to grayscale and applies adaptive thresholding to remove noise.
3. **OCR Inference:** EasyOCR (ResNet + LSTM) scans the image for text blocks and coordinates.
4. **Reconstruction Agent:** The system clusters text blocks into "Rows" based on Y-coordinates and "Columns" based on X-coordinates.
5. **Audit Agent:**
* *Sanity Check:* Converts string numbers ("1,200.00") to floats.
* *Validation:* Checks if `Row_1 + Row_2 + ... + Row_N == Total_Declared`.


6. **Reporting:** Generates a flagged Excel sheet highlighting any mismatches.

---


```

```