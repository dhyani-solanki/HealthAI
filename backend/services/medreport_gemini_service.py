# ============================================================
#  services/medreport_gemini_service.py
#  AI service for MedReport Analyzer module — uses Bytez API.
# ============================================================

import os
import json
from dotenv import load_dotenv
from services.bytez_client import call_bytez

load_dotenv(override=True)


def _parse_json_response(text: str) -> dict | list:
    """Parse JSON from Gemini response, handling markdown code blocks."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


def _keyword_classify(raw_text: str) -> str | None:
    """Fast keyword-based pre-classification to help the AI."""
    text_lower = raw_text.lower()
    kw_map = {
        "CBC (Complete Blood Count)": ["hemoglobin", "haemoglobin", "hgb", "wbc", "rbc", "platelet", "hematocrit", "mcv", "mch", "mchc", "complete blood count", "cbc"],
        "Lipid Panel": ["cholesterol", "ldl", "hdl", "triglyceride", "vldl", "lipid"],
        "Blood Glucose / HbA1c": ["glucose", "hba1c", "glycated", "fasting sugar", "blood sugar", "random sugar", "post prandial"],
        "Liver Function Test (LFT)": ["sgpt", "sgot", "alt", "ast", "bilirubin", "albumin", "alkaline phosphatase", "liver function", "lft", "ggt"],
        "Kidney Function Test / Renal Panel": ["creatinine", "bun", "urea", "egfr", "uric acid", "kidney", "renal"],
        "Thyroid Function Test (TFT)": ["tsh", "t3", "t4", "thyroid", "free t3", "free t4"],
        "Urine Analysis": ["urine", "urinalysis", "specific gravity", "urine ph"],
        "Electrolyte Panel": ["sodium", "potassium", "chloride", "bicarbonate", "electrolyte"],
    }
    scores: dict[str, int] = {}
    for report_type, keywords in kw_map.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[report_type] = score
    if scores:
        return max(scores, key=scores.get)  # type: ignore
    return None


def classify_report(raw_text: str) -> dict:
    """Classify medical report type using keyword pre-check + Bytez AI."""
    # Fast keyword hint
    keyword_hint = _keyword_classify(raw_text)
    hint_text = f"\nHINT: Keyword analysis suggests this may be a \"{keyword_hint}\" report. Verify this against the actual content.\n" if keyword_hint else ""

    prompt = f"""You are an expert medical report classifier. Your job is to determine the type of medical lab report from its text content.

IMPORTANT RULES:
- Read the parameter names, test names, and headings carefully
- Even if the report has multiple test panels, classify by the DOMINANT or PRIMARY test panel
- Do NOT default to "Unknown / Other" unless the text is truly unrecognizable as a medical report
- Common lab parameters like Hemoglobin, WBC, RBC → CBC
- Cholesterol, LDL, HDL, Triglycerides → Lipid Panel
- Glucose, HbA1c → Blood Glucose / HbA1c
- SGPT, SGOT, Bilirubin → Liver Function Test (LFT)
- Creatinine, BUN, Urea → Kidney Function Test / Renal Panel
- TSH, T3, T4 → Thyroid Function Test (TFT)
{hint_text}
Classify into ONE of these categories:
1. CBC (Complete Blood Count)
2. Lipid Panel
3. Blood Glucose / HbA1c
4. Liver Function Test (LFT)
5. Kidney Function Test / Renal Panel
6. Thyroid Function Test (TFT)
7. Urine Analysis
8. Electrolyte Panel
9. Unknown / Other (ONLY if no medical parameters are found at all)

Return ONLY a JSON object:
{{
  "report_type": "<exact category name from the list above>",
  "confidence": "<high|medium|low>",
  "reasoning": "<brief explanation>"
}}

Medical Report Text:
---
{raw_text[:10000]}
---

Return ONLY the JSON object, no other text."""

    try:
        response_text = call_bytez(prompt, temperature=0.1, max_tokens=256)
        result = _parse_json_response(response_text)
        assert "report_type" in result
        assert "confidence" in result
        assert "reasoning" in result
        # Validate report_type is in known list
        valid_types = [
            "CBC (Complete Blood Count)", "Lipid Panel", "Blood Glucose / HbA1c",
            "Liver Function Test (LFT)", "Kidney Function Test / Renal Panel",
            "Thyroid Function Test (TFT)", "Urine Analysis", "Electrolyte Panel", "Unknown / Other",
        ]
        if result["report_type"] not in valid_types:
            # Try to match partial
            for vt in valid_types:
                if result["report_type"].lower() in vt.lower() or vt.lower() in result["report_type"].lower():
                    result["report_type"] = vt
                    break
        # If AI said Unknown but keywords found a match, use keyword result
        if result["report_type"] == "Unknown / Other" and keyword_hint:
            result["report_type"] = keyword_hint
            result["confidence"] = "medium"
            result["reasoning"] = f"Classified via keyword analysis: {keyword_hint}. " + result.get("reasoning", "")
        return result
    except Exception as e:
        # Fallback to keyword classification
        if keyword_hint:
            return {
                "report_type": keyword_hint,
                "confidence": "medium",
                "reasoning": f"AI classification failed, used keyword fallback: {keyword_hint}.",
            }
        return {
            "report_type": "Unknown / Other",
            "confidence": "low",
            "reasoning": f"Classification failed: {str(e)}.",
        }


def extract_parameters(raw_text: str, report_type: str) -> list[dict]:
    """Extract clinically significant parameters based on report type."""

    param_guidance = {
        "CBC": """
