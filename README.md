# FinVision AI  
### Agentic AI System for Document Digitization & Payment Validation

FinVision AI is an agentic AI–based decision-support system designed to digitize financial documents, evaluate audit readiness, and generate executive-grade reports to assist payment validation workflows in enterprise and PSU environments.

---

## 🔹 Project Objectives

- Convert physical documents into structured digital data
- Perform OCR using machine learning models
- Assess data quality and audit readiness
- Support payment decision-making (without auto-payment)
- Generate management-ready Excel dashboards
- Ensure deployment safety on free-tier infrastructure

---

## 🔹 System Architecture (Agentic Design)

The system is structured as independent agents:

| Agent | Responsibility |
|-----|---------------|
| OCR Agent | Extracts text using EasyOCR with image preprocessing |
| Audit Agent | Signature presence, amount extraction, risk scoring |
| Evaluation Agent | OCR accuracy benchmarking |
| Reporting Agent | Executive Excel dashboard generation |
| Application Layer | Orchestrates agents via FastAPI |

This separation improves explainability, auditability, and maintainability.

---

## 🔹 End-to-End Workflow

1. User uploads document (file or camera)
2. OCR agent extracts structured text
3. Data quality metrics are computed
4. Audit agent evaluates payment readiness
5. Reporting agent generates Excel dashboards
6. Outputs are available for download via UI

---

## 🔹 Outputs Generated

- `ocr.xlsx` – OCR text with confidence scores  
- `payments.xlsx` – Audit and payment decision records  
- `finvision_dashboard.xlsx` – Executive review dashboard  

---

## 🔹 Executive Dashboard Contents

- Executive Summary (KPIs)
- Payment Decisions (actionable table)
- Risk Analysis
- OCR Quality Metrics
- Raw Data for traceability

---

## 🔹 Deployment

- Backend: FastAPI
- Hosting: Render (Free Tier)
- No GPU, no paid services
- CPU-only, deployment-safe libraries

---

## 🔹 Limitations

- OCR accuracy depends on document quality
- Signature detection is heuristic-based
- Amount extraction uses rule-based logic
- Fraud risk scoring is simulated
- No authentication or role-based access

These are documented and considered future enhancement areas.

---

## 🔹 Future Enhancements

- Domain-specific OCR fine-tuning
- NLP-based amount extraction
- Signature classification models
- Human-in-the-loop feedback integration
- Role-based access and logging
- Enhanced evaluation datasets

---

## 🔹 Tech Stack

- Python 3.10
- FastAPI
- EasyOCR
- OpenCV (Headless for easy deployability)
- Pandas, OpenPyXL
- HTML, CSS, JavaScript

