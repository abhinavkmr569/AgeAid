from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from database import engine, Base, get_db
from models import PatientReport, TestResult, User
# Added UserProfileUpdate to imports
from schemas import UserCreate, UserLogin, UpdateContext, UserProfileUpdate
from extractor import smart_extract, analyze_trend_with_gemini
from passlib.context import CryptContext
from normalizer import normalize_test_name
from utils import standardize_date
from clusters import get_related_tests
from collections import defaultdict
import uvicorn
import logging
import json
from datetime import datetime
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Base.metadata.create_all(bind=engine) # Alembic handles this now
app = FastAPI(title="Health AI")

# --- AUTH ---
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first(): 
        raise HTTPException(400, "Email exists")
    
    empty_log = json.dumps([]) 
    new_user = User(
        email=user.email, hashed_password=pwd_context.hash(user.password),
        full_name=user.full_name, dob=user.dob, gender=user.gender,
        medical_history=user.medical_history, activity_level=user.activity_level,
        diet_type=user.diet_type, alcohol_freq=user.alcohol_freq,
        smoking_status=user.smoking_status, sleep_hours=user.sleep_hours,
        ai_analysis_consent=user.ai_consent,
        current_context=empty_log
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "user_id": new_user.id, "name": new_user.full_name}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password): 
        raise HTTPException(400, "Invalid Credentials")
    return {"status": "success", "user_id": db_user.id, "name": db_user.full_name}

# --- PROFILE & REMARKS ---

@app.get("/user/{user_id}/profile")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    
    try: logs = json.loads(user.current_context) if user.current_context else []
    except: logs = []
    
    # Return logs AND profile details (for the Edit screen)
    return {
        "status": "success", 
        "logs": logs,
        "profile": {
            "email": user.email,
            "full_name": user.full_name,
            "dob": user.dob,
            "gender": user.gender,
            "diet_type": user.diet_type,
            "activity_level": user.activity_level,
            "smoking_status": user.smoking_status,
            "alcohol_freq": user.alcohol_freq,
            "sleep_hours": user.sleep_hours,
            "medical_history": user.medical_history
        }
    }

