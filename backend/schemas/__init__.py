# ============================================================
#  schemas/__init__.py
#
#  The `schemas/` package shadows `schemas.py` in Python's
#  import system. This file re-exports every class from the
#  original schemas.py so that ALL existing code that does:
#    from schemas import UserSignup, ...
#  continues to work without any modification.
# ============================================================

import importlib.util
import sys
from pathlib import Path

# Load the original schemas.py via importlib (shadowed by this package)
_orig_path = Path(__file__).parent.parent / "schemas.py"
_spec = importlib.util.spec_from_file_location("_health_app_orig_schemas", str(_orig_path))
_orig_mod = importlib.util.module_from_spec(_spec)
sys.modules["_health_app_orig_schemas"] = _orig_mod
_spec.loader.exec_module(_orig_mod)

# ── Re-export every public class from the original schemas.py ──
UserSignup              = _orig_mod.UserSignup
UserLogin               = _orig_mod.UserLogin
TokenResponse           = _orig_mod.TokenResponse
UserOut                 = _orig_mod.UserOut
UserUpdate              = _orig_mod.UserUpdate
ChatRequest             = _orig_mod.ChatRequest
ChatResponse            = _orig_mod.ChatResponse
ChatHistoryItem         = _orig_mod.ChatHistoryItem
ChatSessionOut          = _orig_mod.ChatSessionOut
MediScanRequest         = _orig_mod.MediScanRequest
MediScanResponse        = _orig_mod.MediScanResponse
MediScanImageResponse   = _orig_mod.MediScanImageResponse
HealthRecordCreate      = _orig_mod.HealthRecordCreate
HealthRecordOut         = _orig_mod.HealthRecordOut
FamilyHistoryCreate     = _orig_mod.FamilyHistoryCreate
FamilyHistoryOut        = _orig_mod.FamilyHistoryOut
ReminderCreate          = _orig_mod.ReminderCreate
ReminderOut             = _orig_mod.ReminderOut
ReminderUpdate          = _orig_mod.ReminderUpdate
WhatsAppNumberInput     = _orig_mod.WhatsAppNumberInput
PhoneNumberInput        = _orig_mod.PhoneNumberInput
VerifyCodeInput         = _orig_mod.VerifyCodeInput
PhoneVerificationStatus = _orig_mod.PhoneVerificationStatus
DashboardStats          = _orig_mod.DashboardStats

__all__ = [
    "UserSignup", "UserLogin", "TokenResponse", "UserOut", "UserUpdate",
    "ChatRequest", "ChatResponse", "ChatHistoryItem", "ChatSessionOut",
    "MediScanRequest", "MediScanResponse", "MediScanImageResponse",
    "HealthRecordCreate", "HealthRecordOut",
    "FamilyHistoryCreate", "FamilyHistoryOut",
    "ReminderCreate", "ReminderOut", "ReminderUpdate", "WhatsAppNumberInput",
    "PhoneNumberInput", "VerifyCodeInput", "PhoneVerificationStatus",
    "DashboardStats",
]
