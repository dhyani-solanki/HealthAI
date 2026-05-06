# ============================================================
#  routers/mediinsight_gemini.py  — MULTI-KEY GEMINI
#
#  Each task uses its OWN Gemini API key so quota never runs out:
#
#  GEMINI_KEY_EXTRACTION  → extracting parameters from PDF text
#  GEMINI_KEY_SUMMARY     → generating overall summary
#  GEMINI_KEY_SIGNIFICANCE→ per-parameter clinical notes
#  GEMINI_KEY_COMPARISON  → comparing two reports
#  GEMINI_API_KEY         → fallback if specific key not set
#
#  All keys are FREE from https://aistudio.google.com/apikey
#  Each key = 20 free requests/day = 20 separate analyses/day per task
#
#  Add to backend/.env:
#    GEMINI_KEY_EXTRACTION=AIza...    ← key 1
#    GEMINI_KEY_SUMMARY=AIza...       ← key 2
#    GEMINI_KEY_SIGNIFICANCE=AIza...  ← key 3
#    GEMINI_KEY_COMPARISON=AIza...    ← key 4
#    GEMINI_API_KEY=AIza...           ← key 5 (master fallback)
# ============================================================

import os, re, json, logging, time
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests as _requests

logger    = logging.getLogger("mediinsight.gemini")
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

GEMINI_MODEL = "gemini-2.5-flash"
_BASE_URL    = "https://generativelanguage.googleapis.com/v1beta/models"
_GEMINI_URL  = f"{_BASE_URL}/{GEMINI_MODEL}:generateContent"

# ── Task → Key name mapping ───────────────────────────────────
# Each task uses a specific key from .env
TASK_KEY_MAP = {
    "extraction":   "GEMINI_KEY_EXTRACTION",    # extracting params from PDF
    "summary":      "GEMINI_KEY_SUMMARY",        # overall summary generation
    "significance": "GEMINI_KEY_SIGNIFICANCE",   # per-param clinical notes
    "comparison":   "GEMINI_KEY_COMPARISON",     # report comparison
    "default":      "GEMINI_API_KEY",            # fallback for anything else
}


# ── Read any key from .env file directly ──────────────────────
def _read_env(key_name: str) -> str:
    """Read a specific key from .env — bypasses SDK preferences."""
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == key_name:
                val = v.strip().strip('"').strip("'")
                if val:
                    return val
    return os.environ.get(key_name, "").strip()


def get_key_for_task(task: str) -> str:
    """
    Get the API key for a specific task.
    Falls back through: task key → master key → any available key.
    """
    # Try task-specific key first
    specific_name = TASK_KEY_MAP.get(task, "GEMINI_API_KEY")
    key = _read_env(specific_name)
    if key:
        logger.info(f"[Key] Using {specific_name} for task '{task}'")
        return key

    # Try master fallback key
    key = _read_env("GEMINI_API_KEY")
    if key:
        logger.warning(f"[Key] {specific_name} not set — using GEMINI_API_KEY for task '{task}'")
        return key

    # Try any other configured key
    for name in TASK_KEY_MAP.values():
        key = _read_env(name)
        if key:
            logger.warning(f"[Key] Using {name} as emergency fallback for task '{task}'")
            return key

    logger.error("[Key] No Gemini API key found in .env!")
    return ""


def list_configured_keys() -> Dict[str, str]:
    """Returns which keys are configured — for health check endpoint."""
    result = {}
    for task, env_name in TASK_KEY_MAP.items():
        key = _read_env(env_name)
        result[task] = f"✅ {env_name} set (...{key[-6:]})" if key else f"❌ {env_name} not set"
    return result


# ── Response extractor ────────────────────────────────────────
def _extract_text(data: dict) -> str:
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        pass
    try:
        return data["candidates"][0]["content"]["text"].strip()
    except Exception:
        pass
    return ""


# ═══════════════════════════════════════════════════════════════
#  CORE AI CALL — via Bytez API
# ═══════════════════════════════════════════════════════════════
def call_gemini(prompt: str, task: str = "default", max_retries: int = 2) -> str:
    """
    Call Gemini via Bytez API gateway.
    Keeps same function signature for backward compat.
    """
    from services.bytez_client import call_bytez
    text = call_bytez(prompt, temperature=0.1, max_tokens=3000)
    if text:
        logger.info(f"[Bytez/{task}] ✅ {text[:100]}")
    else:
        logger.warning(f"[Bytez/{task}] Empty response")
    return text


