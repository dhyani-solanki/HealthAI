# ============================================================
#  routers/data_insights.py
#  ALL new endpoints prefixed /data-insights/
#  Register in main.py with ONE line:
#    from routers.data_insights import router as data_insights_router
#    app.include_router(data_insights_router)
# ============================================================

import uuid
import shutil
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth.dependencies import get_current_user
from models import User   # existing User model (unchanged)

# ── Import the NEW model so its table is created on startup ──
from models.report_insight_model import DataInsightReport

# ── Services ─────────────────────────────────────────────────
from services.pdf_extractor   import extract_text
from services.report_detector import detect_report_type, extract_parameters
from services.ai_analysis     import stream_analysis, stream_comparison, build_delta_comparison
from services.report_info_cache import get_all_report_info, get_report_info_by_key

logger     = logging.getLogger("data_insights.router")
router     = APIRouter(prefix="/data-insights", tags=["📊 Data Insights"])
UPLOAD_DIR = Path("uploads/data_insights")
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
#  1. GET /data-insights/report-info
#     Returns the educational info cards for all 9 report types
# ─────────────────────────────────────────────────────────────
@router.get("/report-info", summary="Get educational info for all report types")
def get_report_info(current_user: User = Depends(get_current_user)):
    """Returns pre-fetched info cards for all supported report types."""
    return get_all_report_info()


@router.get("/report-info/{key}", summary="Get info for a specific report type")
def get_report_info_key(key: str, current_user: User = Depends(get_current_user)):
    info = get_report_info_by_key(key)
    if not info:
        raise HTTPException(status_code=404, detail=f"No info for report type '{key}'.")
    return info


# ─────────────────────────────────────────────────────────────
#  2. POST /data-insights/upload
#     Upload PDF → extract text → detect type → save → return
# ─────────────────────────────────────────────────────────────
@router.post("/upload", summary="Upload a health report PDF and auto-detect type")
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    fname = file.filename
    ext   = Path(fname).suffix.lower()
    if ext not in (".pdf", ".txt"):
        raise HTTPException(status_code=400, detail="Only PDF or TXT files are accepted.")

    # Save file
    save_path = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    finally:
        await file.close()

    # Extract text
    extracted_text = extract_text(save_path)
    if not extracted_text:
        save_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from the file. Ensure it is a readable PDF."
        )

    # Detect report type
    report_key, report_label, report_icon, confidence = detect_report_type(extracted_text)

    # Extract parameters
    parameters = extract_parameters(extracted_text, report_key)

    # Save to DB
    record = DataInsightReport(
        user_id        = current_user.id,
        file_name      = fname,
        file_path      = str(save_path),
        report_type    = report_key,
        report_label   = report_label,
        confidence     = confidence,
        extracted_text = extracted_text[:50000],   # cap stored text
        parameters     = parameters,
        status         = "analysed" if parameters else "uploaded",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "report_id":    record.id,
        "report_type":  report_key,
        "report_label": report_label,
        "report_icon":  report_icon,
        "confidence":   confidence,
        "parameters":   parameters,
        "status":       record.status,
        "message":      "Report uploaded and processed successfully.",
    }


