import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import get_db
from models import Reminder, User
from services.sms_service import sms_service
import json
import os


class ReminderScheduler:
    """Background scheduler for sending reminder notifications via SMS"""
    
    def __init__(self):
        self.running = False
        self.check_interval = 60  # Check every 60 seconds
        self._processing_ids = set()  # Track IDs currently being processed
    
    def load_report_data(self) -> dict:
        """Load report data from JSON file"""
        report_file_path = os.path.join(os.path.dirname(__file__), "..", "reminder_report.json")
        try:
            with open(report_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading report data: {e}")
            return {}
    
    def process_reminder(self, reminder: Reminder, report_data: dict, db: Session):
        """Process a single reminder and send SMS"""
        try:
            # Get user's verified phone number
            user = db.query(User).filter(User.id == reminder.user_id).first()
            if not user:
                print(f"User not found for reminder {reminder.id}")
                reminder.status = "failed"
                db.commit()
                return
            
            if not user.phone or not user.phone_verified:
                print(f"No verified phone for reminder {reminder.id}")
                reminder.status = "failed"
                db.commit()
                return
            
            phone_number = user.phone
            
            if reminder.reminder_type == "medicine":
                # Medicine reminder
                message = sms_service.format_medicine_reminder(
                    medicine_name=reminder.title,
                    notes=reminder.description
                )
            elif reminder.reminder_type == "report":
                # Report reminder - fetch details from JSON
                report_info = report_data.get(reminder.title)
                if not report_info:
                    message = f"Reminder: {reminder.title} scheduled. Contact your lab for details."
                else:
                    message = sms_service.format_report_reminder(
                        report_name=reminder.title,
                        best_time=report_info.get("best_time", "Not specified"),
                        fasting_required=report_info.get("fasting_required", "Not specified"),
                        preparation=report_info.get("preparation", []),
                        instructions=report_info.get("instructions", [])
                    )
            else:
                message = f"Reminder: {reminder.title}"
            
            # Send SMS
            sms_service.send_sms(phone_number, message)
            reminder.status = "sent"
            print(f"✅ Sent SMS reminder {reminder.id} to {phone_number}")
            
        except Exception as e:
            print(f"❌ Failed to send reminder {reminder.id}: {str(e)}")
            reminder.status = "failed"
    
    async def check_and_send_reminders(self):
        """Check for due reminders and send notifications"""
        report_data = self.load_report_data()
        
        # Process reminders one at a time with fresh DB session each
        while True:
            db: Session = next(get_db())
            try:
                now = datetime.now()
                
                # Get ONE pending reminder that is due and not being processed
                query = db.query(Reminder).filter(
                    Reminder.is_active == True,
                    Reminder.status == "pending",
                    Reminder.reminder_time <= now
                )
                if self._processing_ids:
                    query = query.filter(~Reminder.id.in_(self._processing_ids))
                reminder = query.first()
                
                if not reminder:
                    break  # No more due reminders
                
                # Add to processing set and mark as sending immediately
                self._processing_ids.add(reminder.id)
                reminder.status = "sending"
                db.commit()
                
                print(f"Processing reminder {reminder.id}: {reminder.title}")
                
                self.process_reminder(reminder, report_data, db)
                
                # Handle recurring reminders
                if reminder.is_recurring and reminder.recurrence_pattern:
                    self.schedule_next_occurrence(reminder, db)
                
                db.commit()
                
                # Remove from processing set
                self._processing_ids.discard(reminder.id)
                
            except Exception as e:
                print(f"Error in check_and_send_reminders: {str(e)}")
                db.rollback()
                # Clean up processing set on error
                if 'reminder' in locals() and reminder:
                    self._processing_ids.discard(reminder.id)
            finally:
                db.close()
    
    def schedule_next_occurrence(self, reminder: Reminder, db: Session):
        """Schedule next occurrence for recurring reminders"""
        if reminder.recurrence_pattern == "daily":
            reminder.reminder_time = reminder.reminder_time + timedelta(days=1)
        elif reminder.recurrence_pattern == "weekly":
            reminder.reminder_time = reminder.reminder_time + timedelta(weeks=1)
        elif reminder.recurrence_pattern == "monthly":
            reminder.reminder_time = reminder.reminder_time + timedelta(days=30)
        else:
            # If unknown pattern, don't reschedule
            reminder.is_active = False
            return
        
        reminder.status = "pending"
    
    async def start(self):
        """Start the scheduler"""
        self.running = True
        print("🔄 Reminder scheduler started")
        
        while self.running:
            try:
                await self.check_and_send_reminders()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"Scheduler error: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        print("⏹️ Reminder scheduler stopped")


# Global scheduler instance
reminder_scheduler = ReminderScheduler()


async def start_scheduler():
    """Start the reminder scheduler in background"""
    asyncio.create_task(reminder_scheduler.start())


def stop_scheduler():
    """Stop the reminder scheduler"""
    reminder_scheduler.stop()
