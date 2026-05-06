# ============================================================
#  test_tavily.py
#  Run this FIRST to verify Tavily is working.
#
#  Run: python test_tavily.py
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend folder
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

from langchain_tavily import TavilySearch

def test_tavily():
    key = os.getenv("TAVILY_API_KEY", "")
    if not key:
        print("❌ TAVILY_API_KEY not found in .env")
        print("   Add this to backend/.env:")
        print("   TAVILY_API_KEY=tvly-...")
        print("   Get free key at: https://tavily.com")
        return False

    print(f"✅ TAVILY_API_KEY found: ...{key[-6:]}")

    try:
        print("\n🔍 Searching MedlinePlus for CBC info...")
        tool = TavilySearch(
            max_results=3,
            search_depth="advanced",
            include_domains=["medlineplus.gov", "healthline.com"],
        )
        raw = tool.invoke({"query": "CBC complete blood count normal ranges hemoglobin"})

        # TavilySearch returns a dict with 'results' key
        if isinstance(raw, dict):
            result_list = raw.get("results", [])
        elif isinstance(raw, list):
            result_list = raw
        else:
            result_list = []

        if not result_list:
            print(f"❌ No results. Raw response keys: {list(raw.keys()) if isinstance(raw, dict) else type(raw)}")
            return False

        print(f"✅ Got {len(result_list)} results\n")
        for i, r in enumerate(result_list[:3], 1):
            print(f"  Result {i}:")
            if isinstance(r, dict):
                print(f"    URL    : {r.get('url', 'N/A')}")
                print(f"    Title  : {r.get('title', 'N/A')}")
                print(f"    Content: {r.get('content', '')[:150]}...")
            else:
                print(f"    Content: {str(r)[:150]}...")
            print()

        print("✅ Tavily is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Tavily error: {e}")
        return False


if __name__ == "__main__":
    success = test_tavily()
    print("\n" + ("="*50))
    print("RESULT:", "✅ PASS — Tavily ready" if success else "❌ FAIL — Fix Tavily first")
    print("="*50)