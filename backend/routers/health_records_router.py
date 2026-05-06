
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, HealthRecord
from schemas import HealthRecordCreate, HealthRecordOut
from auth.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/health-records", tags=["Health Records"])


@router.post("/", response_model=HealthRecordOut)
def create_record(
    data: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = HealthRecord(user_id=current_user.id, **data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[HealthRecordOut])
def get_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == current_user.id
    ).order_by(HealthRecord.record_date.desc()).all()
    return records


@router.get("/{record_id}", response_model=HealthRecordOut)
def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(HealthRecord).filter(
        HealthRecord.id == record_id,
        HealthRecord.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(HealthRecord).filter(
        HealthRecord.id == record_id,
        HealthRecord.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}