@app.post("/user/{user_id}/update_remarks")
def update_remarks(user_id: int, payload: UpdateContext, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    try: logs = json.loads(user.current_context) if user.current_context else []
    except: logs = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%Mhrs")
    logs.append({"timestamp": timestamp, "content": payload.remarks})
    user.current_context = json.dumps(logs)
    db.commit()
    return {"status": "success", "logs": logs}

# --- ACCOUNT MANAGEMENT (NEW) ---

@app.delete("/user/{user_id}/delete")
def delete_account(user_id: int, db: Session = Depends(get_db)):
    """
    Permanently deletes user, reports, and test results.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    
    # 1. Find all reports by this user
    reports = db.query(PatientReport).filter(PatientReport.user_id == user_id).all()
    
    # 2. Delete test results for each report
    for r in reports:
        db.query(TestResult).filter(TestResult.report_id == r.id).delete()
        db.delete(r) # Delete the report itself
    
    # 3. Delete the user
    db.delete(user)
    db.commit()
    return {"status": "success", "message": "Account deleted permanently"}

@app.put("/user/{user_id}/update_profile")
def update_profile(user_id: int, payload: UserProfileUpdate, db: Session = Depends(get_db)):
    """
    Updates lifestyle information.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(404, "User not found")
    
    # Only update fields that are provided (not None)
    if payload.diet_type is not None: user.diet_type = payload.diet_type
    if payload.activity_level is not None: user.activity_level = payload.activity_level
    if payload.smoking_status is not None: user.smoking_status = payload.smoking_status
    if payload.alcohol_freq is not None: user.alcohol_freq = payload.alcohol_freq
    if payload.sleep_hours is not None: user.sleep_hours = payload.sleep_hours
    if payload.medical_history is not None: user.medical_history = payload.medical_history
    
    db.commit()
    return {"status": "success", "message": "Profile updated"}

# --- DATA ENDPOINTS ---

@app.post("/analyze")
async def analyze(user_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_bytes = await file.read()
    print(f"📥 Analyzing {file.filename}...")

    try:
        data, model, tokens = smart_extract(file_bytes, file.content_type)
        print(f"🤖 AI Success. Model: {model}, Tokens: {tokens}")
        
        std_date = standardize_date(data.report_date)
        report = PatientReport(
            user_id=user_id, 
            patient_name=data.patient_name, 
            birth_date=data.birth_date, 
            report_date=std_date, 
            lab_name=data.lab_name
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        saved_count = 0
        for r in data.results:
            try:
                clean_value = float(r.value)
            except (ValueError, TypeError):
                print(f"⚠️ Skipping non-numeric result: {r.test_name} = {r.value}")
                continue 

            db.add(TestResult(
                report_id=report.id, 
                test_name=normalize_test_name(r.test_name), 
                value=clean_value,
                unit=r.unit, 
                min_ref=r.min_ref, 
                max_ref=r.max_ref, 
                confidence_score=r.confidence_score, 
                ai_model_used=model,
                tokens_used=tokens
            ))
            saved_count += 1
            
        db.commit()
        print(f"✅ Successfully saved {saved_count} numeric results.")
        return {"status": "success", "data": data}

    except Exception as e:
        print("❌ CRITICAL ERROR IN /ANALYZE:")
        print(traceback.format_exc()) 
        raise HTTPException(500, f"Server Error: {str(e)}")

@app.get("/user/{user_id}/all_tests")
def get_all_tests(user_id: int, db: Session = Depends(get_db)):
    results = db.query(TestResult, PatientReport.report_date, PatientReport.lab_name)\
                .join(PatientReport).filter(PatientReport.user_id == user_id)\
                .order_by(desc(PatientReport.report_date)).all()
    
    return {"status": "success", "data": [{"Date": d, "Test Name": r.test_name, "Value": r.value, "Unit": r.unit, "Reference": f"{r.min_ref}-{r.max_ref}", "Lab": l, "tokens_used": r.tokens_used, "ai_model": r.ai_model_used} for r, d, l in results]}

@app.post("/analyze_trend")
async def get_trend_analysis(user_id: int = Form(...), test_name: str = Form(...), remarks: str = Form(""), start_date: str = Form(None), end_date: str = Form(None), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    std_test_name = normalize_test_name(test_name)
    related_tests = get_related_tests(std_test_name)
    
    query = db.query(TestResult, PatientReport.report_date, PatientReport.lab_name).join(PatientReport).filter(PatientReport.user_id == user_id).filter(TestResult.test_name.in_(related_tests))
    if start_date and end_date: query = query.filter(and_(PatientReport.report_date >= start_date, PatientReport.report_date <= end_date))
    history_query = query.order_by(PatientReport.report_date.asc()).all()
    
    graph_data = []
    ai_history = defaultdict(list)
    for res, date, lab in history_query:
        if res.test_name == std_test_name:
            graph_data.append({"date": date, "value": res.value, "unit": res.unit, "min_ref": res.min_ref, "max_ref": res.max_ref, "lab": lab})
        if date:
            ai_history[str(date)].append({"name": res.test_name, "value": res.value, "unit": res.unit, "min": res.min_ref, "max": res.max_ref, "lab": lab})

    ai_analysis = None
    if user.ai_analysis_consent:
        profile = {"name": user.full_name, "birth_date": user.dob, "gender": user.gender, "medical_history": user.medical_history, "activity": user.activity_level, "diet": user.diet_type, "alcohol": user.alcohol_freq, "smoke": user.smoking_status, "sleep": user.sleep_hours}
        
        try: stored_logs = json.loads(user.current_context) if user.current_context else []
        except: stored_logs = []
        context_str = "\n".join([f"[{log['timestamp']}] {log['content']}" for log in stored_logs])
        
        if remarks: context_str += f"\n[Current Focus] {remarks}"

        try: ai_analysis = analyze_trend_with_gemini(profile, std_test_name, ai_history, context_str)
        except Exception as e: ai_analysis = f"AI Error: {str(e)}"

    return {"history": graph_data, "analysis": ai_analysis}

@app.get("/user/{user_id}/history")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    reports = db.query(PatientReport.id, PatientReport.report_date).filter(PatientReport.user_id == user_id).order_by(desc(PatientReport.report_date)).all()
    return {"status": "success", "reports": [{"id": r.id, "date": r.report_date} for r in reports]}

@app.get("/report/{report_id}")
def get_report_detail(report_id: int, db: Session = Depends(get_db)):
    report = db.query(PatientReport).filter(PatientReport.id == report_id).first()
    results = db.query(TestResult).filter(TestResult.report_id == report.id).all()
    return {"status": "success", "report_date": report.report_date, "lab": report.lab_name, "results": [{"test_name": r.test_name, "value": r.value, "unit": r.unit, "min_ref": r.min_ref, "max_ref": r.max_ref} for r in results]}

@app.get("/user/{user_id}/latest_report")
def get_latest_report(user_id: int, db: Session = Depends(get_db)):
    report = db.query(PatientReport).filter(PatientReport.user_id == user_id).order_by(desc(PatientReport.report_date)).first()
    if not report: return {"status": "empty"}
    return get_report_detail(report.id, db)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)