import os
from typing import Optional
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


class SMSService:
    """Service for sending SMS and phone verification using Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SERVICE_SID")
        self.client = None
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
    
    def _clean_phone(self, phone_number: str) -> str:
        clean = phone_number.strip()
        if not clean.startswith('+'):
            clean = '+' + clean
        return clean
    
    def _get_or_create_verify_service(self) -> str:
        """Get existing or create a new Twilio Verify Service"""
        if self.verify_service_sid:
            return self.verify_service_sid
        
        if not self.client:
            raise ValueError("Twilio credentials not configured")
        
        # Create a new Verify Service
        service = self.client.verify.v2.services.create(
            friendly_name='Health App Verification'
        )
        self.verify_service_sid = service.sid
        print(f"Created Twilio Verify Service: {service.sid}")
        return service.sid

    # ── SMS Verification via Twilio Verify ──
    def send_verification_sms(self, phone_number: str) -> dict:
        """Send SMS verification code via Twilio Verify Service (works for ANY number)"""
        if not self.client:
            raise ValueError("Twilio credentials not configured")
        
        clean_phone = self._clean_phone(phone_number)
        service_sid = self._get_or_create_verify_service()
        
        try:
            verification = self.client.verify.v2 \
                .services(service_sid) \
                .verifications \
                .create(to=clean_phone, channel='sms')
            return {"status": verification.status, "to": clean_phone}
        except Exception as e:
            raise Exception(f"Failed to send verification SMS: {str(e)}")
    
    def check_verification_code(self, phone_number: str, code: str) -> dict:
        """Check SMS verification code via Twilio Verify Service"""
        if not self.client:
            raise ValueError("Twilio credentials not configured")
        
        clean_phone = self._clean_phone(phone_number)
        service_sid = self._get_or_create_verify_service()
        
        try:
            check = self.client.verify.v2 \
                .services(service_sid) \
                .verification_checks \
                .create(to=clean_phone, code=code)
            return {"status": check.status, "valid": check.status == "approved"}
        except Exception as e:
            raise Exception(f"Failed to check verification code: {str(e)}")

    # ── Verified Caller ID (needed for trial accounts to send SMS) ──
    def add_to_verified_caller_ids(self, phone_number: str) -> dict:
        """Add number to Twilio Verified Caller IDs via phone call"""
        if not self.client:
            raise ValueError("Twilio credentials not configured")
        
        clean_phone = self._clean_phone(phone_number)
        
        try:
            validation_request = self.client.validation_requests.create(
                friendly_name=f'HealthApp-{clean_phone}',
                phone_number=clean_phone
            )
            return {
                "validation_code": validation_request.validation_code,
                "call_sid": validation_request.call_sid
            }
        except Exception as e:
            raise Exception(f"Failed to request caller ID verification: {str(e)}")
    
    def is_number_verified(self, phone_number: str) -> bool:
        """Check if a phone number is in Twilio's Verified Caller IDs"""
        if not self.client:
            return False
        
        clean_phone = self._clean_phone(phone_number)
        try:
            caller_ids = self.client.outgoing_caller_ids.list(phone_number=clean_phone)
            return len(caller_ids) > 0
        except Exception:
            return False

    # ── Send SMS (for reminders) ──
    def send_sms(self, to_phone_number: str, message: str) -> dict:
        """Send an SMS message via Twilio"""
        if not self.client:
            raise ValueError("Twilio credentials not configured")
        if not self.from_number:
            raise ValueError("TWILIO_PHONE_NUMBER not configured in .env")
        
        clean_phone = self._clean_phone(to_phone_number)
        try:
            msg = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=clean_phone
            )
            return {"sid": msg.sid, "status": msg.status}
        except Exception as e:
            raise Exception(f"Failed to send SMS: {str(e)}")
    
    # ── Message formatters ──
    def format_medicine_reminder(self, medicine_name: str, notes: Optional[str] = None) -> str:
        message = f"Reminder: Time to take your medicine - {medicine_name}"
        if notes:
            message += f"\nNotes: {notes}"
        return message
    
    def format_report_reminder(
        self,
        report_name: str,
        best_time: str,
        fasting_required: str,
        preparation: list,
        instructions: list
    ) -> str:
        message = f"Reminder: {report_name} scheduled\n\n"
        message += f"Best Time: {best_time}\n"
        message += f"Fasting: {fasting_required}\n"
        if preparation:
            message += "\nPreparation:\n"
            for prep in preparation[:3]:
                message += f"- {prep}\n"
        return message


# Singleton instance
sms_service = SMSService()
