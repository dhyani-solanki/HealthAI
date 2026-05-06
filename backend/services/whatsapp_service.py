import os
from typing import Optional
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


class WhatsAppService:
    """Service for sending WhatsApp messages using Twilio API"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
        self.client = None
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
    
    async def send_message(
        self,
        to_phone_number: str,
        message: str
    ) -> dict:
        """
        Send a WhatsApp message via Twilio
        
        Args:
            to_phone_number: Recipient phone number with country code (e.g., +919876543210)
            message: Message content to send
            
        Returns:
            dict: Message SID and status
        """
        if not self.client:
            raise ValueError("Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
        
        # Clean phone number
        clean_phone = to_phone_number.strip()
        if not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        try:
            msg = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=f"whatsapp:{clean_phone}"
            )
            return {"sid": msg.sid, "status": msg.status}
        except Exception as e:
            raise Exception(f"Failed to send WhatsApp message: {str(e)}")
    
    def format_medicine_reminder(self, medicine_name: str, notes: Optional[str] = None) -> str:
        """Format a medicine reminder message"""
        message = f"⏰ Reminder: It's time to take your medicine - {medicine_name}"
        if notes:
            message += f"\n\n📝 Notes: {notes}"
        message += "\n\nPlease take your medicine as prescribed."
        return message
    
    def format_report_reminder(
        self,
        report_name: str,
        best_time: str,
        fasting_required: str,
        preparation: list,
        instructions: list
    ) -> str:
        """Format a report/test reminder message with instructions"""
        message = f"📋 Reminder: You have a {report_name} scheduled.\n\n"
        message += "📝 Instructions:\n\n"
        message += f"⏰ Best Time: {best_time}\n"
        message += f"🍽️ Fasting Required: {fasting_required}\n"
        
        if preparation:
            message += "\n📋 Preparation:\n"
            for prep in preparation:
                message += f"  • {prep}\n"
        
        if instructions:
            message += "\n💡 Notes:\n"
            for instruction in instructions:
                message += f"  • {instruction}\n"
        
        message += "\nPlease follow these instructions for accurate test results."
        return message


# Singleton instance
whatsapp_service = WhatsAppService()
