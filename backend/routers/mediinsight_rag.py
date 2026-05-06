# ============================================================
#  routers/mediinsight_rag.py — Orchestrator (7-step pipeline)
# ============================================================

import re, json, logging
from typing import List, Dict, Any, Tuple, Optional

from routers.mediinsight_config import (
    ALLOWED_TYPES, REJECTED_KW, STANDARD_RANGES, TRUSTED_SOURCES, KEY_PARAMS
)
from routers.mediinsight_tavily import (
    retrieve_medical_data, build_context,
    get_param_significance, is_sufficient
)
from routers.mediinsight_gemini import (
    call_gemini, parse_json,
    extract_params_from_gemini,
    generate_summary_direct,
    get_comparison_summary,
    list_configured_keys,
)

logger = logging.getLogger("mediinsight.core")


# ── Step 1: Input preprocessing ───────────────────────────────
def preprocess_input(report_type: str, extracted_text: str,
                     patient_context: Dict) -> Dict:
    if report_type not in ALLOWED_TYPES:
        raise ValueError(f"'{report_type}' is not a supported lab report type.")
    text_lower = extracted_text.lower()
    for kw in REJECTED_KW:
        if kw in text_lower:
            raise ValueError(f"Imaging report detected ('{kw}'). Only lab reports accepted.")
    clean_text = re.sub(r"\s+", " ", extracted_text).strip()
    if len(clean_text) < 50:
        raise ValueError("Report text too short. Upload a valid lab report.")
    whose    = patient_context.get("whose", "Myself")
    relation = patient_context.get("relation", "")
    gender   = patient_context.get("gender", "general")
    subject  = f"{relation} ({whose})" if relation else whose
    return {
        "report_type":     report_type,
        "clean_text":      clean_text,
        "whose":           whose,
        "relation":        relation,
        "gender":          gender,
        "subject":         subject,
        "patient_context": patient_context,
    }


# ── Normal range helpers ──────────────────────────────────────
def get_normal_range(name: str, gender: str = "general",
                     report_range: str = "") -> str:
    """Look up normal range. Use report's own range as fallback."""
    key = name.lower().strip()
    for k, v in STANDARD_RANGES.items():
        if k == key or k in key or key in k:
            r = v.get(gender, v.get("general", "—"))
            if r and r != "—":
                return r
    # Use range from the report itself if our table doesn't have it
    if report_range and report_range.strip() not in ("", "—", "-"):
        return report_range.strip()
    return "—"


def determine_status(value: float, nr: str) -> str:
    if not nr or nr == "—":
        return "Unknown"
    try:
        nums = re.findall(r"[\d.]+", nr)
        if not nums:
            return "Unknown"
        if nr.strip().startswith("<"):
            hi = float(nums[0])
            if value <= hi:       return "Normal"
            if value <= hi*1.1:   return "Borderline"
            return "High"
        if nr.strip().startswith(">"):
            lo = float(nums[0])
            if value >= lo:       return "Normal"
            if value >= lo*0.9:   return "Borderline"
            return "Low"
        if len(nums) >= 2:
            lo, hi = float(nums[0]), float(nums[1])
            if lo <= value <= hi: return "Normal"
            if value < lo:
                return "Borderline" if (lo-value)/lo < 0.1 else "Low"
            return "Borderline" if (value-hi)/hi < 0.1 else "High"
    except Exception:
        pass
    return "Unknown"


def build_chart_data(params: List[Dict]) -> List[Dict]:
    chart = []
    for p in params:
        nums = re.findall(r"[\d.]+", p.get("normal_range", ""))
        nr   = p.get("normal_range", "")
        lo = hi = None
        if nr.startswith("<") and nums:    lo, hi = 0.0, float(nums[0])
        elif nr.startswith(">") and nums:  lo, hi = float(nums[0]), float(nums[0])*2
        elif len(nums) >= 2:               lo, hi = float(nums[0]), float(nums[1])
        if lo is not None:
            chart.append({
                "name":        p["name"],
                "value":       p["value"],
                "unit":        p["unit"],
                "normal_low":  lo,
                "normal_high": hi,
                "status":      p["status"],
            })
    return chart


