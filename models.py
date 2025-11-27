from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    dob = Column(String)
    gender = Column(String)
    medical_history = Column(Text)
    
    # Lifestyle
    activity_level = Column(String)
    diet_type = Column(String)
    alcohol_freq = Column(String)
    smoking_status = Column(String)
    sleep_hours = Column(Float)
    
    current_context = Column(Text, nullable=True)
    ai_analysis_consent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PatientReport(Base):
    __tablename__ = "patient_reports"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # NEW: Lab Name
    lab_name = Column(String, nullable=True) 
    
    patient_name = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    report_date = Column(String, nullable=True)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("patient_reports.id"))
    test_name = Column(String, index=True)
    value = Column(Float)
    unit = Column(String)
    min_ref = Column(Float, nullable=True)
    max_ref = Column(Float, nullable=True)
    confidence_score = Column(Integer)
    ai_model_used = Column(String)