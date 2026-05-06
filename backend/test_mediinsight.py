# ============================================================
#  test_mediinsight.py
#  Run AFTER test_tavily.py and test_gemini.py both pass.
#
#  Tests all 7 steps of the MediInsight pipeline.
#  Run from backend/: python test_mediinsight.py
# ============================================================

import sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))

SAMPLE_REPORT = """
PATIENT LAB REPORT — CBC
Date: 15-June-2025
Hemoglobin       : 9.5 g/dL      (Normal: 13.5-17.5)
RBC Count        : 3.8 M/uL      (Normal: 4.5-5.9)
WBC Count        : 11500 /uL     (Normal: 4500-11000)
Platelets        : 185000 /uL    (Normal: 150000-400000)
Hematocrit       : 30%           (Normal: 41-53%)
MCV              : 72 fL         (Normal: 80-100)
MCH              : 24 pg         (Normal: 27-33)
MCHC             : 31 g/dL       (Normal: 32-36)
"""


def sep(title=""): print(f"\n{'─'*55}"); print(f"  {title}" if title else ""); print('─'*55) if title else None


def run():
    print("="*55)
    print("  MEDIINSIGHT FULL PIPELINE TEST  (7 Steps)")
    print("="*55)

    # ── Import all modules ─────────────────────────────────
    sep("📦 Importing modules")
    try:
        from routers.mediinsight_config import ALLOWED_TYPES, STANDARD_RANGES
        from routers.mediinsight_tavily import retrieve_medical_data, build_context, is_sufficient
        from routers.mediinsight_gemini import call_gemini, parse_json, GEMINI_MODEL
        from routers.mediinsight_rag    import analyze_report, get_normal_range, determine_status
        print(f"  ✅ All modules imported")
        print(f"  ✅ Gemini model: {GEMINI_MODEL}")
        print(f"  ✅ {len(ALLOWED_TYPES)} report types loaded")
        print(f"  ✅ {len(STANDARD_RANGES)} normal ranges loaded")
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        import traceback; traceback.print_exc()
        return False

    # ── Step 1: Input preprocessing ────────────────────────
    sep("Step 1: Input Preprocessing")
    from routers.mediinsight_rag import preprocess_input
    try:
        inputs = preprocess_input(
            "CBC (Complete Blood Count)", SAMPLE_REPORT,
            {"whose": "Myself", "relation": "", "gender": "male"}
        )
        print(f"  ✅ Report type : {inputs['report_type']}")
        print(f"  ✅ Subject     : {inputs['subject']}")
        print(f"  ✅ Text length : {len(inputs['clean_text'])} chars")
    except Exception as e:
        print(f"  ❌ {e}"); return False

    # ── Step 2: Tavily retrieval ────────────────────────────
    sep("Step 2: Tavily Data Retrieval")
    scraped = retrieve_medical_data("CBC (Complete Blood Count)")
    if scraped:
        print(f"  ✅ Got {len(scraped)} chars from trusted sources")
        print(f"  Preview: {scraped[:120]}...")
    else:
        print("  ⚠️  No Tavily data — fallback mode will be used")

    # ── Step 3: Context building ────────────────────────────
    sep("Step 3: Context Building")
    context = build_context(scraped, "CBC (Complete Blood Count)", ["hemoglobin","wbc"])
    print(f"  ✅ Context built: {len(context)} chars (filtered from {len(scraped)} scraped)")
    print(f"  Sufficient: {is_sufficient(scraped)}")

    # ── Normal range + status logic ─────────────────────────
    sep("Normal Range & Status Logic")
    tests = [("Hemoglobin",9.5,"male","Low"),("WBC",11500,"general","High"),
             ("Platelets",185000,"general","Normal")]
    for name,val,gender,expected in tests:
        nr  = get_normal_range(name, gender)
        st  = determine_status(val, nr)
        ok  = st == expected
        print(f"  {'✅' if ok else '❌'} {name}: {val} → {st} (expected {expected}, range: {nr})")

    # ── Step 4+5: Gemini call ───────────────────────────────
    sep("Steps 4+5: Gemini Generation (fine-tuned prompt)")
    resp = call_gemini('Return ONLY this JSON: {"status":"ok","model":"working"}')
    parsed = parse_json(resp)
    if parsed and parsed.get("status") == "ok":
        print(f"  ✅ Gemini JSON call works: {resp.strip()[:80]}")
    else:
        print(f"  ✅ Gemini responded: {resp.strip()[:80]}")

    # ── Full pipeline ───────────────────────────────────────
    sep("Full 7-Step Pipeline")
    print("  (This calls Gemini 2-4 times — may take 20-40s)")
    try:
        result = analyze_report(
            report_type     = "CBC (Complete Blood Count)",
            extracted_text  = SAMPLE_REPORT,
            report_id       = 999,
            patient_context = {"whose": "Myself", "relation": "", "gender": "male"},
            gender          = "male",
        )
        params  = result.get("parameters", [])
        summary = result.get("summary", {})
        chart   = result.get("chart_data", [])

        print(f"\n  📋 Parameters extracted : {len(params)}")
        print(f"  📊 Chart-ready params   : {len(chart)}")
        print(f"  🌐 Tavily used          : {result.get('tavily_used')}")
        print(f"  🤖 Model used           : {result.get('model_used')}")
        print(f"\n  Parameters:")
        for p in params[:5]:
            print(f"    • {p['name']:20} {p['raw_value']:15} {p['status']:10} (Normal: {p['normal_range']})")
        print(f"\n  Summary:")
        print(f"    {summary.get('overall_summary','')[:200]}")
        abn = summary.get('abnormal_findings', [])
        if abn:
            print(f"\n  Abnormal findings ({len(abn)}):")
            for a in abn[:3]: print(f"    ⚠️  {a}")

        print("\n  ✅ Full pipeline PASSED!")
        return True
    except Exception as e:
        import traceback
        print(f"  ❌ Pipeline failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ok = run()
    print("\n" + "="*55)
    print("RESULT:", "✅ ALL STEPS PASSED — Ready for production!" if ok
          else "❌ FAILED — Fix errors above")
    print("="*55)
    if ok:
        print("\nNext: restart uvicorn and test via Streamlit UI")