# ── Built-in significance notes (no API call needed) ──────────
_SIG_TABLE: Dict[str, Dict[str, str]] = {
    # CBC
    "hemoglobin": {
        "Low": "Low haemoglobin may indicate anaemia, which can cause fatigue and reduced oxygen delivery to tissues.",
        "High": "High haemoglobin may indicate dehydration, polycythaemia, or living at high altitude.",
        "Normal": "Haemoglobin is within the normal range, indicating healthy red blood cell oxygen-carrying capacity.",
    },
    "packed cell volume": {
        "Low": "Low PCV/haematocrit may indicate anaemia or blood loss.",
        "High": "High PCV may indicate dehydration or polycythaemia.",
        "Normal": "PCV is normal, indicating a healthy proportion of red blood cells.",
    },
    "pcv": {
        "Low": "Low PCV may indicate anaemia or blood loss.",
        "High": "High PCV may indicate dehydration or polycythaemia.",
        "Normal": "PCV is within normal range.",
    },
    "rbc": {
        "Low": "Low RBC count may indicate anaemia or nutritional deficiency.",
        "High": "High RBC count may indicate dehydration or polycythaemia.",
        "Normal": "RBC count is normal.",
    },
    "mcv": {
        "Low": "Low MCV (microcytosis) may indicate iron deficiency anaemia or thalassaemia.",
        "High": "High MCV (macrocytosis) may indicate B12 or folate deficiency.",
        "Normal": "MCV is normal, indicating typical red blood cell size.",
    },
    "mch": {
        "Low": "Low MCH may indicate iron deficiency or thalassaemia.",
        "High": "High MCH may indicate B12 or folate deficiency.",
        "Normal": "MCH is within normal range.",
    },
    "mchc": {
        "Low": "Low MCHC may indicate iron deficiency anaemia.",
        "High": "High MCHC may indicate hereditary spherocytosis.",
        "Normal": "MCHC is normal.",
    },
    "rdw": {
        "High": "High RDW indicates variation in red blood cell size, commonly seen in nutritional anaemias.",
        "Low": "Low RDW is generally not clinically significant.",
        "Normal": "RDW is normal, indicating uniform red blood cell size.",
    },
    "wbc": {
        "Low": "Low WBC (leucopaenia) may indicate viral infection, bone marrow suppression, or autoimmune conditions.",
        "High": "High WBC (leucocytosis) may indicate bacterial infection, inflammation, or stress response.",
        "Normal": "WBC count is normal, suggesting a healthy immune system.",
    },
    "tlc": {
        "Low": "Low TLC may indicate viral infection or bone marrow suppression.",
        "High": "High TLC may indicate infection or inflammation.",
        "Normal": "Total leukocyte count is normal.",
    },
    "neutrophils": {
        "Low": "Low neutrophils may increase susceptibility to bacterial infections.",
        "High": "High neutrophils are commonly associated with bacterial infection or physical stress.",
        "Normal": "Neutrophil count is normal.",
    },
    "lymphocytes": {
        "Low": "Low lymphocytes may indicate viral illness, immune suppression, or stress.",
        "High": "High lymphocytes may indicate viral infection or chronic lymphocytic conditions.",
        "Normal": "Lymphocyte count is normal.",
    },
    "monocytes": {
        "High": "High monocytes may indicate chronic infection, inflammation, or recovery from illness.",
        "Low": "Low monocytes are rarely clinically significant.",
        "Normal": "Monocyte count is normal.",
    },
    "eosinophils": {
        "High": "High eosinophils may indicate allergic conditions, asthma, or parasitic infection.",
        "Low": "Low eosinophils are generally not significant.",
        "Normal": "Eosinophil count is normal.",
    },
    "basophils": {
        "High": "High basophils may be associated with allergic reactions or inflammatory conditions.",
        "Normal": "Basophil count is normal.",
    },
    "platelet count": {
        "Low": "Low platelets (thrombocytopaenia) may increase bleeding risk.",
        "High": "High platelets may indicate inflammation, iron deficiency, or reactive thrombocytosis.",
        "Normal": "Platelet count is normal.",
    },
    "mean platelet volume": {
        "Low": "Low MPV may indicate bone marrow suppression.",
        "High": "High MPV may indicate platelet activation or cardiovascular risk.",
        "Normal": "Mean platelet volume is normal.",
    },
    # LFT
    "alt": {
        "High": "Elevated ALT/SGPT may indicate liver inflammation, fatty liver, or hepatitis.",
        "Normal": "ALT is normal, suggesting healthy liver cell function.",
    },
    "ast": {
        "High": "Elevated AST/SGOT may indicate liver damage, muscle injury, or cardiac issues.",
        "Normal": "AST is within normal range.",
    },
    "alp": {
        "High": "Elevated ALP may indicate liver or bile duct disease, or bone disorders.",
        "Normal": "Alkaline phosphatase is normal.",
    },
    "bilirubin": {
        "High": "Elevated bilirubin may indicate liver disease, haemolysis, or bile duct obstruction (jaundice).",
        "Normal": "Bilirubin is within normal range.",
    },
    "albumin": {
        "Low": "Low albumin may indicate malnutrition, liver disease, or chronic illness.",
        "Normal": "Albumin is normal, suggesting adequate protein status.",
    },
    # Lipid
    "cholesterol": {
        "High": "High cholesterol increases cardiovascular disease risk and may be related to diet or genetics.",
        "Normal": "Total cholesterol is within the optimal range.",
    },
    "ldl": {
        "High": "High LDL ('bad cholesterol') increases the risk of arterial plaque and heart disease.",
        "Normal": "LDL cholesterol is within the optimal range.",
    },
    "hdl": {
        "Low": "Low HDL ('good cholesterol') is associated with increased cardiovascular risk.",
        "High": "High HDL is generally protective against heart disease.",
        "Normal": "HDL cholesterol is at a healthy level.",
    },
    "triglycerides": {
        "High": "High triglycerides may be associated with poor diet, obesity, or metabolic syndrome.",
        "Normal": "Triglycerides are within the normal range.",
    },
    "vldl": {
        "High": "High VLDL is associated with elevated triglycerides and cardiovascular risk.",
        "Normal": "VLDL cholesterol is within normal range.",
    },
    "non-hdl": {
        "High": "High non-HDL cholesterol indicates elevated total atherogenic lipoproteins.",
        "Normal": "Non-HDL cholesterol is within the acceptable range.",
    },
    # Thyroid
    "tsh": {
        "High": "High TSH may indicate an underactive thyroid (hypothyroidism).",
        "Low": "Low TSH may indicate an overactive thyroid (hyperthyroidism).",
        "Normal": "TSH is normal, suggesting balanced thyroid function.",
    },
    "t3": {
        "High": "High T3 may indicate hyperthyroidism.",
        "Low": "Low T3 may indicate hypothyroidism.",
        "Normal": "T3 is within normal range.",
    },
    "t4": {
        "High": "High T4 may indicate hyperthyroidism.",
        "Low": "Low T4 may indicate hypothyroidism.",
        "Normal": "T4 is within normal range.",
    },
    "free t3": {
        "High": "High Free T3 may indicate hyperthyroidism.",
        "Low": "Low Free T3 may suggest hypothyroidism.",
        "Normal": "Free T3 is normal.",
    },
    "free t4": {
        "High": "High Free T4 may indicate hyperthyroidism.",
        "Low": "Low Free T4 may indicate hypothyroidism.",
        "Normal": "Free T4 is within normal range.",
    },
    # Glucose
    "glucose": {
        "High": "High blood glucose may indicate diabetes or pre-diabetes and warrants further evaluation.",
        "Low": "Low blood glucose (hypoglycaemia) may cause dizziness and fatigue.",
        "Normal": "Blood glucose is within the normal fasting range.",
    },
    "hba1c": {
        "High": "Elevated HbA1c indicates prolonged high blood sugar, associated with diabetes.",
        "Normal": "HbA1c is normal, suggesting good long-term blood sugar control.",
    },
    # RFT
    "creatinine": {
        "High": "High creatinine may indicate reduced kidney function or dehydration.",
        "Normal": "Creatinine is normal, suggesting healthy kidney filtration.",
    },
    "urea": {
        "High": "High urea may indicate kidney disease, dehydration, or high protein diet.",
        "Normal": "Urea is within normal range.",
    },
    # ESR/CRP
    "esr": {
        "High": "Elevated ESR is a non-specific marker of inflammation, infection, or autoimmune conditions.",
        "Normal": "ESR is within normal range.",
    },
    "crp": {
        "High": "Elevated CRP is a marker of active inflammation or infection in the body.",
        "Normal": "CRP is within normal range, suggesting no significant acute inflammation.",
    },
    # Iron
    "ferritin": {
        "Low": "Low ferritin indicates depleted iron stores, often seen in iron deficiency anaemia.",
        "High": "High ferritin may indicate iron overload, inflammation, or liver disease.",
        "Normal": "Ferritin is normal, indicating adequate iron stores.",
    },
    "serum iron": {
        "Low": "Low serum iron may indicate iron deficiency or chronic disease.",
        "High": "High serum iron may indicate iron overload or haemochromatosis.",
        "Normal": "Serum iron is within normal range.",
    },
}


