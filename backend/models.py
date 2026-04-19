from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    cgpa = Column(Float, nullable=True)
    interests = Column(Text, nullable=True)

    resumes = relationship("Resume", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"
    resume_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    file_path = Column(String)
    parsed_text = Column(Text, nullable=True)
    upload_date = Column(Date, default=datetime.date.today)

    user = relationship("User", back_populates="resumes")

class Prediction(Base):
    __tablename__ = "predictions"
    prediction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    predicted_role = Column(String)
    confidence_score = Column(Float)
    prediction_date = Column(Date, default=datetime.date.today)

    user = relationship("User", back_populates="predictions")
