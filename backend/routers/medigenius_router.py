import os
import sys
import importlib
import json
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import User, ChatMessage, ChatSession
from schemas import ChatRequest, ChatResponse, ChatHistoryItem, ChatSessionOut
from auth.dependencies import get_current_user


router = APIRouter(prefix="/medigenius", tags=["MediGenius"])

# region agent log
def _dbg(hypothesis_id: str, location: str, message: str, data: dict):
    try:
        with open("C:/Users/DHYANI/health-app/debug-5f1b4f.log", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "5f1b4f",
                "runId": "pre-fix",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000),
            }, ensure_ascii=True) + "\n")
    except Exception:
        pass
# endregion

# ============================================================
# Initialize MediGenius
# ============================================================
medigenius_app = None
medigenius_initialize = None

try:
    BACKEND_DIR = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    )
    MEDIGENIUS_DIR = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "medigenius")
    )
    # region agent log
    _dbg("H1", "medigenius_router.py:init", "MediGenius init started", {"medigeniusDir": MEDIGENIUS_DIR, "cwd": os.getcwd()})
    # endregion

    # Ensure backend root is importable so "medigenius.*" package imports resolve.
    if BACKEND_DIR not in sys.path:
        sys.path.insert(0, BACKEND_DIR)
    # region agent log
    _dbg("H2", "medigenius_router.py:sys_path", "Path prepared for imports", {"backendDirInSysPath": BACKEND_DIR in sys.path, "medigeniusDirInSysPath": MEDIGENIUS_DIR in sys.path, "sysPathHead": sys.path[:3]})
    # endregion

    # Change working directory temporarily so relative paths (./data/, ./medical_db/) resolve
    original_cwd = os.getcwd()
    os.chdir(MEDIGENIUS_DIR)

    # Import the modules directly
    from medigenius.core.langgraph_workflow import create_workflow
    from medigenius.core.state import initialize_conversation_state, reset_query_state
    from medigenius.tools.vector_store import get_or_create_vectorstore

    # Initialize vector store
    pdf_path = os.path.join(MEDIGENIUS_DIR, "data", "medical_book.pdf")
    persist_dir = os.path.join(MEDIGENIUS_DIR, "medical_db")
    # region agent log
    _dbg("H3", "medigenius_router.py:paths", "Vector DB source paths", {"pdfExists": os.path.exists(pdf_path), "persistDirExists": os.path.exists(persist_dir)})
    # endregion

    existing_db = get_or_create_vectorstore(persist_dir=persist_dir)
    if not existing_db and os.path.exists(pdf_path):
        from medigenius.tools.pdf_loader import process_pdf
        doc_splits = process_pdf(pdf_path)
        get_or_create_vectorstore(documents=doc_splits, persist_dir=persist_dir)
    # region agent log
    _dbg("H4", "medigenius_router.py:vectorstore", "Vectorstore initialized", {"existingDb": bool(existing_db)})
    # endregion

    # Create the workflow
    medigenius_app = create_workflow()
    # region agent log
    _dbg("H5", "medigenius_router.py:workflow", "Workflow creation status", {"workflowReady": medigenius_app is not None})
    # endregion

    # Restore working directory
    os.chdir(original_cwd)

    print("MediGenius initialized successfully!")

except Exception as e:
    # region agent log
    _dbg("H5", "medigenius_router.py:exception", "MediGenius init exception", {"errorType": type(e).__name__, "error": str(e), "cwd": os.getcwd()})
    # endregion
    print(f"MediGenius init failed: {e}")
    print("Chat will return fallback responses.")
    # Restore working directory if it was changed
    try:
        os.chdir(original_cwd)
    except:
        pass


# ============================================================
# Helper: run a query through the workflow
# ============================================================
def run_medigenius_query(question: str, user_id: int) -> tuple[str, str]:
    """Returns (reply_text, source)"""
    from medigenius.core.state import initialize_conversation_state, reset_query_state

    conversation_state = initialize_conversation_state()
    conversation_state = reset_query_state(conversation_state)
    conversation_state["question"] = question

    # Save current dir, switch to medigenius dir for relative paths
    original = os.getcwd()
    MEDIGENIUS_DIR = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "medigenius")
    )
    os.chdir(MEDIGENIUS_DIR)

    try:
        result = medigenius_app.invoke(conversation_state)
        reply = result.get("generation", "Unable to generate a response. Please try rephrasing.")
        source = result.get("source", "MediGenius")
    finally:
        os.chdir(original)

    return reply, source


# ============================================================
# Session Endpoints
# ============================================================
@router.get("/sessions", response_model=list[ChatSessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


@router.post("/sessions", response_model=ChatSessionOut)
def create_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = ChatSession(user_id=current_user.id, title="New Chat")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"message": "Session deleted"}


@router.get("/sessions/{session_id}/messages", response_model=list[ChatHistoryItem])
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )


# ============================================================
# Chat Endpoint (session-aware)
# ============================================================
@router.post("/chat", response_model=ChatResponse)
def chat_with_medigenius(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Auto-create session if not provided
    session_id = request.session_id
    if not session_id:
        session = ChatSession(user_id=current_user.id, title="New Chat")
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id

    # Save user message
    user_msg = ChatMessage(
        user_id=current_user.id,
        session_id=session_id,
        role="user",
        content=request.message,
        timestamp=datetime.utcnow(),
    )
    db.add(user_msg)
    db.commit()

    # Get AI response
    reply_text = ""
    source = "MediGenius"

    if medigenius_app is not None:
        try:
            reply_text, source = run_medigenius_query(request.message, current_user.id)
        except Exception as e:
            reply_text = "I encountered an error processing your request. Please try again."
            source = "Error"
            print(f"MediGenius error: {e}")
    else:
        reply_text = (
            "MediGenius is currently unavailable. "
            "Please make sure the AI system is properly configured with valid API keys."
        )
        source = "Fallback"

    # Save AI response
    ai_msg = ChatMessage(
        user_id=current_user.id,
        session_id=session_id,
        role="assistant",
        content=reply_text,
        source=source,
        timestamp=datetime.utcnow(),
    )
    db.add(ai_msg)
    db.commit()

    # Update session title from first user message
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session and session.title == "New Chat":
        session.title = request.message[:80]
        session.updated_at = datetime.utcnow()
        db.commit()
    elif session:
        session.updated_at = datetime.utcnow()
        db.commit()

    return ChatResponse(
        reply=reply_text,
        source=source,
        timestamp=datetime.utcnow(),
        session_id=session_id,
    )


# ============================================================
# Chat History (legacy - returns all messages)
# ============================================================
@router.get("/history", response_model=list[ChatHistoryItem])
def get_chat_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.timestamp.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(messages))


# ============================================================
# Clear History
# ============================================================
@router.delete("/history")
def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id).delete()
    db.query(ChatSession).filter(ChatSession.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared"}