def _get_builtin_significance(name: str, status: str) -> str:
    """Look up a pre-written significance note — zero API calls."""
    key = name.lower().strip()
    # Try exact match first
    for k, v in _SIG_TABLE.items():
        if k == key or k in key or key in k:
            note = v.get(status) or v.get("Normal", "")
            if note:
                return note
    return ""


# ── Main pipeline ─────────────────────────────────────────────
def analyze_report(report_type: str, extracted_text: str,
                   report_id: int, patient_context: Dict,
                   gender: str = "general") -> Dict[str, Any]:

    # Step 1: Preprocess
    inputs = preprocess_input(report_type, extracted_text,
                              {**patient_context, "gender": gender})
    logger.info(f"[Step1] Input ready for {inputs['subject']}")

    # Step 2: Tavily retrieval
    scraped   = retrieve_medical_data(report_type)
    tavily_ok = is_sufficient(scraped)
    logger.info(f"[Step2] Tavily: {'✅ data retrieved' if tavily_ok else '⚠️ fallback mode'}")

    # Step 3: Context building
    context = build_context(scraped, report_type) if tavily_ok else ""
    logger.info(f"[Step3] Context: {len(context)} chars")

    # Step 4: Extract parameters (returns list directly, no JSON parsing issues)
    logger.info("[Step4] Extracting parameters…")
    raw_params = extract_params_from_gemini(report_type, inputs["clean_text"])
    logger.info(f"[Step4] Got {len(raw_params)} parameters")

    # Enrich each parameter (NO per-param Gemini calls here)
    enriched = []
    for p in raw_params:
        name = p.get("name", "")
        try:    val = float(p.get("value", 0))
        except: continue
        unit         = p.get("unit", "")
        report_range = p.get("report_range", "")
        nr   = get_normal_range(name, gender, report_range)
        stat = determine_status(val, nr)

        # Significance from scraped data first (free, no API call)
        sig = get_param_significance(name, scraped)
        if not sig:
            # Use built-in lookup table (also free, no API call)
            sig = _get_builtin_significance(name, stat)
        if not sig:
            sig = f"{name} is {stat.lower()}."

        enriched.append({
            "name":         name,
            "value":        val,
            "unit":         unit,
            "raw_value":    p.get("raw_value", f"{val} {unit}"),
            "normal_range": nr,
            "status":       stat,
            "significance": sig,
            "source":       "Tavily / MedlinePlus" if tavily_ok else "Built-in reference",
        })

    # ── Filter to key parameters only ────────────────────────
    # Remove derived/irrelevant values (Mentzer Index, Others, etc.)
    key_names = [k.lower() for k in KEY_PARAMS.get(report_type, [])]
    if key_names:
        filtered = []
        for p in enriched:
            pname = p["name"].lower()
            # Keep if name matches any key param (partial match allowed)
            if any(kn in pname or pname in kn for kn in key_names):
                filtered.append(p)
        enriched = filtered if filtered else enriched  # fallback if nothing matched
    logger.info(f"[Filter] {len(enriched)} key parameters after filtering")
    summary = generate_summary_direct(
        report_type     = report_type,
        subject         = inputs["subject"],
        report_text     = inputs["clean_text"],
        enriched_params = enriched,
        scraped_context = context,
    )
    logger.info(f"[Step5] Summary done: {summary['overall_summary'][:80]}")

    # Step 7: Return structured output
    return {
        "report_type":     report_type,
        "patient_context": inputs["patient_context"],
        "subject":         inputs["subject"],
        "parameters":      enriched,
        "summary":         summary,
        "chart_data":      build_chart_data(enriched),
        "scraped_sources": list(TRUSTED_SOURCES.get(report_type, [])),
        "tavily_used":     tavily_ok,
        "model_used":      "gemini-2.5-flash",
        "disclaimer":      "MediInsight provides educational insights only. Always consult a qualified physician.",
    }


