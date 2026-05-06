from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


# ============================================================
#  AUTH SCHEMAS
# ============================================================
class UserSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_name: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None


# ============================================================
#  MEDIGENIUS SCHEMAS
# ============================================================
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str
    source: str = "Unknown"
    timestamp: datetime
    session_id: Optional[int] = None


class ChatHistoryItem(BaseModel):
    id: int
    role: str
    content: str
    source: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatSessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================
#  MEDISCAN SCHEMAS
# ============================================================
class MediScanRequest(BaseModel):
    medicine_name: str


class MediScanResponse(BaseModel):
    id: int
    medicine_name: str
    scan_result: str
    scanned_at: datetime
    image_data: Optional[str] = None

    class Config:
        from_attributes = True

class MediScanImageResponse(BaseModel):
    id: int
    medicine_name: str
    scan_result: str
    scanned_at: datetime
    image_data: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================
#  HEALTH RECORDS SCHEMAS
# ============================================================
class HealthRecordCreate(BaseModel):
    record_type: str
    title: str
    description: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    record_date: date


class HealthRecordOut(BaseModel):
    id: int
    record_type: str
    title: str
    description: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    record_date: date
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
#  FAMILY HISTORY SCHEMAS
# ============================================================
class FamilyHistoryCreate(BaseModel):
    relation: str
    condition: str
    diagnosis_age: Optional[int] = None
    notes: Optional[str] = None
    is_alive: bool = True


class FamilyHistoryOut(BaseModel):
    id: int
    relation: str
    condition: str
    diagnosis_age: Optional[int] = None
    notes: Optional[str] = None
    is_alive: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
#  REMINDERS SCHEMAS
# ============================================================
class ReminderCreate(BaseModel):
    whatsapp_number: Optional[str] = None
    title: str
    description: Optional[str] = None
    reminder_type: str  # "medicine" or "report"
    reminder_time: datetime
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", "monthly"


class ReminderOut(BaseModel):
    id: int
    whatsapp_number: Optional[str] = None
    title: str
    description: Optional[str] = None
    reminder_type: str
    reminder_time: datetime
    is_recurring: bool
    recurrence_pattern: Optional[str] = None
    is_active: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReminderUpdate(BaseModel):
    whatsapp_number: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_time: Optional[datetime] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None


class WhatsAppNumberInput(BaseModel):
    whatsapp_number: str


class PhoneNumberInput(BaseModel):
    phone_number: str


class VerifyCodeInput(BaseModel):
    phone_number: str
    code: str


class PhoneVerificationStatus(BaseModel):
    phone_number: Optional[str] = None
    phone_verified: bool = False


# ============================================================
#  DASHBOARD SCHEMAS
# ============================================================
class DashboardStats(BaseModel):
    total_chats: int
    total_scans: int
    total_records: int
    total_family_conditions: int
    total_family_reports: int
    active_reminders: int
    recent_chats: List[ChatHistoryItem]
    upcoming_reminders: List[ReminderOut]