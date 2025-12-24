import pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import PieChart, BarChart, Reference

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "data" / "output"
REPORT_DIR = BASE_DIR / "reports"

OCR_FILE = OUTPUT_DIR / "ocr.xlsx"
PAYMENT_FILE = OUTPUT_DIR / "payments.xlsx"
DASHBOARD_FILE = REPORT_DIR / "finvision_dashboard.xlsx"

REPORT_DIR.mkdir(exist_ok=True)

def generate_dashboard():
    pay_df = pd.read_excel(PAYMENT_FILE)
    ocr_df = pd.read_excel(OCR_FILE)

    with pd.ExcelWriter(DASHBOARD_FILE, engine="openpyxl") as writer:
        pay_df.to_excel(writer, sheet_name="PAYMENT_DECISIONS", index=False)
        ocr_df.to_excel(writer, sheet_name="RAW_OCR_DATA", index=False)

    wb = load_workbook(DASHBOARD_FILE)
    build_executive_summary(wb, pay_df, ocr_df)
    format_payment_sheet(wb)
    build_risk_analysis(wb, pay_df)
    build_ocr_quality(wb, ocr_df)

    wb.save(DASHBOARD_FILE)

def build_executive_summary(wb, pay_df, ocr_df):
    ws = wb.create_sheet("EXECUTIVE_SUMMARY", 0)

    ws["A1"] = "FINVISION AI – EXECUTIVE DASHBOARD"
    ws["A1"].font = Font(size=16, bold=True)
    ws.merge_cells("A1:F1")

    total = len(pay_df)
    ready = len(pay_df[pay_df["final_status"] == "READY_FOR_PAYMENT"])
    hold = len(pay_df[pay_df["final_status"] == "ON_HOLD"])
    avg_conf = round(ocr_df["confidence"].mean(), 2)
    high_risk = len(pay_df[pay_df["fraud_risk_score"] > 0.5])

    metrics = [
        ("Total Documents Processed", total, "D9F99D"),
        ("Ready for Payment", ready, "22C55E"),
        ("On Hold (Audit Review)", hold, "FACC15"),
        ("Avg OCR Confidence", avg_conf, "38BDF8"),
        ("High Risk Documents", high_risk, "EF4444"),
    ]

    row = 3
    for title, value, color in metrics:
        ws[f"A{row}"] = title
        ws[f"A{row}"].font = Font(bold=True)
        ws[f"B{row}"] = value
        ws[f"B{row}"].font = Font(size=14, bold=True)
        ws[f"B{row}"].fill = PatternFill("solid", fgColor=color)
        ws[f"B{row}"].alignment = Alignment(horizontal="center")
        row += 1

def format_payment_sheet(wb):
    ws = wb["PAYMENT_DECISIONS"]
    ws.freeze_panes = "A2"

    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 18

    for cell in ws[1]:
        cell.font = Font(bold=True)

def build_risk_analysis(wb, pay_df):
    ws = wb.create_sheet("RISK_ANALYSIS")

    ws["A1"] = "Risk Distribution"
    ws["A1"].font = Font(bold=True)

    ws.append(["Risk Category", "Count"])
    ws.append(["Low (<0.3)", len(pay_df[pay_df["fraud_risk_score"] < 0.3])])
    ws.append(["Medium (0.3–0.6)", len(pay_df[(pay_df["fraud_risk_score"] >= 0.3) & (pay_df["fraud_risk_score"] <= 0.6)])])
    ws.append(["High (>0.6)", len(pay_df[pay_df["fraud_risk_score"] > 0.6])])

    chart = BarChart()
    data = Reference(ws, min_col=2, min_row=2, max_row=4)
    labels = Reference(ws, min_col=1, min_row=3, max_row=5)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(labels)
    chart.title = "Fraud Risk Distribution"

    ws.add_chart(chart, "D2")

def build_ocr_quality(wb, ocr_df):
    ws = wb.create_sheet("OCR_QUALITY")

    ws["A1"] = "OCR Quality Overview"
    ws["A1"].font = Font(bold=True)

    ws.append(["Metric", "Value"])
    ws.append(["Average OCR Confidence", round(ocr_df["confidence"].mean(), 2)])
    ws.append(["Min OCR Confidence", round(ocr_df["confidence"].min(), 2)])
    ws.append(["Max OCR Confidence", round(ocr_df["confidence"].max(), 2)])
