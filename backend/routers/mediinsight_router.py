# ============================================================
#  routers/mediinsight_router.py
#  FastAPI endpoints — STEP 7 output delivery
#
#  Register in main.py:
#    from routers.mediinsight_router import router as mediinsight_router
#    app.include_router(mediinsight_router)
# ============================================================

import uuid, shutil, logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models import User, LabReport, LabAnalysis, LabComparison
from auth.dependencies import get_current_user
from routers.mediinsight_rag import analyze_report, compare_reports
from routers.mediinsight_config import ALLOWED_TYPES, REJECTED_KW

logger     = logging.getLogger("mediinsight.router")
router     = APIRouter(prefix="/mediinsight", tags=["🧬 MediInsight"])
UPLOAD_DIR = Path("uploads/lab_reports")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def extract_pdf_text(path: Path) -> str:
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extract error: {e}")
        return ""


def _get_report(report_id: int, user_id: int, db: Session) -> dict:
    row = db.execute(text(
        "SELECT id, user_id, report_type, file_name, "
        "COALESCE(extracted_text,'') AS extracted_text, "
        "upload_date, COALESCE(status,'pending') AS status "
        "FROM lab_reports WHERE id=:rid AND user_id=:uid"
    ), {"rid": report_id, "uid": user_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"id":row[0],"user_id":row[1],"report_type":row[2],
            "file_name":row[3],"extracted_text":row[4],
            "upload_date":row[5],"status":row[6]}


def _upsert_analysis(db: Session, report_id: int, result: dict):
    analysis = db.query(LabAnalysis).filter(LabAnalysis.report_id==report_id).first()
    kp_data  = {
        "parameters":  result.get("parameters", []),
        "chart_data":  result.get("chart_data", []),
        "disclaimer":  result.get("disclaimer", ""),
        "tavily_used": result.get("tavily_used", False),
    }
    if analysis:
        analysis.summary        = result.get("summary")
        analysis.key_parameters = kp_data
        analysis.rag_chunks_used= [{"source": s} for s in result.get("scraped_sources", [])]
    else:
        db.add(LabAnalysis(
            report_id       = report_id,
            summary         = result.get("summary"),
            key_parameters  = kp_data,
            rag_chunks_used = [{"source": s} for s in result.get("scraped_sources", [])],
        ))
    db.commit()


def _mark_processed(report_id: int, db: Session):
    db.execute(text("UPDATE lab_reports SET status='processed' WHERE id=:rid"), {"rid": report_id})
    db.commit()


# ═══ 0. API KEYS STATUS ═══════════════════════════════════════
@router.get("/keys/status", summary="Check which Gemini API keys are configured")
def keys_status(current_user: User = Depends(get_current_user)):
    """Shows which task-specific keys are set in .env"""
    from routers.mediinsight_gemini import list_configured_keys
    return {
        "message": "Add these keys to backend/.env — each is a separate free Gemini key",
        "keys":    list_configured_keys(),
        "guide": {
            "GEMINI_KEY_EXTRACTION":   "Used for extracting parameters from PDF text",
            "GEMINI_KEY_SUMMARY":      "Used for generating overall summary",
            "GEMINI_KEY_SIGNIFICANCE": "Used for per-parameter clinical notes",
            "GEMINI_KEY_COMPARISON":   "Used for comparing two reports",
            "GEMINI_API_KEY":          "Master fallback key",
        },
        "quota_per_key": "20 requests/day, 5 requests/minute (free tier)",
        "get_keys_at":   "https://aistudio.google.com/apikey → Create API key in new project",
    }


# ═══ 1. UPLOAD ════════════════════════════════════════════════
@router.post("/upload", summary="Upload a lab report PDF or TXT")
async def upload_report(
    file:        UploadFile    = File(...),
    report_type: str           = Form(...),
    whose:       str           = Form("Myself"),
    relation:    Optional[str] = Form(None),
    gender:      Optional[str] = Form("general"),
    db:          Session       = Depends(get_db),
    current_user:User          = Depends(get_current_user),
):
    if report_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"'{report_type}' is not a supported lab report type.")

    fname = file.filename or "report.pdf"
    if not fname.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF or TXT files accepted.")

    file_path = UPLOAD_DIR / f"{uuid.uuid4()}_{fname}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    extracted = (extract_pdf_text(file_path) if fname.lower().endswith(".pdf")
                 else file_path.read_text(encoding="utf-8", errors="ignore"))

    if any(kw in extracted.lower() for kw in REJECTED_KW):
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Imaging reports are not accepted.")

    record = LabReport(
        user_id=current_user.id, report_type=report_type,
        file_name=fname, extracted_text=extracted, status="pending",
    )
    try:
        record.file_path = str(file_path)
    except Exception:
        pass
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "report_id":   record.id,
        "message":     "Report uploaded successfully.",
        "status":      "pending",
        "whose":       whose,
        "relation":    relation or "",
        "gender":      gender or "general",
    }