# ─────────────────────────────────────────────────────────────
#  3. GET /data-insights/reports/{report_id}/analysis  (SSE)
#     Stream AI health insight for a saved report
# ─────────────────────────────────────────────────────────────
@router.get("/reports/{report_id}/analysis", summary="Stream AI analysis via SSE")
def stream_report_analysis(
    report_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    report = _get_report_or_404(report_id, current_user.id, db)
    params = report.parameters or []
    label  = report.report_label or report.report_type

    if not params:
        raise HTTPException(
            status_code=400,
            detail="No parameters found in this report. Upload a richer PDF."
        )

    def sse_generator():
        yield "data: [START]\n\n"
        for chunk in stream_analysis(label, params):
            # SSE format: each data line
            safe_chunk = chunk.replace("\n", " ")
            yield f"data: {safe_chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ─────────────────────────────────────────────────────────────
#  4. POST /data-insights/reports/compare  (SSE)
#     Compare two reports of the same type
# ─────────────────────────────────────────────────────────────
@router.post("/reports/compare", summary="Compare two reports and stream AI summary")
def compare_reports_endpoint(
    report_id_1:  int,
    report_id_2:  int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    r1 = _get_report_or_404(report_id_1, current_user.id, db)
    r2 = _get_report_or_404(report_id_2, current_user.id, db)

    if r1.report_type != r2.report_type:
        raise HTTPException(
            status_code=400,
            detail="Both reports must be the same type to compare."
        )

    # Determine older / newer by upload_date
    if r1.upload_date <= r2.upload_date:
        older, newer = r1, r2
    else:
        older, newer = r2, r1

    older_params = older.parameters or []
    newer_params = newer.parameters or []
    label        = newer.report_label or newer.report_type

    # Build delta data (non-streaming JSON)
    deltas = build_delta_comparison(older_params, newer_params)

    # SSE stream for AI summary
    def sse_generator():
        # First yield the delta JSON as a special SSE event
        yield f"data: [DELTA]{json.dumps(deltas)}\n\n"
        yield "data: [START]\n\n"
        for chunk in stream_comparison(label, older_params, newer_params):
            safe_chunk = chunk.replace("\n", " ")
            yield f"data: {safe_chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ─────────────────────────────────────────────────────────────
#  5. GET /data-insights/reports  — list user's reports
# ─────────────────────────────────────────────────────────────
@router.get("/reports", summary="List all uploaded reports for current user")
def list_reports(
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    reports = (
        db.query(DataInsightReport)
        .filter(DataInsightReport.user_id == current_user.id)
        .order_by(DataInsightReport.upload_date.desc())
        .all()
    )
    return [
        {
            "id":           r.id,
            "file_name":    r.file_name,
            "report_type":  r.report_type,
            "report_label": r.report_label,
            "confidence":   r.confidence,
            "parameters":   r.parameters or [],
            "upload_date":  r.upload_date.isoformat() if r.upload_date else "",
            "status":       r.status,
        }
        for r in reports
    ]


# ─────────────────────────────────────────────────────────────
#  6. GET /data-insights/reports/{report_id}  — single report
# ─────────────────────────────────────────────────────────────
@router.get("/reports/{report_id}", summary="Get a single report's details")
def get_report(
    report_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    r = _get_report_or_404(report_id, current_user.id, db)
    return {
        "id":           r.id,
        "file_name":    r.file_name,
        "report_type":  r.report_type,
        "report_label": r.report_label,
        "confidence":   r.confidence,
        "parameters":   r.parameters or [],
        "upload_date":  r.upload_date.isoformat() if r.upload_date else "",
        "status":       r.status,
    }


# ─────────────────────────────────────────────────────────────
#  7. POST /data-insights/reports/{report_id}/reanalyze
#     Re-run extraction on an already-saved file (fixes old bad params)
# ─────────────────────────────────────────────────────────────
@router.post("/reports/{report_id}/reanalyze", summary="Re-run parameter extraction on a saved report")
def reanalyze_report(
    report_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    report = _get_report_or_404(report_id, current_user.id, db)

    if not report.extracted_text:
        # Try re-extracting from file on disk
        if report.file_path and Path(report.file_path).exists():
            new_text = extract_text(report.file_path)
            if new_text:
                report.extracted_text = new_text[:50000]
        if not report.extracted_text:
            raise HTTPException(status_code=400, detail="No text available to re-analyze.")

    # Re-detect and re-extract
    report_key, report_label, report_icon, confidence = detect_report_type(report.extracted_text)
    parameters = extract_parameters(report.extracted_text, report_key)

    report.report_type  = report_key
    report.report_label = report_label
    report.confidence   = confidence
    report.parameters   = parameters
    report.status       = "analysed" if parameters else "uploaded"
    db.commit()
    db.refresh(report)

    return {
        "report_id":    report.id,
        "report_type":  report_key,
        "report_label": report_label,
        "report_icon":  report_icon,
        "confidence":   confidence,
        "parameters":   parameters,
        "status":       report.status,
        "message":      f"Re-analyzed: {len(parameters)} parameters extracted.",
    }


# ─────────────────────────────────────────────────────────────
#  8. DELETE /data-insights/reports/{report_id}
# ─────────────────────────────────────────────────────────────
@router.delete("/reports/{report_id}", summary="Delete a report")
def delete_report(
    report_id:    int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    report = _get_report_or_404(report_id, current_user.id, db)

    # Delete file from disk
    if report.file_path:
        Path(report.file_path).unlink(missing_ok=True)

    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully.", "report_id": report_id}
