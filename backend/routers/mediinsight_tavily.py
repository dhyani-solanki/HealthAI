# ============================================================
#  routers/mediinsight_tavily.py
#  STEP 2 — Data Retrieval
#
#  Uses Tavily to scrape trusted medical sources.
#  Returns structured, filtered context for Gemini.
#
#  pip install langchain-tavily
#  .env: TAVILY_API_KEY=tvly-...
# ============================================================

import os, re, logging
from pathlib import Path
from typing import Dict, List, Optional

logger    = logging.getLogger("mediinsight.tavily")
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# In-session cache so the same report type is never scraped twice
_cache: Dict[str, str] = {}


def _read_key(name: str) -> str:
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == name:
                val = v.strip().strip('"').strip("'")
                if val:
                    return val
    return os.environ.get(name, "").strip()


TRUSTED_DOMAINS = [
    "medlineplus.gov",
    "healthline.com",
    "my.clevelandclinic.org",
    "cdc.gov",
    "thyroid.org",
    "diabetes.org",
    "niddk.nih.gov",
    "heart.org",
]


# ── Step 2: Data Retrieval ────────────────────────────────────
def retrieve_medical_data(report_type: str, query: Optional[str] = None) -> str:
    """
    Step 2 — Retrieve medical data from trusted sources via Tavily.
    Returns raw combined text from top results.
    Returns "" if Tavily key missing or search fails (triggers fallback).
    """
    cache_key = f"{report_type}::{query or ''}"
    if cache_key in _cache:
        logger.info(f"[Tavily] Cache hit: {report_type}")
        return _cache[cache_key]

    key = _read_key("TAVILY_API_KEY")
    if not key:
        logger.warning("[Tavily] TAVILY_API_KEY not set — will use Gemini fallback")
        return ""

    search_query = query or f"{report_type} lab test normal ranges interpretation clinical significance"

    try:
        os.environ["TAVILY_API_KEY"] = key
        from langchain_tavily import TavilySearch

        tool    = TavilySearch(
            max_results     = 5,
            search_depth    = "advanced",
            include_domains = TRUSTED_DOMAINS,
        )
        raw = tool.invoke({"query": search_query})

        # Handle dict response (new langchain-tavily format)
        if isinstance(raw, dict):
            result_list = raw.get("results", [])
        elif isinstance(raw, list):
            result_list = raw
        else:
            result_list = []

        # Extract text from each result
        texts = []
        for r in result_list:
            if isinstance(r, dict):
                content = r.get("content") or r.get("text") or ""
                url     = r.get("url", "")
                title   = r.get("title", "")
                if content and len(content) > 50:
                    texts.append(f"SOURCE: {title}\nURL: {url}\n{content}")
            elif isinstance(r, str) and len(r) > 50:
                texts.append(r)

        combined = "\n\n---\n\n".join(texts)
        _cache[cache_key] = combined
        logger.info(f"[Tavily] Retrieved {len(texts)} sources for '{report_type}'")
        return combined

    except Exception as e:
        logger.error(f"[Tavily] Retrieval failed: {e}")
        return ""


# ── Step 3: Context Building ──────────────────────────────────
def build_context(scraped_text: str, report_type: str,
                  param_names: Optional[List[str]] = None) -> str:
    """
    Step 3 — Filter and organize scraped data into structured context.
    Keeps only sentences relevant to the report type and parameter names.
    Ensures only high-quality content is passed to Gemini.
    """
    if not scraped_text:
        return ""

    lines      = scraped_text.split(".")
    keywords   = [report_type.lower()] + [p.lower() for p in (param_names or [])]
    relevant   = []
    seen       = set()

    for line in lines:
        line_lower = line.lower().strip()
        if len(line_lower) < 30:
            continue
        # Keep only lines mentioning relevant terms
        if any(kw in line_lower for kw in keywords):
            clean = line.strip()
            # Deduplicate
            sig   = clean[:60].lower()
            if sig not in seen:
                seen.add(sig)
                relevant.append(clean)

    # Cap at 3000 chars to stay within Gemini token budget
    context = ". ".join(relevant)
    if len(context) > 3000:
        context = context[:3000] + "..."

    logger.info(f"[Tavily] Built context: {len(relevant)} relevant sentences, {len(context)} chars")
    return context


def get_param_significance(param_name: str, scraped_text: str) -> str:
    """Extract the most relevant sentence about a specific parameter."""
    if not scraped_text:
        return ""
    sentences = [
        s.strip() for s in scraped_text.lower().split(".")
        if param_name.lower() in s and len(s.strip()) > 30
    ]
    return sentences[0].capitalize() + "." if sentences else ""


def is_sufficient(scraped_text: str, min_chars: int = 200) -> bool:
    """Step 6 check — is the scraped data sufficient or do we need Gemini fallback?"""
    return bool(scraped_text) and len(scraped_text.strip()) >= min_chars