Hemoglobin (Men: 13.5-17.5 g/dL, Women: 12.0-16.0 g/dL) [Source: MedlinePlus],
WBC/White Blood Cells (4,500-11,000 cells/mcL) [Source: Mayo Clinic],
RBC/Red Blood Cells (Men: 4.7-6.1 million/mcL, Women: 4.2-5.4 million/mcL) [Source: MedlinePlus],
Platelets (150,000-400,000/mcL) [Source: MedlinePlus],
Hematocrit (Men: 38.3-48.6%, Women: 35.5-44.9%) [Source: Mayo Clinic],
MCV (80-100 fL) [Source: Cleveland Clinic], MCH (27-33 pg) [Source: MedlinePlus],
MCHC (32-36 g/dL) [Source: MedlinePlus], RDW (11.5-14.5%) [Source: Cleveland Clinic]""",
        "Lipid Panel": """
Total Cholesterol (<200 desirable, 200-239 borderline, >=240 high mg/dL) [Source: American Heart Association],
LDL Cholesterol (<100 optimal, 100-129 near optimal, 130-159 borderline, >=160 high mg/dL) [Source: Mayo Clinic],
HDL Cholesterol (Men: >40, Women: >50, >60 protective mg/dL) [Source: American Heart Association],
Triglycerides (<150 normal, 150-199 borderline, >=200 high mg/dL) [Source: MedlinePlus],
VLDL (5-40 mg/dL) [Source: Cleveland Clinic]""",
        "Blood Glucose / HbA1c": """
Fasting Glucose (70-100 normal, 100-125 prediabetes, >=126 diabetes mg/dL) [Source: American Diabetes Association],
HbA1c (<5.7% normal, 5.7-6.4% prediabetes, >=6.5% diabetes) [Source: WHO / ADA],
Post-Prandial Glucose (<140 normal, 140-199 prediabetes mg/dL) [Source: American Diabetes Association],
Random Blood Sugar (<200 normal mg/dL) [Source: MedlinePlus]""",
        "Liver Function Test (LFT)": """
ALT/SGPT (7-56 U/L) [Source: Mayo Clinic], AST/SGOT (10-40 U/L) [Source: MedlinePlus],
ALP (44-147 U/L) [Source: MedlinePlus], Bilirubin Total (0.1-1.2 mg/dL) [Source: Mayo Clinic],
Bilirubin Direct (0.0-0.3 mg/dL) [Source: Cleveland Clinic],
Albumin (3.4-5.4 g/dL) [Source: MedlinePlus], Total Protein (6.0-8.3 g/dL) [Source: Mayo Clinic],
GGT (Men: 8-61, Women: 5-36 U/L) [Source: MedlinePlus]""",
        "Kidney Function Test / Renal Panel": """
Creatinine (Men: 0.74-1.35, Women: 0.59-1.04 mg/dL) [Source: Mayo Clinic],
BUN (7-20 mg/dL) [Source: MedlinePlus], eGFR (>90 normal, 60-89 mildly decreased, <60 kidney disease) [Source: National Kidney Foundation],
Uric Acid (Men: 3.4-7.0, Women: 2.4-6.0 mg/dL) [Source: Mayo Clinic],
Urea (15-40 mg/dL) [Source: Apollo Diagnostics]""",
        "Thyroid Function Test (TFT)": """
TSH (0.4-4.0 mIU/L) [Source: American Thyroid Association],
T3 (80-200 ng/dL) [Source: MedlinePlus], T4 (5.0-12.0 mcg/dL) [Source: MedlinePlus],
Free T3 (2.3-4.2 pg/mL) [Source: Mayo Clinic], Free T4 (0.8-1.8 ng/dL) [Source: Mayo Clinic]""",
        "Urine Analysis": """
