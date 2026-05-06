# ============================================================
#  routers/medreport_router.py
#  MedReport Analyzer — integrated into Data Insights module.
#  Upload → Classify → Extract → Summary pipeline.
#  Uses MEDREPORT_GEMINI_API_KEY and MEDREPORT_TAVILY_API_KEY.
# ============================================================

import uuid
import shutil
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import date, datetime

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from models import User, HealthRecord
from models.report_insight_model import DataInsightReport

from services.medreport_pdf_service import extract_text_from_pdf
from services.medreport_gemini_service import classify_report, extract_parameters, generate_summary

logger = logging.getLogger("medreport.router")
router = APIRouter(prefix="/medreport", tags=["🏥 MedReport Analyzer"])
UPLOAD_DIR = Path("uploads/medreports")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────────────────────
def _get_report_or_404(report_id: int, user_id: int, db: Session) -> DataInsightReport:
    report = (
        db.query(DataInsightReport)
        .filter(DataInsightReport.id == report_id, DataInsightReport.user_id == user_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


# ─────────────────────────────────────────────────────────────
#  1. POST /medreport/upload
#     Upload PDF → extract text → classify → extract params → summary → save
#     Full pipeline in one call (like reference project)
# ─────────────────────────────────────────────────────────────
@router.post("/upload", summary="Upload medical report with owner info")
async def upload_medreport(
    file: UploadFile = File(...),
    owner_type: str = Form(default="myself"),
    owner_name: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Validate owner_type
    if owner_type not in ("myself", "family", "others"):
        raise HTTPException(status_code=400, detail="owner_type must be 'myself', 'family', or 'others'.")

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 20MB limit.")

    # Save file to disk
    save_path = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    # Step 1: Extract text from PDF
    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")

    # Step 2: Classify report type
    classification = classify_report(raw_text)
    report_type = classification["report_type"]
    confidence = classification["confidence"]

    # Step 3: Extract parameters
    try:
        parameters = extract_parameters(raw_text, report_type)
    except ValueError as e:
        parameters = []
        logger.warning(f"Parameter extraction warning: {e}")

    # Step 4: Generate summary
    summary_text = ""
    if parameters:
        try:
            summary_text = generate_summary(report_type, parameters)
        except Exception as e:
            logger.warning(f"Summary generation warning: {e}")

    # Step 5: Convert parameters to the format DataInsightReport expects
    di_parameters = []
    for p in parameters:
        normal_range_str = ""
        if p.get("normal_min") is not None and p.get("normal_max") is not None:
            normal_range_str = f"{p['normal_min']} - {p['normal_max']}"
        di_parameters.append({
            "name": p["name"],
            "value": p["value"],
            "unit": p.get("unit", ""),
            "status": p.get("status", "normal"),
            "normal_range": normal_range_str,
            "normal_min": p.get("normal_min"),
            "normal_max": p.get("normal_max"),
            "source": p.get("source", ""),
            "insight": p.get("insight", ""),
        })

    # Step 6: Save to DataInsightReport
    record = DataInsightReport(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=str(save_path),
        report_type=report_type.lower().replace(" ", "_").replace("/", "_"),
        report_label=report_type,
        confidence=confidence,
        extracted_text=raw_text[:50000],
        parameters=di_parameters,
        owner_type=owner_type,
        owner_name=owner_name,
        summary=summary_text,
        status="analysed" if parameters else "uploaded",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Step 7: If owner_type == "myself", also create a HealthRecord
    health_record_id = None
    if owner_type == "myself":
        param_summary = ", ".join(
            f"{p['name']}: {p['value']} {p['unit']} ({p['status']})"
            for p in di_parameters[:5]
        )
        description = f"AI-analyzed report: {report_type}\n"
        if param_summary:
            description += f"Key parameters: {param_summary}\n"
        if summary_text:
            description += f"\n{summary_text[:500]}"

        health_record = HealthRecord(
            user_id=current_user.id,
            record_type="lab_report",
            title=f"{report_type} - {file.filename}",
            description=description,
            record_date=date.today(),
        )
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
        health_record_id = health_record.id

    return {
        "report_id": record.id,
        "report_type": report_type,
        "report_label": report_type,
        "confidence": confidence,
        "classification_reasoning": classification.get("reasoning", ""),
        "parameters": di_parameters,
        "summary": summary_text,
        "owner_type": owner_type,
        "owner_name": owner_name,
        "health_record_id": health_record_id,
        "status": record.status,
        "message": f"Report uploaded and analysed. {len(parameters)} parameters extracted.",
    }


# ─────────────────────────────────────────────────────────────
#  STEP A: POST /medreport/classify — upload PDF + classify only (1 AI call)
# ─────────────────────────────────────────────────────────────
@router.post("/classify", summary="Upload PDF, extract text, classify report type")
async def classify_medreport(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 20MB limit.")

    save_path = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    try:
        raw_text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")

    classification = classify_report(raw_text)

    return {
        "file_name": file.filename,
        "file_path": str(save_path),
        "raw_text": raw_text[:50000],
        "report_type": classification["report_type"],
        "report_label": classification["report_type"],
        "confidence": classification["confidence"],
        "classification_reasoning": classification.get("reasoning", ""),
    }


# ─────────────────────────────────────────────────────────────
#  STEP B: POST /medreport/extract-params — extract parameters (1 AI call)
# ─────────────────────────────────────────────────────────────
@router.post("/extract-params", summary="Extract clinical parameters from report text")
def extract_params_endpoint(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_text = data.get("raw_text", "")
    report_type = data.get("report_type", "Unknown / Other")

    if not raw_text:
        raise HTTPException(status_code=400, detail="raw_text is required.")

    try:
        parameters = extract_parameters(raw_text, report_type)
    except ValueError as e:
        parameters = []
        logger.warning(f"Parameter extraction warning: {e}")

    di_parameters = []
    for p in parameters:
        normal_range_str = ""
        if p.get("normal_min") is not None and p.get("normal_max") is not None:
            normal_range_str = f"{p['normal_min']} - {p['normal_max']}"
        di_parameters.append({
            "name": p["name"],
            "value": p["value"],
            "unit": p.get("unit", ""),
            "status": p.get("status", "normal"),
            "normal_range": normal_range_str,
            "normal_min": p.get("normal_min"),
            "normal_max": p.get("normal_max"),
            "source": p.get("source", ""),
            "insight": p.get("insight", ""),
        })

    return {
        "parameters": di_parameters,
        "param_count": len(di_parameters),
    }


# ─────────────────────────────────────────────────────────────
#  STEP C: POST /medreport/generate-summary — generate summary (1 AI call)
# ─────────────────────────────────────────────────────────────
@router.post("/generate-summary", summary="Generate AI summary from parameters")
def generate_summary_endpoint(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report_type = data.get("report_type", "Unknown")
    parameters = data.get("parameters", [])

    if not parameters:
        return {"summary": ""}

    try:
        summary_text = generate_summary(report_type, parameters)
    except Exception as e:
        logger.warning(f"Summary generation warning: {e}")
        summary_text = ""

    return {"summary": summary_text}


# ─────────────────────────────────────────────────────────────
#  1c. POST /medreport/save — save an analyzed report to DB
# ─────────────────────────────────────────────────────────────
@router.post("/save", summary="Save an analyzed report to the database")
def save_medreport(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_name = data.get("file_name", "report.pdf")
    file_path = data.get("file_path", "")
    report_type = data.get("report_type", "Unknown")
    report_label = data.get("report_label", report_type)
    confidence = data.get("confidence", "low")
    parameters = data.get("parameters", [])
    summary = data.get("summary", "")
    owner_type = data.get("owner_type", "myself")
    owner_name = data.get("owner_name")

    if owner_type not in ("myself", "family", "others"):
        raise HTTPException(status_code=400, detail="owner_type must be 'myself', 'family', or 'others'.")

    now = datetime.utcnow()

    record = DataInsightReport(
        user_id=current_user.id,
        file_name=file_name,
        file_path=file_path,
        report_type=report_type.lower().replace(" ", "_").replace("/", "_"),
        report_label=report_label,
        confidence=confidence,
        parameters=parameters,
        owner_type=owner_type,
        owner_name=owner_name,
        summary=summary,
        upload_date=now,
        status="analysed" if parameters else "uploaded",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # If "myself", also create a HealthRecord
    health_record_id = None
    if owner_type == "myself":
        param_summary = ", ".join(
            f"{p['name']}: {p['value']} {p['unit']} ({p['status']})"
            for p in parameters[:5]
        )
        description = f"AI-analyzed report: {report_type}\n"
        if param_summary:
            description += f"Key parameters: {param_summary}\n"
        if summary:
            description += f"\n{summary[:500]}"

        health_record = HealthRecord(
            user_id=current_user.id,
            record_type="lab_report",
            title=f"{report_type} - {file_name}",
            description=description,
            record_date=date.today(),
        )
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
        health_record_id = health_record.id

    return {
        "report_id": record.id,
        "health_record_id": health_record_id,
        "saved_at": now.isoformat(),
        "message": f"Report saved successfully with {len(parameters)} parameters.",
    }


# ─────────────────────────────────────────────────────────────
#  2. GET /medreport/reports — list reports filtered by owner
# ─────────────────────────────────────────────────────────────
@router.get("/reports", summary="List medreport reports for current user")
def list_medreports(
    owner_type: Optional[str] = Query(default=None),
    owner_name: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(DataInsightReport)
        .filter(DataInsightReport.user_id == current_user.id)
    )
    # Only filter reports that were uploaded via medreport (they have owner_type set)
    if owner_type:
        query = query.filter(DataInsightReport.owner_type == owner_type)
    if owner_name:
        query = query.filter(DataInsightReport.owner_name == owner_name)

    reports = query.order_by(DataInsightReport.upload_date.desc()).all()

    return [
        {
            "id": r.id,
            "file_name": r.file_name,
            "report_type": r.report_type,
            "report_label": r.report_label,
            "confidence": r.confidence,
            "parameters": r.parameters or [],
            "owner_type": r.owner_type,
            "owner_name": r.owner_name,
            "summary": r.summary,
            "upload_date": r.upload_date.isoformat() if r.upload_date else "",
            "status": r.status,
        }
        for r in reports
    ]


# ─────────────────────────────────────────────────────────────
#  3. GET /medreport/family-reports — family reports grouped by member
# ─────────────────────────────────────────────────────────────
@router.get("/family-reports", summary="Get family reports grouped by member")
def get_family_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = (
        db.query(DataInsightReport)
        .filter(
            DataInsightReport.user_id == current_user.id,
            DataInsightReport.owner_type == "family",
        )
        .order_by(DataInsightReport.upload_date.desc())
        .all()
    )

    # Group by owner_name
    grouped = {}
    for r in reports:
        name = r.owner_name or "Unknown"
        if name not in grouped:
            grouped[name] = []
        grouped[name].append({
            "id": r.id,
            "file_name": r.file_name,
            "report_type": r.report_type,
            "report_label": r.report_label,
            "confidence": r.confidence,
            "parameters": r.parameters or [],
            "summary": r.summary,
            "upload_date": r.upload_date.isoformat() if r.upload_date else "",
            "status": r.status,
        })

    return {
        "family_members": [
            {"name": name, "report_count": len(reps), "reports": reps}
            for name, reps in grouped.items()
        ]
    }


# ─────────────────────────────────────────────────────────────
#  4. GET /medreport/reports/{report_id} — single report detail
# ─────────────────────────────────────────────────────────────
@router.get("/reports/{report_id}", summary="Get a single medreport detail")
def get_medreport(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = _get_report_or_404(report_id, current_user.id, db)
    return {
        "id": r.id,
        "file_name": r.file_name,
        "report_type": r.report_type,
        "report_label": r.report_label,
        "confidence": r.confidence,
        "parameters": r.parameters or [],
        "owner_type": r.owner_type,
        "owner_name": r.owner_name,
        "summary": r.summary,
        "upload_date": r.upload_date.isoformat() if r.upload_date else "",
        "status": r.status,
    }


# ─────────────────────────────────────────────────────────────
#  5. DELETE /medreport/reports/{report_id}
# ─────────────────────────────────────────────────────────────
@router.delete("/reports/{report_id}", summary="Delete a medreport")
def delete_medreport(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_report_or_404(report_id, current_user.id, db)
    if report.file_path:
        Path(report.file_path).unlink(missing_ok=True)
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully.", "report_id": report_id}


# ─────────────────────────────────────────────────────────────
#  6. POST /medreport/reports/bulk-delete
# ─────────────────────────────────────────────────────────────
@router.post("/reports/bulk-delete", summary="Bulk delete medreports")
def bulk_delete_medreports(
    report_ids: list[int] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = 0
    for rid in report_ids:
        report = db.query(DataInsightReport).filter(
            DataInsightReport.id == rid,
            DataInsightReport.user_id == current_user.id,
        ).first()
        if report:
            if report.file_path:
                Path(report.file_path).unlink(missing_ok=True)
            db.delete(report)
            deleted += 1
    db.commit()
    return {"message": f"{deleted} report(s) deleted.", "deleted": deleted}


# ─────────────────────────────────────────────────────────────
#  7. GET /medreport/pdf/{report_id} — serve the original PDF
# ─────────────────────────────────────────────────────────────
@router.get("/pdf/{report_id}", summary="Serve the original uploaded PDF")
def serve_report_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = _get_report_or_404(report_id, current_user.id, db)
    if not report.file_path:
        raise HTTPException(status_code=404, detail="No PDF file associated with this report.")
    pdf_path = Path(report.file_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found on disk.")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=report.file_name or "report.pdf",
    )


# ─────────────────────────────────────────────────────────────
#  8. GET /medreport/pdf-by-path — serve PDF by file_path (for pre-save preview)
# ─────────────────────────────────────────────────────────────
@router.get("/pdf-by-path", summary="Serve PDF by file path (pre-save preview)")
def serve_pdf_by_path(
    file_path: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    pdf_path = Path(file_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found.")
    # Security: only serve files from our upload directory
    try:
        pdf_path.resolve().relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied.")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )
