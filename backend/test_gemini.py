# ============================================================
#  test_gemini.py
#  Run this SECOND to verify your Gemini API key works
#  and find which model is available on your key.
#
#  Run: python test_gemini.py
# ============================================================

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend folder
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


def read_key_from_env_file(key_name: str) -> str:
    """Read directly from .env file — bypasses any SDK interference."""
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == key_name:
                return v.strip().strip('"').strip("'")
    return os.environ.get(key_name, "")


# All models to test — from your rate limits dashboard
MODELS_TO_TEST = [
    "gemini-2.5-flash-lite-preview-06-17",  # Gemini 3.1 Flash Lite — 500 RPD
    "gemini-2.5-flash",                      # Gemini 2.5 Flash — 20 RPD
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-flash-preview-04-17",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
]

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
TEST_PROMPT = "Say exactly: Hello from MediInsight"


def test_model(key: str, model: str) -> tuple:
    """Returns (success: bool, message: str)"""
    try:
        url  = f"{BASE_URL}/{model}:generateContent?key={key}"
        body = {
            "contents": [{"parts": [{"text": TEST_PROMPT}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 20},
        }
        resp = requests.post(url, json=body, timeout=15)

        if resp.status_code == 200:
            data = resp.json()
            # Try to extract text — show raw if structure differs
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return True, f"✅ Response: {text.strip()}"
            except (KeyError, IndexError, TypeError):
                return True, f"✅ Got 200 — raw: {str(data)[:250]}"

        elif resp.status_code == 404:
            return False, "❌ 404 — Model not available on this key"

        elif resp.status_code == 429:
            error = resp.json().get("error", {})
            msg   = error.get("message", "")
            if "limit: 0" in msg:
                return False, "❌ 429 — Quota is 0 (not enabled)"
            return False, f"⚠️  429 — Rate limited: {msg[:80]}"

        elif resp.status_code == 400:
            return False, f"❌ 400 — {resp.text[:150]}"

        else:
            return False, f"❌ {resp.status_code} — {resp.text[:150]}"

    except Exception as e:
        return False, f"❌ Exception: {e}"


def test_gemini():
    print("=" * 55)
    print("  GEMINI API KEY TEST")
    print("=" * 55)

    # Read key
    key = read_key_from_env_file("GEMINI_API_KEY")
    if not key:
        print("❌ GEMINI_API_KEY not found in backend/.env")
        print("   Get a key at: https://aistudio.google.com/apikey")
        return None

    print(f"✅ GEMINI_API_KEY found: ...{key[-8:]}\n")

    # Test list models endpoint
    print("🔍 Checking available models...\n")

    working_models = []

    for model in MODELS_TO_TEST:
        success, msg = test_model(key, model)
        status = "✅ WORKS" if success else "   skip "
        print(f"  {status}  {model:<45} {msg}")
        if success:
            working_models.append(model)

    print("\n" + "=" * 55)
    if working_models:
        print(f"✅ PASS — {len(working_models)} working model(s) found!")
        print(f"   Best model to use: {working_models[0]}")
        print(f"\n   Add this to your mediinsight_rag.py:")
        print(f'   _GEMINI_MODELS = {working_models}')
    else:
        print("❌ FAIL — No working model found.")
        print("\n   Possible reasons:")
        print("   1. Key is a Google Cloud key, not AI Studio key")
        print("      → Get correct key at: https://aistudio.google.com/apikey")
        print("   2. Daily quota exhausted (limit: 0 means not enabled)")
        print("      → Create a new project at aistudio.google.com")
    print("=" * 55)

    return working_models[0] if working_models else None


if __name__ == "__main__":
    best_model = test_gemini()