pH (4.5-8.0) [Source: MedlinePlus], Specific Gravity (1.005-1.030) [Source: MedlinePlus],
Protein (Negative/Trace) [Source: Mayo Clinic], Glucose (Negative) [Source: MedlinePlus],
RBC (0-2 per HPF) [Source: Cleveland Clinic], WBC (0-5 per HPF) [Source: Cleveland Clinic]""",
        "Electrolyte Panel": """
Sodium (136-145 mEq/L) [Source: MedlinePlus], Potassium (3.5-5.0 mEq/L) [Source: Mayo Clinic],
Chloride (96-106 mEq/L) [Source: MedlinePlus], Bicarbonate (22-29 mEq/L) [Source: MedlinePlus],
Calcium (8.5-10.5 mg/dL) [Source: MedlinePlus], Magnesium (1.7-2.2 mg/dL) [Source: Mayo Clinic],
Phosphorus (2.5-4.5 mg/dL) [Source: Cleveland Clinic]""",
    }

    guidance = param_guidance.get(
        report_type,
        "Extract all measurable clinical parameters found in the report."
    )

    prompt = f"""You are a medical data extraction specialist.
Extract the clinically significant parameters from this {report_type} medical report.

REFERENCE RANGES:
{guidance}

For each parameter found:
1. Extract the exact value and unit from the report
2. Compare against reference ranges to determine status
3. Provide the normal reference range (min and max)
4. Add a brief clinical insight for abnormal values

Return ONLY a JSON object:
{{
  "parameters": [
    {{
      "name": "<parameter name>",
      "value": <numeric value>,
      "unit": "<measurement unit>",
      "status": "<low|normal|high|borderline>",
      "normal_min": <minimum normal value>,
      "normal_max": <maximum normal value>,
      "source": "<MUST be a real authoritative medical source: MedlinePlus, Mayo Clinic, Cleveland Clinic, American Heart Association, American Diabetes Association, National Kidney Foundation, American Thyroid Association, Apollo Diagnostics, WHO, or similar trusted medical institution>",
      "insight": "<brief clinical insight if abnormal, empty string if normal>"
    }}
  ]
}}

Rules:
- Only include parameters with actual numeric values
- value must be a number (int or float)
- status: "low" if below normal_min, "high" if above normal_max, "borderline" if within 5% of limits
- insight: only for non-normal values

Medical Report Text:
---
{raw_text[:8000]}
---

Return ONLY the JSON object."""

    try:
        response_text = call_bytez(prompt)
        result = _parse_json_response(response_text)
        parameters = result.get("parameters", [])
        cleaned = []
        for p in parameters:
            if all(k in p for k in ["name", "value", "unit", "status"]):
                try:
                    p["value"] = float(p["value"])
                    if p["status"] not in ("low", "normal", "high", "borderline"):
                        p["status"] = "normal"
                    p["normal_min"] = float(p.get("normal_min")) if p.get("normal_min") is not None else None
                    p["normal_max"] = float(p.get("normal_max")) if p.get("normal_max") is not None else None
                    p["source"] = p.get("source", "")
                    p["insight"] = p.get("insight", "")
                    cleaned.append(p)
                except (ValueError, TypeError):
                    continue
        return cleaned
    except Exception as e:
        raise ValueError(f"Parameter extraction failed: {str(e)}")


def generate_summary(report_type: str, parameters: list[dict]) -> str:
    """Generate a structured, human-friendly medical report summary."""

    param_text = "\n".join(
        f"- {p['name']}: {p['value']} {p['unit']} (Status: {p['status']})"
        for p in parameters
    )

    prompt = f"""You are a medical report interpretation assistant.

Analyze this {report_type} lab report with extracted values.

Generate a clear, structured, human-friendly summary following this format:

1. Overall Summary (2-3 short lines about overall status)
2. Important Abnormal / Borderline Findings (Parameter → Value → Meaning)
3. Normal / Reassuring Findings (2-4 key normal values)
4. Short Cause / Reason (for each abnormal value)
5. Severity Level (Normal / Mild changes / Needs attention / Urgent review)
6. Final Verdict (one concluding line)
7. Health Tips & Actionable Next Steps (2-3 evidence-based tips)
8. Clinical Consultation Guidance

Rules:
- Use bullet points, short lines
- Simple language for non-medical person
- Do not overstate severity
- Keep concise but informative

Report Type: {report_type}

Extracted Parameters:
{param_text}"""

    try:
        response_text = call_bytez(prompt)
        return response_text.strip() if response_text else (
            f"Unable to generate summary for this {report_type} report. "
            f"Please review the extracted parameters. "
            f"This is AI-generated and should not replace professional medical advice."
        )
    except Exception as e:
        return (
            f"Unable to generate summary for this {report_type} report. "
            f"Please review the extracted parameters. Error: {str(e)}. "
            f"This is AI-generated and should not replace professional medical advice."
        )
