from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from auth.jwt_handler import verify_token
from database import get_db
from models import User
import json
import time
from typing import Optional

security = HTTPBearer(auto_error=False)

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


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    if credentials is None:
        # region agent log
        _dbg("H15", "dependencies.py:missing_token", "No bearer token provided", {"hasCredentialsObject": False})
        # endregion
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    # region agent log
    _dbg("H10", "dependencies.py:get_current_user", "Auth dependency entered", {"hasToken": bool(token), "tokenLength": len(token or "")})
    # endregion
    payload = verify_token(token)

    if payload is None:
        # region agent log
        _dbg("H11", "dependencies.py:invalid_token", "Token verification failed", {"payloadIsNone": True})
        # endregion
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        # region agent log
        _dbg("H12", "dependencies.py:invalid_payload", "Token payload missing sub", {"payloadKeys": list(payload.keys()) if isinstance(payload, dict) else []})
        # endregion
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        # region agent log
        _dbg("H13", "dependencies.py:user_not_found", "Token sub not present in DB", {"userId": user_id})
        # endregion
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # region agent log
    _dbg("H14", "dependencies.py:user_ok", "Authenticated user resolved", {"userId": user.id})
    # endregion
    return user