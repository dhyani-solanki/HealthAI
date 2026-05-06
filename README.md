# 🏥 AI-Powered Personal Health Support System

A full-stack health management platform with FastAPI backend, Streamlit frontend, PostgreSQL database, and Claude AI integration.

---

## 🗂️ Project Structure

```
health_app/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy DB connection
│   ├── models/
│   │   └── models.py        # DB models (User, HealthRecord, etc.)
│   ├── schemas/
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── routers/
│   │   ├── auth.py          # Signup / Login / JWT
│   │   ├── health.py        # Health records & family history
│   │   ├── reminders.py     # Medication reminders
│   │   └── ai_features.py   # MediScan + MediGenius (Claude AI)
│   └── utils/
│       └── auth.py          # JWT utilities + password hashing
├── frontend/
│   ├── app.py               # Main Streamlit app
│   ├── styles.py            # Custom HTML/CSS/JS components
│   └── api_client.py        # API helper functions
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Quick Setup

### 1. Clone & Install

```bash
cd health_app
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

```sql
CREATE DATABASE health_app_db;
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in:
# - DATABASE_URL
# - SECRET_KEY (any long random string)
# - ANTHROPIC_API_KEY (from console.anthropic.com)
```

### 4. Run the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be at: http://localhost:8000
API docs: http://localhost:8000/docs

### 5. Run the Frontend

```bash
cd frontend
streamlit run app.py
```

The app will open at: http://localhost:8501

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🔐 Auth | Signup/Login with JWT (access + refresh tokens) |
| 🏥 Health Records | Age, gender, BMI, allergies, conditions, medications |
| 📋 Health Summary | Visual overview with BMI calculator |
| 👨‍👩‍👧 Family History | Track hereditary conditions by relation |
| 💊 MediScan | AI medicine lookup by name or image |
| 🤖 MediGenius | AI medical chatbot (powered by Claude) |
| ⏰ Reminders | Medication and appointment alerts |
| 📊 Dashboard | Health analytics and stats overview |

---

## 🔒 Security

- Passwords hashed with **bcrypt**
- **JWT access tokens** (30 min expiry)
- **JWT refresh tokens** (7 days expiry)
- All health APIs are **user-scoped** (users can only access their own data)
- CORS configured for local Streamlit frontend

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, Jose JWT, Passlib/bcrypt
- **Frontend:** Streamlit with custom HTML/CSS/JS (dark healthcare UI)
- **AI:** Anthropic Claude (MediScan + MediGenius)
- **Auth:** JWT Bearer tokens

---

## 📡 API Endpoints

```
POST /auth/signup         → Create account, returns tokens
POST /auth/login          → Login, returns tokens
GET  /auth/me             → Get current user

POST /health/record       → Save/update health record
GET  /health/record       → Get health record
POST /health/family-history     → Add family history entry
GET  /health/family-history     → List family history
DELETE /health/family-history/{id} → Delete entry

POST /reminders/          → Create reminder
GET  /reminders/          → List reminders
DELETE /reminders/{id}    → Delete reminder

POST /ai/chat             → Chat with MediGenius
GET  /ai/chat/history     → Get chat history
POST /ai/mediscan/text    → Scan medicine by name
POST /ai/mediscan/image   → Scan medicine by image
```
# health-app
