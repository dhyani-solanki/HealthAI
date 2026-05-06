import sys
import os

# Fix internal imports (from core.xxx, from agents.xxx, from tools.xxx)
_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)