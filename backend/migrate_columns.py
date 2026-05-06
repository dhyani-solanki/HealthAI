"""Add missing columns to users and reminders tables"""
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # User columns
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20)"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code VARCHAR(6)"))
    conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code_expires TIMESTAMP"))
    
    # Reminder columns
    conn.execute(text("ALTER TABLE reminders ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20)"))
    conn.execute(text("ALTER TABLE reminders ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending'"))
    conn.commit()
    print("Migration complete: columns added successfully.")
