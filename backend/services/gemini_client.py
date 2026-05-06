# ============================================================
#  services/gemini_client.py
#  Google Gemini API client for text and vision calls
# ============================================================

import os
import base64
import logging
import requests
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger("gemini_client")

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _read_env(key: str) -> str:
    """Read key from .env file."""
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == key:
                val = v.strip().split("#")[0].strip().strip('"').strip("'")
                if val:
                    return val
    return os.environ.get(key, "").strip()


def get_gemini_key() -> str:
    """Get the Gemini API key from environment."""
    return _read_env("GEMINI_API_KEY")


def call_gemini(prompt: str, temperature: float = 0.35, max_tokens: int = 4096) -> str:
    """
    Call Gemini API with a text prompt and return the response text.
    """
    key = get_gemini_key()
    if not key:
        logger.error("GEMINI_API_KEY not set in .env")
        return ""

    try:
        resp = requests.post(
            f"{GEMINI_API_URL}?key={key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            },
            timeout=120,
        )

        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return ""
        else:
            logger.error(f"Gemini {resp.status_code}: {resp.text[:300]}")
            return ""
    except Exception as e:
        logger.error(f"Gemini call error: {e}")
        return ""


def call_gemini_vision(prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Call Gemini API with text + image (multimodal) for medicine image scanning.
    """
    key = get_gemini_key()
    if not key:
        logger.error("GEMINI_API_KEY not set in .env")
        return ""

    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    try:
        resp = requests.post(
            f"{GEMINI_API_URL}?key={key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": b64_image,
                                }
                            },
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 2048,
                },
            },
            timeout=120,
        )

        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return ""
        else:
            logger.error(f"Gemini vision {resp.status_code}: {resp.text[:300]}")
            return ""
    except Exception as e:
        logger.error(f"Gemini vision call error: {e}")
        return ""


def call_gemini_chat(messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """
    Call Gemini API with multi-turn chat messages.
    Converts OpenAI-style messages to Gemini format.
    """
    key = get_gemini_key()
    if not key:
        logger.error("GEMINI_API_KEY not set in .env")
        return ""

    # Convert OpenAI-style messages to Gemini format
    contents = []
    for msg in messages:
        role = msg.get("role", "user")
        gemini_role = "model" if role == "assistant" else "user"
        contents.append({
            "role": gemini_role,
            "parts": [{"text": msg.get("content", "")}],
        })

    try:
        resp = requests.post(
            f"{GEMINI_API_URL}?key={key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            },
            timeout=120,
        )

        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return ""
        else:
            logger.error(f"Gemini chat {resp.status_code}: {resp.text[:300]}")
            return ""
    except Exception as e:
        logger.error(f"Gemini chat error: {e}")
        return ""
