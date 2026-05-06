# Reminder Module - Setup Guide

## Overview
The Reminder module allows users to set medicine reminders and medical test/report reminders with automated WhatsApp notifications.

## Environment Variables

Add the following environment variables to your `.env` file for WhatsApp integration:

```env
# WhatsApp Cloud API Configuration (Meta)
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_API_VERSION=v18.0
```

### Getting WhatsApp Credentials

1. **Create a Meta Developer Account**
   - Go to [developers.facebook.com](https://developers.facebook.com)
   - Create an account and verify your phone number

2. **Create a WhatsApp Business App**
   - In the Meta Developer Portal, create a new app
   - Select "Business" type
   - Add the "WhatsApp" product to your app

3. **Get Access Token**
   - In your app settings, go to WhatsApp > Configuration
   - Generate a temporary access token (for testing) or permanent token (for production)
   - Copy the access token

4. **Get Phone Number ID**
   - In WhatsApp > Configuration, you'll see your phone number ID
   - Copy this ID

## Database Migration

The database models have been updated with new fields. You may need to run a migration:

```bash
# If using Alembic
alembic upgrade head

# Or recreate tables (WARNING: This will delete existing data)
# In your Python script:
from database import engine, Base
Base.metadata.create_all(bind=engine)
```

## Starting the Reminder Scheduler

The reminder scheduler runs in the background to send WhatsApp notifications at scheduled times.

### Option 1: Start with FastAPI (Recommended)

Update `main.py` to start the scheduler on startup:

```python
from services.reminder_scheduler import start_scheduler

@app.on_event("startup")
async def startup_event():
    await start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    from services.reminder_scheduler import stop_scheduler
    stop_scheduler()
```

### Option 2: Run as Separate Process

```bash
python -m backend.services.reminder_scheduler
```

## Available Reports

The system includes 9 predefined medical reports with detailed instructions:

1. Lipid Profile
2. CBC (Complete Blood Count)
3. Blood Glucose
4. Thyroid Profile
5. Liver Function Test
6. Kidney Function Test
7. Vitamin D
8. Vitamin B12
9. HbA1c

## API Endpoints

### Reminders
- `POST /reminders/` - Create a new reminder
- `GET /reminders/` - Get all reminders for current user
- `GET /reminders/upcoming` - Get upcoming reminders
- `PUT /reminders/{id}` - Update a reminder
- `DELETE /reminders/{id}` - Delete a reminder

### WhatsApp
- `POST /reminders/whatsapp-number` - Save user's WhatsApp number
- `GET /reminders/whatsapp-number` - Get user's WhatsApp number

### Reports
- `GET /reminders/reports` - Get list of available reports
- `GET /reminders/reports/{report_name}` - Get details for a specific report

## Frontend

The Reminder page is available at: `/dashboard/reminders`

Features:
- Add/Edit WhatsApp number
- Create medicine reminders
- Create medical test/report reminders with instructions
- View all reminders
- Delete reminders
- Set recurring reminders (daily, weekly, monthly)

## Testing

1. Start the backend server
2. Start the frontend development server
3. Navigate to `/dashboard/reminders`
4. Add your WhatsApp number
5. Create a test reminder with a future time
6. Wait for the reminder time to receive WhatsApp notification

## Troubleshooting

### WhatsApp Messages Not Sending
- Verify WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID are correct
- Check that the phone number format includes country code (e.g., +91)
- Ensure the recipient's phone number is saved in your WhatsApp Business contacts
- Check the Meta Developer Dashboard for API errors

### Scheduler Not Running
- Ensure the scheduler is started (check main.py startup event)
- Check backend logs for scheduler errors
- Verify database connection is working

### Report Details Not Loading
- Check that `reminder_report.json` exists in the backend directory
- Verify the JSON file is valid
- Check file permissions

## Security Notes

- Never commit `.env` file to version control
- Use environment-specific access tokens (development vs production)
- Regularly rotate WhatsApp access tokens
- Implement rate limiting for WhatsApp API calls
