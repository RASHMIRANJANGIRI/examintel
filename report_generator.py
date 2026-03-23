from fpdf import FPDF

def create_pdf_report(file_path, subject, predictions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Predicted Questions Report - {subject}", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", size=12)

    for i, (question, score, topic) in enumerate(predictions, start=1):
        line = f"{i}. {question} | Score: {score} | Topic: {topic}"
        pdf.multi_cell(0, 10, line)
        pdf.ln(1)

    pdf.output(file_path)