# ── JSON parser ───────────────────────────────────────────────
def _escape_in_strings(text: str) -> str:
    out, in_str, i = [], False, 0
    while i < len(text):
        ch = text[i]
        if ch == '\\' and in_str and i+1 < len(text):
            out.append(ch); out.append(text[i+1]); i += 2; continue
        if ch == '"':
            in_str = not in_str; out.append(ch)
        elif in_str and ch == '\n': out.append('\\n')
        elif in_str and ch == '\r': out.append('\\r')
        elif in_str and ch == '\t': out.append('\\t')
        else: out.append(ch)
        i += 1
    return "".join(out)


def parse_json(text: str) -> Optional[dict]:
    if not text:
        return None
    t = re.sub(r"```json\s*","",text)
    t = re.sub(r"```\s*","",t).strip()
    for a in [t, _escape_in_strings(t), t.replace("\n"," "),
              re.sub(r",\s*([}\]])",r"\1",t)]:
        try: return json.loads(a)
        except: pass
    s, e = t.find("{"), t.rfind("}")
    if s!=-1 and e>s:
        c = t[s:e+1]
        for a in [c, _escape_in_strings(c), c.replace("\n"," "),
                  re.sub(r",\s*([}\]])",r"\1",c)]:
            try: return json.loads(a)
            except: pass
    return None


# ── System role ───────────────────────────────────────────────
SYSTEM_ROLE = (
    "You are MediInsight, a medical educational assistant. "
    "Explain lab results simply and empathetically. "
    "NEVER diagnose. NEVER prescribe. "
    "Use 'may indicate', 'commonly associated with'. "
    "Be reassuring and accurate."
)


# ═══════════════════════════════════════════════════════════════
#  TASK 1 — EXTRACTION  (uses GEMINI_KEY_EXTRACTION)
# ═══════════════════════════════════════════════════════════════
_EXTRACT_GUIDE: Dict[str, str] = {
    "CBC (Complete Blood Count)": (
        "Extract: Hemoglobin/Haemoglobin, Packed Cell Volume/PCV/Hematocrit, RBC Count, "
        "MCV, MCH, MCHC, RDW, Total Leukocyte Count/TLC/WBC, Segmented Neutrophils, "
        "Lymphocytes, Monocytes, Eosinophils, Basophils, Platelet Count, Mean Platelet Volume/MPV. "
        "SKIP: Mentzer Index, Band Forms, Metamyelocytes, Myelocytes, Promyelocytes, Blasts, Others. "
        "If Neutrophils/Lymphocytes appear both as % and absolute (thou/mm3), take the % version."
    ),
    "Liver Function Test (LFT)": (
        "Extract: ALT/SGPT, AST/SGOT, ALP/Alkaline Phosphatase, GGT/Gamma GT, "
        "Total Bilirubin, Direct Bilirubin, Indirect Bilirubin, Albumin, Total Protein, Globulin. "
        "SKIP: Calculated ratios like AST/ALT ratio."
    ),
    "Renal Function Test (RFT)": (
        "Extract: Creatinine, Urea/Blood Urea/BUN, Uric Acid, Sodium, Potassium, "
        "Chloride, Calcium, Magnesium, Phosphorus, eGFR/GFR if present. "
        "SKIP: Urea/Creatinine ratio."
    ),
    "Lipid Profile": (
        "Extract ALL of these — do not skip any: "
        "Total Cholesterol/Cholesterol Total, Triglycerides, HDL Cholesterol, "
        "LDL Cholesterol/LDL Cholesterol Direct, VLDL Cholesterol, Non-HDL Cholesterol."
    ),
    "Thyroid Function Test": (
        "Extract: TSH, Total T3, Total T4, Free T3/FT3, Free T4/FT4. "
        "SKIP: Anti-TPO, Anti-Thyroglobulin unless they have a numeric result."
    ),
    "Blood Glucose / HbA1c": (
        "Extract: Fasting Blood Glucose/FBS, HbA1c/Glycated Haemoglobin, "
        "Post Prandial Glucose/PPBS, Random Blood Glucose if present."
    ),
    "Electrolyte Panel": (
        "Extract: Sodium, Potassium, Chloride, Bicarbonate/CO2, "
        "Calcium, Magnesium, Phosphorus/Phosphate."
    ),
    "ESR / CRP": (
        "Extract: ESR (Erythrocyte Sedimentation Rate), "
        "CRP (C-Reactive Protein), hs-CRP if present."
    ),
    "Iron Studies": (
        "Extract: Serum Iron, Ferritin, TIBC (Total Iron Binding Capacity), "
        "Transferrin Saturation, UIBC if present."
    ),
}