# ── Comparison ────────────────────────────────────────────────
def compare_reports(report_type: str,
                    curr_result: Dict, prev_result: Dict) -> Dict:
    cp = {p["name"]: p for p in curr_result.get("parameters", [])}
    pp = {p["name"]: p for p in prev_result.get("parameters", [])}

    comparisons = []
    for name in set(cp) & set(pp):
        try:
            cv, pv = float(cp[name]["value"]), float(pp[name]["value"])
            diff   = cv - pv
            trend  = "Stable" if abs(diff)<0.001 else ("Increasing" if diff>0 else "Decreasing")
        except Exception:
            trend = "Stable"
        comparisons.append({
            "parameter":      name,
            "previous":       pp[name]["raw_value"],
            "current":        cp[name]["raw_value"],
            "trend":          trend,
            "interpretation": (
                f"{name} has {trend.lower()} from "
                f"{pp[name]['raw_value']} to {cp[name]['raw_value']}."
            ),
        })

    overall = ""
    if comparisons:
        trend_desc = ", ".join(
            f"{c['parameter']} is {c['trend'].lower()}"
            for c in comparisons[:6]
        )
        overall = get_comparison_summary(report_type, trend_desc)
        overall = re.sub(r"[{}\[\]\"]", "", overall or "").strip()
    if not overall:
        overall = "Several parameters have changed between the two reports."

    return {
        "comparisons":   comparisons,
        "overall_trend": overall,
        "disclaimer":    "Educational only. Please consult a qualified physician.",
    }