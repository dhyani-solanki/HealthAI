# ============================================================
#  schemas/report_insight_schema.py  — Pydantic schemas only
# ============================================================

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ParameterOut(BaseModel):
    name: str
    value: str
    unit: str = ""
    status: str = "normal"         # "normal" | "borderline" | "high" | "low"
    normal_range: str = ""


class DataInsightReportOut(BaseModel):
    id: int
    file_name: str
    report_type: str
    report_label: Optional[str] = None
    confidence: Optional[str] = None
    parameters: Optional[List[ParameterOut]] = None
    upload_date: datetime
    status: str

    class Config:
        from_attributes = True


class CompareRequest(BaseModel):
    report_id_1: int
    report_id_2: int


class ReportInfoCard(BaseModel):
    key: str
    label: str
    icon: str
    short_desc: str
    what_it_measures: str
    why_important: str
    normal_ranges: List[Dict[str, str]]
    conditions_detected: List[str]