def extract_params_from_gemini(report_type: str, report_text: str) -> List[Dict]:
    """
    Extraction pipeline — minimises API calls:
    1. Regex first  → FREE, instant, handles all Dr Lal formats
    2. Gemini only  → if regex finds < 2 params (rare edge case)

    This means most analyses use ZERO Gemini calls for extraction.
    Gemini is only a last resort for unusual PDF formats.
    """
    # Step 1: Try regex first — completely free
    regex_results = _regex_fallback(report_type, report_text)
    logger.info(f"[Extraction] Regex found {len(regex_results)} params")

    if len(regex_results) >= 2:
        # Regex worked — skip Gemini entirely (save API quota)
        logger.info("[Extraction] ✅ Using regex results — Gemini call skipped")
        return regex_results

    # Step 2: Regex found nothing — try Gemini as last resort
    logger.info("[Extraction] Regex insufficient — trying Gemini")
    guide = _EXTRACT_GUIDE.get(
        report_type,
        "Extract all laboratory parameters that have a numeric result."
    )
    prompt = (
        f"Extract lab test results from this {report_type} report.\n\n"
        f"WHAT TO EXTRACT:\n{guide}\n\n"
        f"REPORT TEXT:\n{report_text[:5000]}\n\n"
        f"Values may appear in different formats:\n"
        f'  - Same line: "Cholesterol Total  150  mg/dL  <200"\n'
        f'  - Separate lines: "Hemoglobin\\n(Photometry)\\n11.00\\ng/dL"\n'
        f"  - Table: Test Name | Results | Units | Bio. Ref. Interval\n\n"
        f"Return ONLY a JSON array. No markdown. No explanation.\n"
        f'[{{"name":"Cholesterol Total","value":150,"unit":"mg/dL","raw_value":"150 mg/dL","report_range":"<200"}}]\n\n'
        f"Rules: value = plain number. Extract every parameter listed. Return [] if nothing found.\n\n"
        f"JSON array:"
    )
    raw = call_gemini(prompt, task="extraction")
    logger.info(f"[Extraction] Gemini raw ({len(raw or '')} chars): {(raw or '')[:200]}")

    if raw:
        cleaned = re.sub(r"```(?:json)?\s*","",raw).replace("```","").strip()
        s, e = cleaned.find("["), cleaned.rfind("]")
        if s != -1 and e > s:
            arr = cleaned[s:e+1]
            for attempt in [arr, _escape_in_strings(arr), arr.replace("\n"," "),
                            re.sub(r",\s*([}\]])",r"\1",arr)]:
                try:
                    result = json.loads(attempt)
                    if isinstance(result, list) and result:
                        logger.info(f"[Extraction] ✅ Gemini extracted {len(result)} params")
                        return result
                except Exception:
                    pass

    logger.warning("[Extraction] Both regex and Gemini failed")
    return regex_results  # return whatever regex found (even if empty)


