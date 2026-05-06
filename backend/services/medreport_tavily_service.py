# ============================================================
#  services/medreport_tavily_service.py
#  Tavily search service for MedReport Analyzer module ONLY.
#  Uses MEDREPORT_TAVILY_API_KEY (from reference project).
# ============================================================

import os
from datetime import datetime, timezone, timedelta
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("MEDREPORT_TAVILY_API_KEY", "")

TRUSTED_DOMAINS = [
    "medlineplus.gov",
    "mayoclinic.org",
    "labcorp.com",
    "apollohospitals.com",
    "who.int",
    "clevelandclinic.org",
    "healthline.com",
]


def _get_client() -> TavilyClient:
    """Initialize Tavily client using medreport-specific API key."""
    if not TAVILY_API_KEY:
        raise ValueError("MEDREPORT_TAVILY_API_KEY is not set in .env")
    return TavilyClient(api_key=TAVILY_API_KEY)


def search_reference_range(parameter_name: str, unit: str = "") -> dict:
    """Search for normal reference range of a medical parameter."""
    client = _get_client()
    domain_filter = " OR ".join(f"site:{d}" for d in TRUSTED_DOMAINS[:3])
    query = f'"{parameter_name}" normal reference range {unit} {domain_filter}'

    try:
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=5,
            include_domains=TRUSTED_DOMAINS,
        )

        results = response.get("results", [])
        snippets = []
        source_url = ""
        source_name = ""

        for r in results:
            content = r.get("content", "")
            url = r.get("url", "")
            if content:
                snippets.append(content)
            if not source_url and url:
                source_url = url
                try:
                    from urllib.parse import urlparse
                    source_name = urlparse(url).netloc.replace("www.", "")
                except Exception:
                    source_name = "web"

        return {
            "snippets": snippets,
            "source_url": source_url,
            "source_name": source_name,
            "query": query,
        }
    except Exception as e:
        return {
            "snippets": [],
            "source_url": "",
            "source_name": "",
            "query": query,
            "error": str(e),
        }


def is_cache_stale(fetched_at: datetime, max_age_days: int = 30) -> bool:
    """Check if a cached reference range is older than max_age_days."""
    if fetched_at is None:
        return True
    now = datetime.now(timezone.utc)
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    return (now - fetched_at) > timedelta(days=max_age_days)
