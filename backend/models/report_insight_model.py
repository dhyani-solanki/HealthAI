# ============================================================
#  models/report_insight_model.py
#  NEW table only — do NOT modify models.py
#  Import this module so SQLAlchemy registers the table with
#  the same Base used by the rest of the app.
# ============================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base          # shared Base from database.py


class DataInsightReport(Base):
    """Stores user-uploaded health reports for the Data Insights module."""
    __tablename__ = "data_insight_reports"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name      = Column(String(255), nullable=False)
    file_path      = Column(String(500), nullable=True)
    report_type    = Column(String(100), nullable=False)   # e.g. "lipid_profile"
    report_label   = Column(String(200), nullable=True)    # human-readable label
    confidence     = Column(String(20), nullable=True)     # "high" / "medium" / "low"
    extracted_text = Column(Text, nullable=True)
    parameters     = Column(JSON, nullable=True)           # [{name, value, unit, status, normal_range}]
    owner_type     = Column(String(50), default="myself")  # myself | family | others
    owner_name     = Column(String(255), nullable=True)    # e.g. "Father", "Mother", custom name
    summary        = Column(Text, nullable=True)           # AI-generated summary text
    upload_date    = Column(DateTime, default=datetime.utcnow)
    status         = Column(String(50), default="uploaded") # uploaded | analysed | failed

    # Relationship back to User (no back_populates — we don't modify models.py)
    user = relationship("User", foreign_keys=[user_id])
