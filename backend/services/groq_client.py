# ============================================================
#  services/groq_client.py
#  Groq API client for MediScan image analysis
# ============================================================

import os
import base64
import logging
import requests
from pathlib import Path
from typing import Optional

logger = logging.getLogger("groq_client")

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


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


def get_groq_key() -> str:
    """Get the Groq API key from environment."""
    return _read_env("GROQ_API_KEY")


def call_groq_vision(prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Call Groq Vision API with text + image for medicine scanning.
    Returns the response text with source attribution.
    """
    key = get_groq_key()
    if not key:
        logger.error("GROQ_API_KEY not set in .env")
        return ""

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    try:
        resp = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_VISION_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
            timeout=120,
        )

        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                return content.strip()
            return ""
        else:
            logger.error(f"Groq Vision {resp.status_code}: {resp.text[:300]}")
            return ""
    except Exception as e:
        logger.error(f"Groq Vision call error: {e}")
        return ""