# ═══ 2. ANALYZE (full 7-step pipeline) ════════════════════════
@router.post("/{report_id}/analyze", summary="Run full MediInsight analysis pipeline")
def run_analysis(
    report_id:   int,
    whose:       str           = Form("Myself"),
    relation:    Optional[str] = Form(None),
    gender:      Optional[str] = Form("general"),
    db:          Session       = Depends(get_db),
    current_user:User          = Depends(get_current_user),
):
    report = _get_report(report_id, current_user.id, db)
    patient_context = {"whose": whose, "relation": relation or "", "gender": gender or "general"}

    try:
        result = analyze_report(
            report_type     = report["report_type"],
            extracted_text  = report["extracted_text"],
            report_id       = report_id,
            patient_context = patient_context,
            gender          = gender or "general",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        err = str(e).lower()
        if "429" in err or "quota" in err or "rate" in err:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini API rate limit reached (free tier: 20 requests/day). "
                    "Parameters extracted via fallback. "
                    "Wait until midnight PST for quota reset, or get a new API key at https://aistudio.google.com/apikey"
                )
            )
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

    _upsert_analysis(db, report_id, result)
    _mark_processed(report_id, db)
    return result


# ═══ 3. COMPARE ═══════════════════════════════════════════════
@router.post("/compare", summary="Compare two reports of the same type")
def run_comparison(
    current_report_id:  int     = Form(...),
    previous_report_id: int     = Form(...),
    db:                 Session = Depends(get_db),
    current_user:       User    = Depends(get_current_user),
):
    curr_r = _get_report(current_report_id,  current_user.id, db)
    prev_r = _get_report(previous_report_id, current_user.id, db)

    if curr_r["report_type"] != prev_r["report_type"]:
        raise HTTPException(status_code=400, detail="Both reports must be the same type.")

    curr_a = db.query(LabAnalysis).filter(LabAnalysis.report_id==current_report_id).first()
    prev_a = db.query(LabAnalysis).filter(LabAnalysis.report_id==previous_report_id).first()
    if not curr_a or not prev_a:
        raise HTTPException(status_code=400, detail="Analyse both reports first.")

    return compare_reports(
        curr_r["report_type"],
        {"parameters": (curr_a.key_parameters or {}).get("parameters", [])},
        {"parameters": (prev_a.key_parameters or {}).get("parameters", [])},
    )


# ═══ 4. HISTORY ═══════════════════════════════════════════════
@router.get("/history", summary="List all reports for current user")
def get_history(db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    rows = db.execute(text(
        "SELECT id, report_type, file_name, upload_date, COALESCE(status,'pending') "
        "FROM lab_reports WHERE user_id=:uid ORDER BY upload_date DESC"
    ), {"uid": current_user.id}).fetchall()
    return [{"id":r[0],"report_type":r[1],"file_name":r[2],
             "upload_date":r[3].isoformat() if r[3] else "","status":r[4]}
            for r in rows]


# ═══ DEBUG — see raw PDF text & extraction ════════════════════
@router.get("/{report_id}/debug", summary="Debug: see raw text and extraction")
def debug_report(
    report_id:   int,
    db:          Session = Depends(get_db),
    current_user:User    = Depends(get_current_user),
):
    """Returns raw extracted text so you can debug why params are missing."""
    report = _get_report(report_id, current_user.id, db)
    text   = report["extracted_text"] or ""
    lines  = text.split("\n")
    return {
        "report_id":       report_id,
        "report_type":     report["report_type"],
        "text_length":     len(text),
        "line_count":      len(lines),
        "first_50_lines":  lines[:50],
        "full_text":       text[:3000],
    }


# ═══ 6. DELETE REPORT ═════════════════════════════════════════
@router.delete("/{report_id}", summary="Delete a report and its analysis")
def delete_report(
    report_id:   int,
    db:          Session = Depends(get_db),
    current_user:User    = Depends(get_current_user),
):
    # Verify ownership
    row = db.execute(text(
        "SELECT id FROM lab_reports WHERE id=:rid AND user_id=:uid"
    ), {"rid": report_id, "uid": current_user.id}).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found.")

    # Delete analysis first (FK constraint)
    db.execute(text("DELETE FROM lab_analysis WHERE report_id=:rid"), {"rid": report_id})
    db.execute(text("DELETE FROM lab_comparisons WHERE current_report_id=:rid OR previous_report_id=:rid"), {"rid": report_id})
    db.execute(text("DELETE FROM lab_reports WHERE id=:rid"), {"rid": report_id})
    db.commit()

    return {"message": "Report deleted successfully.", "report_id": report_id}
@router.get("/{report_id}/results", summary="Retrieve saved analysis")
def get_results(
    report_id:   int,
    db:          Session = Depends(get_db),
    current_user:User    = Depends(get_current_user),
):
    report   = _get_report(report_id, current_user.id, db)
    analysis = db.query(LabAnalysis).filter(LabAnalysis.report_id==report_id).first()
    kp       = analysis.key_parameters or {} if analysis else {}
    return {
        "report_type":   report["report_type"],
        "file_name":     report["file_name"],
        "summary":       analysis.summary       if analysis else None,
        "parameters":    kp.get("parameters",  []),
        "chart_data":    kp.get("chart_data",   []),
        "tavily_used":   kp.get("tavily_used",  False),
        "disclaimer":    kp.get("disclaimer",   ""),
        "rag_sources":   [s.get("source","") for s in (analysis.rag_chunks_used or [])] if analysis else [],
    }