from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, ChatMessage, MedicineScan, HealthRecord, FamilyHistory, Reminder, DataInsightReport
from schemas import DashboardStats, ChatHistoryItem, ReminderOut
from auth.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Counts
    total_chats = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.role == "user"
    ).count()

    total_scans = db.query(MedicineScan).filter(
        MedicineScan.user_id == current_user.id
    ).count()

    total_records = db.query(HealthRecord).filter(
        HealthRecord.user_id == current_user.id
    ).count()

    total_family = db.query(FamilyHistory).filter(
        FamilyHistory.user_id == current_user.id
    ).count()

    total_family_reports = db.query(DataInsightReport).filter(
        DataInsightReport.user_id == current_user.id,
        DataInsightReport.owner_type == "family"
    ).count()

    active_reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_active == True
    ).count()

    # Recent chats (last 5)
    recent_chats = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.timestamp.desc()).limit(5).all()

    # Upcoming reminders
    upcoming = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_active == True,
        Reminder.reminder_time >= datetime.utcnow()
    ).order_by(Reminder.reminder_time).limit(5).all()

    return DashboardStats(
        total_chats=total_chats,
        total_scans=total_scans,
        total_records=total_records,
        total_family_conditions=total_family,
        total_family_reports=total_family_reports,
        active_reminders=active_reminders,
        recent_chats=recent_chats,
        upcoming_reminders=upcoming,
    )