def _regex_fallback(report_type: str, text: str) -> List[Dict]:
    """Regex fallback — used ONLY when Gemini key is exhausted."""
    ALL_KW = [
        "Hemoglobin","Haemoglobin","Packed Cell Volume","PCV","Hematocrit",
        "RBC","MCV","MCH","MCHC","RDW","WBC","TLC","Total Leukocyte",
        "Neutrophil","Lymphocyte","Monocyte","Eosinophil","Basophil",
        "Platelet","MPV","Mean Platelet",
        "ALT","SGPT","AST","SGOT","ALP","Alkaline","GGT","Gamma",
        "Bilirubin","Albumin","Total Protein","Globulin",
        "Creatinine","Urea","BUN","Uric Acid","GFR","eGFR",
        "Sodium","Potassium","Chloride","Calcium","Magnesium","Phosphorus",
        "Cholesterol","Triglyceride","HDL","LDL","VLDL","Non-HDL",
        "TSH","T3","T4","Free T3","Free T4","FT3","FT4",
        "Glucose","HbA1c","Haemoglobin A1c","Fasting","Postprandial",
        "ESR","CRP","C-Reactive","Ferritin","TIBC","Transferrin","Serum Iron",
    ]
    SKIP_KW = ["test","result","reference","bio","page","note","national",
               "above","optimal","borderline","interpretation","recommendation"]

    params = []
    seen   = set()
    lines  = [l.strip() for l in text.replace("\r","\n").split("\n") if l.strip()]

    # ── Pattern A: Multi-space horizontal "Name    Value   unit   ref" ──
    for line in lines:
        m = re.match(r"^(.{3,60}?)\s{2,}(\d+\.?\d*)\s*([a-zA-Z/%µ][^\s]{0,14})?\s*([<>]?\s*\d[\d.\s\-–]*)?$", line)
        if not m: continue
        name_raw, val_str = m.group(1).strip(), m.group(2).strip()
        unit, ref = (m.group(3) or "").strip(), (m.group(4) or "").strip()
        if not any(kw.lower() in name_raw.lower() for kw in ALL_KW): continue
        if any(w in name_raw.lower() for w in SKIP_KW): continue
        try: val = float(val_str)
        except: continue
        clean = re.sub(r"\s*\([^)]*\)","",name_raw).strip()
        clean = re.sub(r"\s+"," ",clean)
        key = clean.lower()
        if key not in seen:
            seen.add(key)
            params.append({"name":clean,"value":val,"unit":unit,
                           "raw_value":f"{val_str} {unit}".strip(),"report_range":ref})

    # ── Pattern B: Dr Lal single-space "Cholesterol Total 150" ──────────
    # This is the exact format in B131.pdf lipid report
    if len(params) < 2:
        for idx, line in enumerate(lines):
            # Line ends with a standalone number
            m = re.match(r"^(.{3,70}?)\s+(\d+\.?\d*)$", line)
            if not m: continue
            name_raw, val_str = m.group(1).strip(), m.group(2).strip()
            if not any(kw.lower() in name_raw.lower() for kw in ALL_KW): continue
            if any(w in name_raw.lower() for w in SKIP_KW): continue
            try: val = float(val_str)
            except: continue
            # Look at following lines for unit and ref
            unit, ref = "", ""
            for look in range(idx+1, min(idx+4, len(lines))):
                nxt = lines[look].strip()
                if nxt.startswith("(") and nxt.endswith(")"): continue  # skip method notes
                um = re.match(r"^([a-zA-Z/%µ][^\s]{0,14})\s*([<>]?\s*\d[\d.\s\-–]*)?$", nxt)
                if um:
                    unit = um.group(1).strip()
                    ref  = (um.group(2) or "").strip()
                    break
                break
            clean = re.sub(r"\s*\([^)]*\)","",name_raw).strip()
            clean = re.sub(r"\s+"," ",clean)
            key = clean.lower()
            if key not in seen:
                seen.add(key)
                params.append({"name":clean,"value":val,"unit":unit,
                               "raw_value":f"{val_str} {unit}".strip(),"report_range":ref})

    # ── Pattern C: Vertical "Name\n(method)\nvalue\nunit" ───────────────
    i = 0
    while i < len(lines):
        line = lines[i]
        if any(kw.lower() in line.lower() for kw in ALL_KW) and len(line) < 90:
            for j in range(i+1, min(i+7, len(lines))):
                m = re.match(r"^(\d+\.?\d*)$", lines[j].strip())
                if m:
                    try: val = float(m.group(1))
                    except: break
                    unit = ""
                    if j+1 < len(lines):
                        u = lines[j+1].strip()
                        if len(u)<20 and re.search(r"[a-zA-Z/%µ]",u) and not re.match(r"^\d",u):
                            unit = u
                    clean = re.sub(r"\s*\([^)]*\)","",line).strip()
                    clean = re.sub(r"\s+"," ",clean)
                    key = clean.lower()
                    if key not in seen:
                        seen.add(key)
                        params.append({"name":clean,"value":val,"unit":unit,
                                       "raw_value":f"{m.group(1)} {unit}".strip(),"report_range":""})
                    break
        i += 1

    logger.info(f"[Regex] {len(params)} params for {report_type}")
    return params


