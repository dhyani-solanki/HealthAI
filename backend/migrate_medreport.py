"""
One-time migration: add owner_type, owner_name, summary columns to data_insight_reports.
Run: python migrate_medreport.py
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dhyani1724@localhost:5432/health_system")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

migrations = [
    "ALTER TABLE data_insight_reports ADD COLUMN IF NOT EXISTS owner_type VARCHAR(50) DEFAULT 'myself'",
    "ALTER TABLE data_insight_reports ADD COLUMN IF NOT EXISTS owner_name VARCHAR(255)",
    "ALTER TABLE data_insight_reports ADD COLUMN IF NOT EXISTS summary TEXT",
]

for sql in migrations:
    print(f"Running: {sql}")
    cur.execute(sql)

conn.commit()
cur.close()
conn.close()
print("Migration complete!")
