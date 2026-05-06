# ============================================================
#  main.py  — add the one new import line + include_router
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from dotenv import load_dotenv

load_dotenv()

from auth.router import router as auth_router
from routers.medigenius_router import router as medigenius_router
from routers.mediscan_router import router as mediscan_router
from routers.health_records_router import router as records_router
from routers.family_history_router import router as family_router
from routers.reminders_router import router as reminders_router
from routers.dashboard_router import router as dashboard_router
from routers.mediinsight_router import router as mediinsight_router
from routers.data_insights import router as data_insights_router
from routers.medreport_router import router as medreport_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="🏥 AI Health Support System",
    description="Personal health management with AI-powered features",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(medigenius_router)
app.include_router(mediscan_router)
app.include_router(records_router)
app.include_router(family_router)
app.include_router(reminders_router)
app.include_router(dashboard_router)
app.include_router(mediinsight_router)   # ← NEW
app.include_router(data_insights_router) # ← Data Insights module
app.include_router(medreport_router)     # ← MedReport Analyzer module


@app.on_event("startup")
async def startup_event():
    """Start background services on startup"""
    from services.reminder_scheduler import start_scheduler
    try:
        await start_scheduler()
    except Exception as e:
        print(f"Failed to start reminder scheduler: {e}")


@app.on_event("shutdown")
def shutdown_event():
    """Stop background services on shutdown"""
    from services.reminder_scheduler import stop_scheduler
    stop_scheduler()


@app.get("/")
def root():
    return {"message": "🏥 AI Health Support System API", "status": "running", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}