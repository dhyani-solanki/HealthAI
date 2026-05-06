# ============================================================
#  services/ai_analysis.py  (v2)
#  Uses Bytez API for all AI calls
# ============================================================

import os
import re
import json
import logging
from pathlib import Path
from typing import Generator, List, Dict

from services.bytez_client import call_bytez

logger = logging.getLogger("data_insights.ai_analysis")


# ─────────────────────────────────────────────────────────────
#  Analysis prompt
# ─────────────────────────────────────────────────────────────
def _build_analysis_prompt(report_label: str, parameters: List[Dict]) -> str:
    params_str = "\n".join(
        f"  • {p['name']}: {p['value']} {p.get('unit','')}  "
        f"[{p.get('status','').upper()}]  "
        f"Normal range: {p.get('normal_range','N/A')}"
        for p in parameters
    )
    return (
        f"You are a compassionate, expert medical AI assistant.\n"
        f"A patient has uploaded a {report_label} report. "
        f"Here are the extracted parameters:\n\n{params_str}\n\n"
        f"Provide a clear, friendly health insight in plain English. "
        f"Structure your response in 3 short paragraphs:\n"
        f"1. Overall health summary (2-3 sentences).\n"
        f"2. Highlight any abnormal or borderline values and their possible implications.\n"
        f"3. Practical, actionable lifestyle recommendations.\n\n"
        f"Keep the tone supportive and educational. Do NOT diagnose diseases.\n"
        f"End with: 'Note: This is AI-generated insight. Please consult a doctor for medical advice.'"
    )


def _build_comparison_prompt(
    report_label: str,
    older_params: List[Dict],
    newer_params: List[Dict],
) -> str:
    def fmt(params):
        return "\n".join(
            f"  • {p['name']}: {p['value']} {p.get('unit','')} [{p.get('status','').upper()}]"
            for p in params
        )
    return (
        f"You are a medical AI comparing two {report_label} reports.\n\n"
        f"OLDER REPORT:\n{fmt(older_params)}\n\n"
        f"NEWER REPORT:\n{fmt(newer_params)}\n\n"
        f"Write a concise comparison in 3 short paragraphs:\n"
        f"1. What has improved since the older report.\n"
        f"2. What has worsened or stayed concerning.\n"
        f"3. Recommendations going forward.\n\n"
        f"Be supportive and specific. Do NOT diagnose.\n"
        f"End with: 'Note: Always consult a doctor for clinical interpretation.'"
    )


# ─────────────────────────────────────────────────────────────
#  Streaming generators (SSE via FastAPI StreamingResponse)
# ─────────────────────────────────────────────────────────────
def stream_analysis(report_label: str, parameters: List[Dict]) -> Generator[str, None, None]:
    """
    Calls Gemini (non-streaming REST), then yields the text word-by-word
    so the frontend receives an SSE stream.
    """
    prompt = _build_analysis_prompt(report_label, parameters)
    text = call_bytez(prompt)

    if not text:
        text = (
            "Your report parameters have been extracted above. "
            "AI analysis is temporarily unavailable — the Gemini API key may be exhausted "
            "(free tier: 20 requests/day). Please review your values manually and consult "
            "a healthcare professional. Note: This is an AI-generated tool, not medical advice."
        )

    # Yield word by word for typewriter feel
    words = text.split(" ")
    for i, word in enumerate(words):
        sep = " " if i < len(words) - 1 else ""
        yield word + sep


def stream_comparison(
    report_label: str,
    older_params: List[Dict],
    newer_params: List[Dict],
) -> Generator[str, None, None]:
    prompt = _build_comparison_prompt(report_label, older_params, newer_params)
    text = call_bytez(prompt)
    if not text:
        text = (
            "Comparison AI summary is temporarily unavailable. "
            "Please compare your parameter values manually in the table above. "
            "Note: Always consult a doctor for clinical interpretation."
        )
    words = text.split(" ")
    for i, word in enumerate(words):
        sep = " " if i < len(words) - 1 else ""
        yield word + sep


# ─────────────────────────────────────────────────────────────
#  Delta comparison (no AI, purely numeric)
# ─────────────────────────────────────────────────────────────
def build_delta_comparison(older_params: List[Dict], newer_params: List[Dict]) -> List[Dict]:
    newer_map = {p["name"].lower(): p for p in newer_params}
    deltas = []
    GOOD_HIGHER = {"hdl", "vitamin", "albumin", "hemoglobin", "haemoglobin", "ferritin"}

    for op in older_params:
        key = op["name"].lower()
        np_ = newer_map.get(key)
        if not np_:
            continue
        try:
            old_v = float(op["value"])
            new_v = float(np_["value"])
            diff  = new_v - old_v
            pct   = (diff / old_v * 100) if old_v != 0 else 0

            if abs(pct) < 2:
                trend = "stable"
                color = "#7a9ab5"
            elif diff > 0:
                trend = "up"
                color = "#00ff88" if any(g in key for g in GOOD_HIGHER) else "#ff4757"
            else:
                trend = "down"
                color = "#ff4757" if any(g in key for g in GOOD_HIGHER) else "#00ff88"

            deltas.append({
                "name":         op["name"],
                "older_value":  op["value"],
                "newer_value":  np_["value"],
                "unit":         op.get("unit", ""),
                "trend":        trend,
                "color":        color,
                "pct_change":   round(pct, 1),
                "older_status": op.get("status", ""),
                "newer_status": np_.get("status", ""),
            })
        except (ValueError, ZeroDivisionError):
            continue

    return deltas
