from sqlalchemy import Column, Integer, String, Text
from models.db import Base

class UploadedPaper(Base):
    __tablename__ = "uploaded_papers"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255))
    exam_name = Column(String(255))
    year = Column(String(50))
    file_name = Column(String(255))
    extracted_text = Column(Text)

class PredictedQuestion(Base):
    __tablename__ = "predicted_questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255))
    question = Column(Text)
    score = Column(Integer)
    topic = Column(String(255))