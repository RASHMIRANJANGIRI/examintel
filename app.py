import os
import io
import pandas as pd
import streamlit as st
from PIL import Image

from config import EXPORT_DIR
from models.db import Base, engine, SessionLocal
from models.subjects import UploadedPaper, PredictedQuestion
from core.ocr_engine import extract_text_from_image
from core.parser import split_into_questions
from core.predictor import group_similar_questions, rank_predictions
from core.analytics import extract_keywords, infer_topic
from core.report_generator import create_pdf_report

import pdfplumber
import pypdfium2 as pdfium

Base.metadata.create_all(bind=engine)

st.set_page_config(page_title="Exam Intelligence Platform", layout="wide")
st.title("🚀 Exam Intelligence Platform")
st.write("Upload question paper images or PDFs to get high-probability questions.")

st.sidebar.header("Controls")
similarity_threshold = st.sidebar.slider("Similarity Threshold", 0.10, 0.90, 0.45, 0.05)
top_n = st.sidebar.slider("Top Predictions", 5, 50, 10, 1)

subject = st.text_input("Subject Name")
exam_name = st.text_input("Exam Name", value="Semester Exam")
year = st.text_input("Academic Year", value="2025-26")


def extract_text_from_pdf(uploaded_file):
    extracted_text = ""
    pdf_bytes = uploaded_file.read()

    # 1) Try normal text extraction
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
    except Exception:
        pass

    # 2) If little/no text found, use OCR on rendered PDF pages
    if len(extracted_text.strip()) < 50:
        try:
            pdf = pdfium.PdfDocument(pdf_bytes)
            for i in range(len(pdf)):
                page = pdf[i]
                bitmap = page.render(scale=2).to_pil()
                page_text, _ = extract_text_from_image(bitmap)
                extracted_text += page_text + "\n"
        except Exception as e:
            st.error(f"PDF OCR failed: {e}")

    return extracted_text


uploaded_files = st.file_uploader(
    "Upload Question Papers",
    type=["png", "jpg", "jpeg", "pdf"],
    accept_multiple_files=True
)

if uploaded_files and subject:
    db = SessionLocal()
    all_questions = []

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name.lower()

        if file_name.endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(uploaded_file).convert("RGB")
            text, processed = extract_text_from_image(image)
            questions = split_into_questions(text)
            all_questions.extend(questions)

            paper = UploadedPaper(
                subject=subject,
                exam_name=exam_name,
                year=year,
                file_name=uploaded_file.name,
                extracted_text=text
            )
            db.add(paper)

            col1, col2 = st.columns(2)
            with col1:
                st.image(image, caption=f"Original - {uploaded_file.name}", use_container_width=True)
            with col2:
                st.image(processed, caption=f"Processed - {uploaded_file.name}", use_container_width=True)

            with st.expander(f"Extracted Text - {uploaded_file.name}"):
                st.text(text)

        elif file_name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
            questions = split_into_questions(text)
            all_questions.extend(questions)

            paper = UploadedPaper(
                subject=subject,
                exam_name=exam_name,
                year=year,
                file_name=uploaded_file.name,
                extracted_text=text
            )
            db.add(paper)

            st.success(f"Processed PDF: {uploaded_file.name}")
            with st.expander(f"Extracted Text - {uploaded_file.name}"):
                st.text(text)

    db.commit()

    if all_questions:
        st.subheader("Extracted Questions")
        questions_df = pd.DataFrame({"Question": all_questions})
        st.dataframe(questions_df, use_container_width=True)

        groups = group_similar_questions(all_questions, threshold=similarity_threshold)
        ranked = rank_predictions(groups)

        keyword_series = extract_keywords(all_questions, top_n=20)

        enriched_predictions = []
        for q, score in ranked:
            topic = infer_topic(q, keyword_series)
            enriched_predictions.append((q, score, topic))

            pred = PredictedQuestion(subject=subject, question=q, score=score, topic=topic)
            db.add(pred)

        db.commit()

        pred_df = pd.DataFrame(
            enriched_predictions,
            columns=["Predicted Question", "Score", "Topic"]
        )
        pred_df.insert(0, "Rank", range(1, len(pred_df) + 1))

        st.subheader("Predicted High-Probability Questions")
        st.dataframe(pred_df.head(top_n), use_container_width=True)

        st.subheader("Top Topics")
        if not keyword_series.empty:
            st.bar_chart(keyword_series)

        csv = pred_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV Report",
            csv,
            file_name=f"{subject}_predictions.csv",
            mime="text/csv"
        )

        pdf_path = os.path.join(EXPORT_DIR, f"{subject}_prediction_report.pdf")
        create_pdf_report(pdf_path, subject, enriched_predictions[:top_n])

        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download PDF Report",
                data=f,
                file_name=f"{subject}_prediction_report.pdf",
                mime="application/pdf"
            )

    else:
        st.warning("No valid questions could be extracted from uploaded files.")

    db.close()
else:
    st.info("Enter subject name and upload one or more image/PDF question papers.")