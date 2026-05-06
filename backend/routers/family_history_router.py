from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, FamilyHistory
from schemas import FamilyHistoryCreate, FamilyHistoryOut
from auth.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/family-history", tags=["Family History"])


@router.post("/", response_model=FamilyHistoryOut)
def add_family_history(
    data: FamilyHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = FamilyHistory(user_id=current_user.id, **data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/", response_model=List[FamilyHistoryOut])
def get_family_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entries = db.query(FamilyHistory).filter(
        FamilyHistory.user_id == current_user.id
    ).order_by(FamilyHistory.created_at.desc()).all()
    return entries


@router.delete("/{entry_id}")
def delete_family_history(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(FamilyHistory).filter(
        FamilyHistory.id == entry_id,
        FamilyHistory.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted"}