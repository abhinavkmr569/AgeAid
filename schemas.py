from pydantic import BaseModel, Field, EmailStr, field_validator
import re
from typing import List, Optional, Union

# --- SHARED VALIDATORS ---
def validate_password_strength(v: str) -> str:
    """
    Enforces strong password policy:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character (!@#$%^&* etc)
    """
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', v):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', v):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', v):
        raise ValueError('Password must contain at least one number')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        raise ValueError('Password must contain at least one special character')
    return v

class BloodTestItem(BaseModel):
    test_name: str = Field(..., description="Standardized name")
    value: Union[float, str] = Field(..., description="Value") # <--- Allow Strings!
    unit: str = Field("Unknown", description="Unit")
    min_ref: Optional[float] = Field(None)
    max_ref: Optional[float] = Field(None)
    confidence_score: int = Field(..., description="0-100 score")

class ExtractionResult(BaseModel):
    lab_name: Optional[str] = Field(None, description="Name of the Laboratory (e.g. Apollo, Thyrocare)")
    patient_name: Optional[str] = Field(None)
    birth_date: Optional[str] = Field(None)
    report_date: Optional[str] = Field(None)
    results: List[BloodTestItem]

# --- AUTH ---
class UserCreate(BaseModel):
    email: EmailStr  # <--- Validates email format automatically
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    dob: str
    gender: str
    medical_history: Optional[str] = None
    activity_level: str
    diet_type: str
    alcohol_freq: str
    smoking_status: str
    sleep_hours: float = Field(..., ge=0, le=24) # 0-24 hours validation
    ai_consent: bool

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password_strength(v)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UpdateContext(BaseModel):
    remarks: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
