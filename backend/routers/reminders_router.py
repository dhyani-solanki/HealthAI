from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Reminder
from schemas import ReminderCreate, ReminderOut, ReminderUpdate, WhatsAppNumberInput, PhoneNumberInput, VerifyCodeInput
from auth.dependencies import get_current_user
from typing import List, Optional
from datetime import datetime, timedelta
from services.sms_service import sms_service
import json
import os

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.post("/", response_model=ReminderOut)
def create_reminder(
    data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder = Reminder(user_id=current_user.id, **data.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("/", response_model=List[ReminderOut])
def get_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id
    ).order_by(Reminder.reminder_time).all()
    return reminders


@router.get("/upcoming", response_model=List[ReminderOut])
def get_upcoming_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_active == True,
        Reminder.reminder_time >= datetime.utcnow()
    ).order_by(Reminder.reminder_time).limit(10).all()
    return reminders


@router.put("/{reminder_id}", response_model=ReminderOut)
def update_reminder(
    reminder_id: int,
    data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reminder, key, value)

    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted"}


@router.post("/whatsapp-number")
def save_whatsapp_number(
    data: WhatsAppNumberInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save or update user's WhatsApp number"""
    whatsapp_number = data.whatsapp_number

    # Validate phone number format (should start with + and contain digits)
    if not whatsapp_number.startswith('+'):
        raise HTTPException(status_code=400, detail="Phone number must start with country code (e.g., +91)")
    
    if len(whatsapp_number) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    current_user.whatsapp_number = whatsapp_number
    db.commit()
    db.refresh(current_user)
    return {"message": "WhatsApp number saved successfully", "whatsapp_number": whatsapp_number}


@router.get("/whatsapp-number")
def get_whatsapp_number(
    current_user: User = Depends(get_current_user)
):
    """Get user's saved WhatsApp number"""
    return {
        "whatsapp_number": current_user.whatsapp_number,
        "has_number": bool(current_user.whatsapp_number)
    }


@router.get("/reports")
def get_available_reports():
    """Get list of available medical reports from JSON"""
    report_file_path = os.path.join(os.path.dirname(__file__), "..", "reminder_report.json")
    
    try:
        with open(report_file_path, 'r') as f:
            report_data = json.load(f)
        
        # Return only report names
        report_names = list(report_data.keys())
        return {
            "reports": report_names,
            "total": len(report_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load reports: {str(e)}")


@router.get("/reports/{report_name}")
def get_report_details(report_name: str):
    """Get details for a specific report"""
    report_file_path = os.path.join(os.path.dirname(__file__), "..", "reminder_report.json")
    
    try:
        with open(report_file_path, 'r') as f:
            report_data = json.load(f)
        
        # Find the report (case-insensitive search)
        report_key = None
        for key in report_data.keys():
            if key.lower() == report_name.lower():
                report_key = key
                break
        
        if not report_key:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "name": report_key,
            "details": report_data[report_key]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load report details: {str(e)}")


# ============================================================
#  PHONE VERIFICATION ENDPOINTS
# ============================================================

@router.post("/phone/send-code")
def send_verification_code(
    data: PhoneNumberInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a phone number: if already in Twilio Verified Caller IDs, auto-verify.
    Otherwise, trigger a Twilio phone call to add it."""
    phone_number = data.phone_number.strip()
    
    if not phone_number.startswith('+'):
        raise HTTPException(status_code=400, detail="Phone number must start with country code (e.g., +91)")
    if len(phone_number) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    # Check if already in Twilio Verified Caller IDs
    if sms_service.is_number_verified(phone_number):
        current_user.phone = phone_number
        current_user.phone_verified = True
        db.commit()
        return {
            "message": "Phone number is already verified!",
            "phone_number": phone_number,
            "already_verified": True,
            "validation_code": None
        }
    
    # Trigger Twilio phone call to add to Verified Caller IDs
    try:
        result = sms_service.add_to_verified_caller_ids(phone_number)
        current_user.phone = phone_number
        current_user.verification_code = result["validation_code"]
        current_user.phone_verified = False
        db.commit()
        return {
            "message": "Twilio is calling your phone. Answer and enter the code shown on screen.",
            "phone_number": phone_number,
            "already_verified": False,
            "validation_code": result["validation_code"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate verification: {str(e)}")


@router.post("/phone/confirm")
def confirm_phone_verification(
    data: PhoneNumberInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if number was added to Verified Caller IDs after the call"""
    phone_number = data.phone_number.strip()
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    is_verified = sms_service.is_number_verified(phone_number)
    
    if is_verified:
        current_user.phone = phone_number
        current_user.phone_verified = True
        current_user.verification_code = None
        db.commit()
        return {"message": "Phone number verified! You will now receive SMS reminders.", "phone_verified": True}
    else:
        return {"message": "Not yet verified. Please answer the call and enter the code.", "phone_verified": False}


@router.get("/phone/status")
def get_phone_status(
    current_user: User = Depends(get_current_user)
):
    """Get user's phone verification status"""
    return {
        "phone_number": current_user.phone,
        "phone_verified": current_user.phone_verified or False
    }