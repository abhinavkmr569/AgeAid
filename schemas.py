from pydantic import BaseModel, Field
from typing import List, Optional

class BloodTestItem(BaseModel):
    test_name: str = Field(..., description="Standardized name")
    value: float = Field(..., description="Numeric value. Use -1 if unreadable.")
    unit: str = Field("Unknown", description="Unit")
    min_ref: Optional[float] = Field(None, description="Lower bound.")
    max_ref: Optional[float] = Field(None, description="Upper bound.")
    confidence_score: int = Field(..., description="0-100 score")

class ExtractionResult(BaseModel):
    lab_name: Optional[str] = Field(None, description="Name of the Laboratory (e.g. Apollo, Thyrocare)")
    patient_name: Optional[str] = Field(None)
    birth_date: Optional[str] = Field(None)
    report_date: Optional[str] = Field(None)
    results: List[BloodTestItem]

# --- AUTH ---
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    dob: str
    gender: str
    medical_history: str
    activity_level: str
    diet_type: str
    alcohol_freq: str
    smoking_status: str
    sleep_hours: float
    ai_consent: bool

class UserLogin(BaseModel):
    email: str
    password: str

class UpdateContext(BaseModel):
    remarks: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
