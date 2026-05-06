from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from database import get_db
from models import User, MedicineScan
from schemas import MediScanRequest, MediScanResponse
from auth.dependencies import get_current_user
from typing import List, Optional
from dotenv import load_dotenv
import traceback
import sys
import os
import base64
from PIL import Image
import io
import google.generativeai as genai

load_dotenv()

# ============================================================
#  MEDISCAN RAG SERVICE
# ============================================================
try:
    from services.mediscan_rag_service import get_mediscan_rag
    RAG_AVAILABLE = True
    print("✅ MediScan RAG service loaded")
except ImportError as e:
    print(f"⚠️ MediScan RAG service not available: {e}")
    RAG_AVAILABLE = False

def call_mediscan(medicine_name: str) -> str:
    """Query medicine information using RAG system"""
    if RAG_AVAILABLE:
        try:
            rag = get_mediscan_rag()
            return rag.generate_medicine_info(medicine_name)
        except Exception as e:
            print(f"❌ RAG error: {e}")
            traceback.print_exc()
    
    # Fallback response
    return (
        f"Medicine Name:\n{medicine_name}\n\n"
        f"Use:\nInformation not available. Please consult a healthcare professional.\n\n"
        f"Dosage:\nAs directed by the Physician.\n\n"
        f"Precautions:\nConsult a doctor before taking any medication.\n\n"
        f"Common Side Effects:\nInformation not available.\n\n"
        f"Disclaimer:\nThis information is for educational purposes only. Consult a doctor before taking any medication."
    )


# ============================================================
#  ROUTER DEFINED FIRST — before any endpoints
# ============================================================
router = APIRouter(prefix="/mediscan", tags=["MediScan"])


# ============================================================
#  ENDPOINTS
# ============================================================

@router.post("/scan", response_model=MediScanResponse)
def scan_medicine_endpoint(
    request: MediScanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Scan/lookup medicine info — protected, per-user"""

    if not request.medicine_name.strip():
        raise HTTPException(status_code=400, detail="Medicine name cannot be empty")

    try:
        result = call_mediscan(request.medicine_name)
    except Exception as e:
        print(f"❌ MediScan error: {e}")
        traceback.print_exc()
        result = "Error retrieving medicine information. Please try again."
    
    scan_record = MedicineScan(
        user_id=current_user.id,
        medicine_name=request.medicine_name,
        scan_result=result,
    )
    db.add(scan_record)
    db.commit()
    db.refresh(scan_record)

    return scan_record


@router.post("/scan-image", response_model=MediScanResponse)
async def scan_medicine_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Scan medicine from uploaded image using Gemini Vision"""

    image_data_base64 = None
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Convert image to base64 for storage
        image_data_base64 = base64.b64encode(contents).decode('utf-8')

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        vision_model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
You are a professional medical assistant.
Step 1: Extract all medicine names visible in the image.
Step 2: If dosage, precautions, or side effects are written in the image, extract them exactly as written.
Step 3: If those details are NOT present in the image, provide general medical information based on your medical knowledge.

Rules:
- Do NOT guess medicine names.
- If medicine name is unclear, say "Not confidently identified".
- Clearly mention whether information is from image or general knowledge.
- Keep response structured.

Format:
Medicine Name:
Source of Information: (Image / General Knowledge)
Use:
Dosage:
Precautions:
Common Side Effects:

Disclaimer: This information is for educational purposes only. Consult a doctor before taking any medication.
"""
        response = vision_model.generate_content([prompt, image])
        result = response.text

        medicine_name = "Image Scan"
        for line in result.split("\n"):
            if line.startswith("Medicine Name:"):
                medicine_name = line.replace("Medicine Name:", "").strip() or "Image Scan"
                break

    except Exception as e:
        print(f"❌ Image scan error: {e}")
        traceback.print_exc()
        result = "Error analyzing image. Please ensure the image is clear and try again."
        medicine_name = "Unknown"

    scan_record = MedicineScan(
        user_id=current_user.id,
        medicine_name=medicine_name,
        scan_result=result,
        image_data=image_data_base64,
    )
    db.add(scan_record)
    db.commit()
    db.refresh(scan_record)

    return scan_record


@router.get("/history", response_model=List[MediScanResponse])
def get_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get medicine scan history for logged-in user"""
    scans = db.query(MedicineScan).filter(
        MedicineScan.user_id == current_user.id
    ).order_by(MedicineScan.scanned_at.desc()).all()
    return scans


@router.delete("/history")
def clear_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.query(MedicineScan).filter(
        MedicineScan.user_id == current_user.id
    ).delete()
    db.commit()
    return {"message": "Scan history cleared"}


@router.delete("/history/{scan_id}")
def delete_scan_item(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a single scan record"""
    scan = db.query(MedicineScan).filter(
        MedicineScan.id == scan_id,
        MedicineScan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    db.delete(scan)
    db.commit()
    return {"message": "Scan deleted"}


@router.get("/suggest")
def suggest_medicines(
    q: str = Query("", description="Partial medicine name for autocomplete"),
    limit: int = Query(10, description="Maximum number of suggestions"),
    current_user: User = Depends(get_current_user)
):
    """Get medicine name suggestions for autocomplete"""
    if not RAG_AVAILABLE:
        return {"suggestions": []}
    
    try:
        rag = get_mediscan_rag()
        suggestions = rag.suggest_medicines(q, limit=limit)
        return {"suggestions": suggestions}
    except Exception as e:
        print(f"❌ Suggestion error: {e}")
        return {"suggestions": []}


@router.post("/ingest-pdf")
async def ingest_medicine_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Ingest a medicine PDF into the RAG vector database"""
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Ingest the PDF
        rag = get_mediscan_rag()
        count = rag.ingest_pdf(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return {"message": f"Successfully ingested {count} medicines from PDF", "count": count}
    
    except Exception as e:
        print(f"❌ PDF ingestion error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to ingest PDF: {str(e)}")


@router.post("/add-medicine")
def add_medicine_to_db(
    medicine_name: str,
    use: Optional[str] = None,
    dosage: Optional[str] = None,
    precautions: Optional[str] = None,
    side_effects: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Manually add a medicine to the RAG vector database"""
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG service not available")
    
    try:
        rag = get_mediscan_rag()
        
        # Build content
        content_parts = []
        if use:
            content_parts.append(f"Use:\n{use}")
        if dosage:
            content_parts.append(f"Dosage:\n{dosage}")
        if precautions:
            content_parts.append(f"Precautions:\n{precautions}")
        if side_effects:
            content_parts.append(f"Common Side Effects:\n{side_effects}")
        
        content = "\n\n".join(content_parts) if content_parts else "No detailed information available."
        
        rag.add_medicine_document(medicine_name, content)
        
        return {"message": f"Successfully added {medicine_name} to database"}
    
    except Exception as e:
        print(f"❌ Add medicine error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add medicine: {str(e)}")