# ═══════════════════════════════════════════════════════════════
#  TASK 2 — SUMMARY  (uses GEMINI_KEY_SUMMARY)
# ═══════════════════════════════════════════════════════════════
def generate_summary_direct(
    report_type: str, subject: str,
    report_text: str, enriched_params: List[Dict],
    scraped_context: str,
) -> Dict[str, Any]:
    """
    TASK 2: Generate human-friendly summary.
    Uses GEMINI_KEY_SUMMARY (20 free requests/day).
    """
    abnormal = [p for p in enriched_params if p["status"] in ("High","Low","Borderline")]
    normal   = [p for p in enriched_params if p["status"] == "Normal"]
    abn_list = [
        f"{p['name']} ({p['status']}: {p['raw_value']}, normal {p['normal_range']})"
        for p in abnormal
    ]
    abn_str = ", ".join(abn_list) if abn_list else "none detected"
    ctx     = f"\n\nFrom trusted sources:\n{scraped_context[:500]}" if scraped_context else ""

    # Overall summary (plain text — no JSON parsing needed)
    summary_text = call_gemini(
        f"{SYSTEM_ROLE}\n\n"
        f"Write 3-4 clear sentences summarising this {report_type} for {subject}.\n"
        f"Total: {len(enriched_params)} parameters. Normal: {len(normal)}. Abnormal: {len(abnormal)}.\n"
        f"Abnormal findings: {abn_str}{ctx}\n"
        f"Report excerpt:\n{report_text[:500]}\n\n"
        f"Write ONLY the summary. Plain text. No bullet points. No JSON. No headers.",
        task="summary"
    )
    summary_text = re.sub(r"[{}\[\]]","", summary_text or "").strip()
    if not summary_text:
        summary_text = (
            f"This {report_type} for {subject} shows "
            f"{len(abnormal)} value(s) outside normal range: {abn_str}."
        )

    # Possible causes (plain text)
    causes = []
    if abnormal:
        causes_raw = call_gemini(
            f"{SYSTEM_ROLE}\n\n"
            f"List 2-3 educational possible causes for: {abn_str}.\n"
            f"One cause per line. No numbering. No JSON. Plain text only.",
            task="summary"
        )
        causes = [
            c.strip(" -•*1234567890.")
            for c in (causes_raw or "").strip().split("\n")
            if c.strip() and len(c.strip()) > 10
        ][:3]
    if not causes:
        causes = ["All parameters within normal range. Consult your doctor for confirmation."]

    # Build findings from structured data (no Gemini needed)
    findings = [
        f"{p['name']} is {p['status'].lower()} at {p['raw_value']} "
        f"(normal: {p['normal_range']})"
        for p in abnormal
    ]

    return {
        "overall_summary":   summary_text,
        "abnormal_findings": findings,
        "possible_causes":   causes,
        "recommendation":    "Please share these results with your doctor for personalised advice.",
        "source_used":       "Tavily + MedlinePlus + Gemini" if scraped_context else "Gemini AI",
    }


# ═══════════════════════════════════════════════════════════════
#  TASK 3 — SIGNIFICANCE  (uses GEMINI_KEY_SIGNIFICANCE)
# ═══════════════════════════════════════════════════════════════
def get_significance(param_name: str, value: float,
                     unit: str, status: str, report_type: str) -> str:
    """
    TASK 3: Generate a 1-2 sentence clinical note for one parameter.
    Uses GEMINI_KEY_SIGNIFICANCE (20 free requests/day).
    """
    resp = call_gemini(
        f"{SYSTEM_ROLE}\n\n"
        f"In 1-2 short sentences explain what {status.lower()} {param_name} "
        f"({value} {unit}) may mean in a {report_type}. "
        f"Do NOT diagnose. Plain text only. No JSON.",
        task="significance"
    )
    return re.sub(r"[{}\[\]\"]","", resp or "").strip() or f"{param_name} is {status.lower()}."


# ═══════════════════════════════════════════════════════════════
#  TASK 4 — COMPARISON  (uses GEMINI_KEY_COMPARISON)
# ═══════════════════════════════════════════════════════════════
def get_comparison_summary(report_type: str, trend_summary: str) -> str:
    """
    TASK 4: Generate overall trend description for comparison.
    Uses GEMINI_KEY_COMPARISON (20 free requests/day).
    """
    resp = call_gemini(
        f"{SYSTEM_ROLE}\n\n"
        f"In 2 sentences describe the overall {report_type} trend where: {trend_summary}. "
        f"Educational, no diagnosis. Plain text only.",
        task="comparison"
    )
    return re.sub(r"[{}\[\]\"]","", resp or "").strip()


# ── Legacy aliases (keep rag.py working without changes) ──────
def build_significance_prompt(param_name, value, unit, status, report_type):
    return f"Explain {status} {param_name} ({value} {unit}) in {report_type}. Plain text."

def build_comparison_prompt(report_type, trend_summary):
    return f"Describe {report_type} trend: {trend_summary}. Plain text."

def build_fallback_prompt(report_type, report_text, subject):
    return f"Summarise {report_type} for {subject}. Report: {report_text[:500]}"