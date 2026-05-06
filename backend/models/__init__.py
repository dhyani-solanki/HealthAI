# ============================================================
#  models/__init__.py
#
#  The `models/` package shadows `models.py` in Python's
#  import system. This file re-exports every class from the
#  original models.py so that ALL existing code that does:
#    from models import User
#  continues to work without any modification.
# ============================================================

import importlib.util
import sys
from pathlib import Path

# Load the original models.py via importlib (it's shadowed by this package)
_orig_path = Path(__file__).parent.parent / "models.py"
_spec = importlib.util.spec_from_file_location("_health_app_orig_models", str(_orig_path))
_orig_mod = importlib.util.module_from_spec(_spec)
# Register in sys.modules first so any internal imports inside models.py resolve correctly
sys.modules["_health_app_orig_models"] = _orig_mod
_spec.loader.exec_module(_orig_mod)

# ── Re-export every public class from the original models.py ──
User                 = _orig_mod.User
ChatSession          = _orig_mod.ChatSession
ChatMessage          = _orig_mod.ChatMessage
MedicineScan         = _orig_mod.MedicineScan
HealthRecord         = _orig_mod.HealthRecord
FamilyHistory        = _orig_mod.FamilyHistory
Reminder             = _orig_mod.Reminder
LabReport            = _orig_mod.LabReport
LabAnalysis          = _orig_mod.LabAnalysis
LabComparison        = _orig_mod.LabComparison
MedicalKnowledgeCache = _orig_mod.MedicalKnowledgeCache

# ── Import and re-export DataInsightReport from report_insight_model ──
from .report_insight_model import DataInsightReport

__all__ = [
    "User", "ChatSession", "ChatMessage", "MedicineScan", "HealthRecord",
    "FamilyHistory", "Reminder", "LabReport", "LabAnalysis",
    "LabComparison", "MedicalKnowledgeCache", "DataInsightReport",
]
