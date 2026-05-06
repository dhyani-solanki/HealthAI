from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Boolean, Date, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


# ============================================================
#  USER MODEL
# ============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    phone_verified = Column(Boolean, default=False)
    verification_code = Column(String(6), nullable=True)
    verification_code_expires = Column(DateTime, nullable=True)
    whatsapp_number = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    medicine_scans = relationship("MedicineScan", back_populates="user", cascade="all, delete-orphan")
    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete-orphan")
    family_history = relationship("FamilyHistory", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    lab_reports = relationship("LabReport", back_populates="user", cascade="all, delete-orphan")


# ============================================================
#  MEDIGENIUS - Chat Sessions
# ============================================================
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


# ============================================================
#  MEDIGENIUS - Chat Messages
# ============================================================
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    source = Column(String(50), nullable=True)  # "RAG", "LLM", "Wikipedia", "Tavily"
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")
    session = relationship("ChatSession", back_populates="messages")


# ============================================================
#  MEDISCAN - Medicine Scans
# ============================================================
class MedicineScan(Base):
    __tablename__ = "medicine_scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    scan_result = Column(Text, nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow)
    image_data = Column(Text, nullable=True)  # Base64 encoded image

    user = relationship("User", back_populates="medicine_scans")


# ============================================================
#  HEALTH RECORDS
# ============================================================
class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_type = Column(String(100), nullable=False)  # "blood_test", "xray", "prescription", etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    doctor_name = Column(String(100), nullable=True)
    hospital_name = Column(String(200), nullable=True)
    record_date = Column(Date, nullable=False)
    file_path = Column(String(500), nullable=True)  # optional file upload path
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="health_records")


# ============================================================
#  FAMILY HISTORY
# ============================================================
class FamilyHistory(Base):
    __tablename__ = "family_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    relation = Column(String(50), nullable=False)  # "father", "mother", "sibling", etc.
    condition = Column(String(255), nullable=False)  # "diabetes", "hypertension", etc.
    diagnosis_age = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    is_alive = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="family_history")


# ============================================================
#  REMINDERS
# ============================================================
class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_number = Column(String(20), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    reminder_type = Column(String(50), nullable=False)  # "medicine", "appointment", "checkup"
    reminder_time = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50), nullable=True)  # "daily", "weekly", "monthly"
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="pending")  # "pending", "sent", "failed"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reminders")

from sqlalchemy import JSON
 
 
# ============================================================
#  MEDIINSIGHT – Lab Reports
# ============================================================
class LabReport(Base):
    __tablename__ = "lab_reports"
 
    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type    = Column(String(100), nullable=False)
    file_name      = Column(String(255), nullable=False)
    file_path      = Column(String(500), nullable=True)
    extracted_text = Column(Text, nullable=True)
    report_date    = Column(Date, nullable=True)
    upload_date    = Column(DateTime, default=datetime.utcnow)
    status         = Column(String(50), default="pending")  # pending | processed | failed
 
    user                    = relationship("User", back_populates="lab_reports")
    analysis                = relationship("LabAnalysis", back_populates="report",
                                           uselist=False, cascade="all, delete-orphan")
    comparisons_as_current  = relationship("LabComparison",
                                           foreign_keys="LabComparison.current_report_id",
                                           back_populates="current_report",
                                           cascade="all, delete-orphan")
    comparisons_as_previous = relationship("LabComparison",
                                           foreign_keys="LabComparison.previous_report_id",
                                           back_populates="previous_report")
 
 
# ============================================================
#  MEDIINSIGHT – AI Analysis Results (stored as JSON)
# ============================================================
class LabAnalysis(Base):
    __tablename__ = "lab_analysis"
 
    id             = Column(Integer, primary_key=True, index=True)
    report_id      = Column(Integer, ForeignKey("lab_reports.id"), unique=True, nullable=False)
    summary        = Column(JSON, nullable=True)        # {report_type, date, overall_summary, abnormal_findings[], possible_causes[]}
    key_parameters = Column(JSON, nullable=True)        # {parameters:[{name,value,normal_range,status,significance,source_url}]}
    rag_chunks_used= Column(JSON, nullable=True)        # [{text, source, url}]  — what RAG context was retrieved
    created_at     = Column(DateTime, default=datetime.utcnow)
 
    report = relationship("LabReport", back_populates="analysis")
 
 
# ============================================================
#  MEDIINSIGHT – Comparison Between Two Reports
# ============================================================
class LabComparison(Base):
    __tablename__ = "lab_comparisons"
 
    id                 = Column(Integer, primary_key=True, index=True)
    user_id            = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type        = Column(String(100), nullable=False)
    current_report_id  = Column(Integer, ForeignKey("lab_reports.id"), nullable=False)
    previous_report_id = Column(Integer, ForeignKey("lab_reports.id"), nullable=False)
    comparison_result  = Column(JSON, nullable=True)   # {comparisons:[{parameter,previous,current,trend,interpretation}]}
    created_at         = Column(DateTime, default=datetime.utcnow)
 
    user            = relationship("User")
    current_report  = relationship("LabReport", foreign_keys=[current_report_id],
                                   back_populates="comparisons_as_current")
    previous_report = relationship("LabReport", foreign_keys=[previous_report_id],
                                   back_populates="comparisons_as_previous")
 
 
# ============================================================
#  MEDIINSIGHT – RAG Knowledge Base (scraped content cache)
# ============================================================
class MedicalKnowledgeCache(Base):
    __tablename__ = "medical_knowledge_cache"
 
    id           = Column(Integer, primary_key=True, index=True)
    topic        = Column(String(200), nullable=False, index=True)  # e.g. "CBC hemoglobin"
    source_name  = Column(String(200), nullable=False)              # "MedlinePlus", "WHO", etc.
    source_url   = Column(String(500), nullable=False)
    content      = Column(Text, nullable=False)                     # scraped text chunk
    scraped_at   = Column(DateTime, default=datetime.utcnow)
    is_active    = Column(Boolean, default=True)
 