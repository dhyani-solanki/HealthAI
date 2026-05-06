# ============================================================
#  services/bytez_client.py
#  Shared Bytez API client for all AI calls
#  Replaces direct Gemini API calls throughout the backend
# ============================================================

import os
import json
import base64
import logging
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("bytez_client")

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
BYTEZ_MODEL = "google/gemini-2.5-flash"
BYTEZ_API_URL = f"https://api.bytez.com/models/v2/{BYTEZ_MODEL}"


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


def get_bytez_key() -> str:
    """Get the Bytez API key from environment."""
    return _read_env("BYTEZ_API_KEY")


def _extract_output(data: dict) -> str:
    """Extract text content from Bytez API response.
    Handles all formats:
      - {"output": {"role": "assistant", "content": "..."}}   ← dict
      - {"output": [{"role": "assistant", "content": "..."}]} ← list
      - {"output": "..."}                                     ← str
    """
    output = data.get("output", "")
    # Dict format: {"role": "assistant", "content": "..."}
    if isinstance(output, dict):
        content = output.get("content", "")
        if content:
            return content.strip()
        return str(output).strip()
    # List format
    if isinstance(output, list):
        for item in output:
            if isinstance(item, dict):
                content = item.get("content", "")
                if content:
                    return content.strip()
        return str(output)
    # String format
    if isinstance(output, str):
        return output.strip()
    return str(output).strip()


def call_bytez(prompt: str, temperature: float = 0.35, max_tokens: int = 4096) -> str:
    """
    Call Bytez API with a text prompt and return the response text.
    This replaces all direct Gemini REST API calls.
    """
    key = get_bytez_key()
    if not key:
        logger.error("BYTEZ_API_KEY not set in .env")
        return ""

    try:
        resp = requests.post(
            BYTEZ_API_URL,
            headers={
                "Authorization": f"Key {key}",
                "Content-Type": "application/json",
            },
            json={
                "input": [{"role": "user", "content": prompt}],
                "params": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            },
            timeout=120,
        )

        if resp.status_code == 200:
            return _extract_output(resp.json())
        else:
            logger.error(f"Bytez {resp.status_code}: {resp.text[:300]}")
            return ""
    except Exception as e:
        logger.error(f"Bytez call error: {e}")
        return ""


def call_bytez_with_image(prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Call Bytez API with text + image (multimodal).
    Used for medicine image scanning.
    """
    key = get_bytez_key()
    if not key:
        logger.error("BYTEZ_API_KEY not set in .env")
        return ""

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64_image}"

    try:
        resp = requests.post(
            BYTEZ_API_URL,
            headers={
                "Authorization": f"Key {key}",
                "Content-Type": "application/json",
            },
            json={
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }
                ],
            },
            timeout=120,
        )

        if resp.status_code == 200:
            return _extract_output(resp.json())
        else:
            logger.error(f"Bytez image call {resp.status_code}: {resp.text[:300]}")
            return ""
    except Exception as e:
        logger.error(f"Bytez image call error: {e}")
        return ""


def call_bytez_chat(messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """
    Call Bytez API with a multi-turn chat messages list.
    Used for MediGenius chat.
    """
    key = get_bytez_key()
    if not key:
        logger.error("BYTEZ_API_KEY not set in .env")
        return ""

    try:
        resp = requests.post(
            BYTEZ_API_URL,
            headers={
                "Authorization": f"Key {key}",
                "Content-Type": "application/json",
            },
            json={
                "input": messages,
                "params": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            },
            timeout=120,
        )

        if resp.status_code == 200:
            return _extract_output(resp.json())
        else:
            logger.error(f"Bytez chat {resp.status_code}: {resp.text[:300]}")
            return ""
    except Exception as e:
        logger.error(f"Bytez chat error: {e}")
        return ""
