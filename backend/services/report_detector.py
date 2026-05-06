# ============================================================
#  services/report_detector.py  (v2)
#  - Strict per-type parameter WHITELIST (no junk extraction)
#  - Trusted clinical reference ranges from ICMR/WHO/AHA
#  - Plausibility checks to skip lab IDs, addresses, dates
# ============================================================

import re
import logging
from typing import Tuple, List, Dict

logger = logging.getLogger("data_insights.report_detector")

# ── Type detection keywords ───────────────────────────────────
REPORT_KEYWORDS: Dict[str, Dict] = {
    "lipid_profile": {
        "label": "Lipid Profile",
        "icon": "🧬",
        "keywords": ["ldl", "hdl", "triglyceride", "total cholesterol", "cholesterol total",
                     "vldl", "non-hdl", "lipoprotein"],
        "weight": 3,
    },
    "cbc": {
        "label": "CBC (Complete Blood Count)",
        "icon": "🫀",
        "keywords": ["haemoglobin", "hemoglobin", "hematocrit", "packed cell volume",
                     "wbc", "rbc", "platelet", "neutrophil", "lymphocyte", "monocyte",
                     "eosinophil", "basophil", "mcv", "mch", "mchc", "rdw", "tlc", "dlc"],
        "weight": 3,
    },
    "glucose": {
        "label": "Glucose / Blood Sugar",
        "icon": "🩸",
        "keywords": ["fasting glucose", "fasting blood sugar", "hba1c", "glycated hemoglobin",
                     "ppbs", "blood sugar", "glucose tolerance", "random blood glucose",
                     "postprandial", "glycated haemoglobin"],
        "weight": 3,
    },
    "thyroid": {
        "label": "Thyroid Profile (TSH/T3/T4)",
        "icon": "🦠",
        "keywords": ["tsh", "free t3", "free t4", "ft3", "ft4",
                     "triiodothyronine", "thyroxine", "thyroid stimulating"],
        "weight": 3,
    },
    "liver_function": {
        "label": "Liver Function Test (LFT)",
        "icon": "🧫",
        "keywords": ["sgpt", "sgot", "alt", "ast", "alkaline phosphatase", "alp",
                     "bilirubin", "total protein", "albumin", "globulin", "ggt",
                     "liver function", "lft"],
        "weight": 3,
    },
    "kidney_function": {
        "label": "Kidney Function Test (KFT/RFT)",
        "icon": "🫁",
        "keywords": ["creatinine", "blood urea", "bun", "uric acid", "gfr", "egfr",
                     "kidney function", "renal function", "kft", "rft"],
        "weight": 3,
    },
    "vitamins": {
        "label": "Vitamins & Minerals",
        "icon": "🧪",
        "keywords": ["vitamin d", "vitamin b12", "vitamin c", "vitamin a",
                     "folate", "folic acid", "ferritin", "transferrin",
                     "25-oh vitamin", "cobalamin"],
        "weight": 3,
    },
    "blood_pressure": {
        "label": "Blood Pressure",
        "icon": "❤️",
        "keywords": ["systolic", "diastolic", "blood pressure", "mmhg",
                     "hypertension", "bp reading", "pulse rate"],
        "weight": 3,
    },
    "hydration": {
        "label": "Water / Hydration",
        "icon": "💧",
        "keywords": ["osmolality", "urine specific gravity", "body water",
                     "dehydration", "electrolyte balance"],
        "weight": 2,
    },
}


# ── Per-type WHITELIST of important parameters ────────────────
# Each entry: (display_name_substring, lo, hi, unit, display_unit)
# lo/hi = trusted normal range (ICMR/WHO/AHA guidelines)
# Only parameters whose name matches a whitelist entry are shown.
PARAM_WHITELIST: Dict[str, List[Tuple]] = {
    "lipid_profile": [
        ("cholesterol total",    0,    200,  "mg/dL", "mg/dL"),
        ("cholesterol",          0,    200,  "mg/dL", "mg/dL"),   # catch-all
        ("triglyceride",         0,    150,  "mg/dL", "mg/dL"),
        ("hdl",                  40,   60,   "mg/dL", "mg/dL"),
        ("ldl",                  0,    100,  "mg/dL", "mg/dL"),
        ("vldl",                 0,    30,   "mg/dL", "mg/dL"),
        ("non-hdl",              0,    130,  "mg/dL", "mg/dL"),
        ("non hdl",              0,    130,  "mg/dL", "mg/dL"),
    ],
    "cbc": [
        ("hemoglobin",           12,   17.5, "g/dL", "g/dL"),
        ("haemoglobin",          12,   17.5, "g/dL", "g/dL"),
        ("packed cell volume",   36,   52,   "%",     "%"),
        ("hematocrit",           36,   52,   "%",     "%"),
        ("rbc",                  4.2,  5.9,  "10⁶/µL","10⁶/µL"),
        ("wbc",                  4,    11,   "10³/µL","10³/µL"),
        ("tlc",                  4,    11,   "10³/µL","10³/µL"),
        ("platelet",             150,  400,  "10³/µL","×10³/µL"),
        ("neutrophil",           40,   75,   "%",     "%"),
        ("lymphocyte",           20,   45,   "%",     "%"),
        ("monocyte",             2,    10,   "%",     "%"),
        ("eosinophil",           1,    6,    "%",     "%"),
        ("mcv",                  80,   100,  "fL",   "fL"),
        ("mch",                  27,   33,   "pg",   "pg"),
        ("mchc",                 32,   36,   "g/dL", "g/dL"),
        ("rdw",                  11.5, 14.5, "%",    "%"),
    ],
    "glucose": [
        ("fasting",              70,   100,  "mg/dL", "mg/dL"),
        ("hba1c",                0,    5.7,  "%",     "%"),
        ("glycated",             0,    5.7,  "%",     "%"),
        ("postprandial",         0,    140,  "mg/dL", "mg/dL"),
        ("ppbs",                 0,    140,  "mg/dL", "mg/dL"),
        ("random",               70,   140,  "mg/dL", "mg/dL"),
    ],
    "thyroid": [
        ("tsh",                  0.4,  4.0,  "mIU/L", "mIU/L"),
        ("free t3",              2.3,  4.2,  "pg/mL", "pg/mL"),
        ("ft3",                  2.3,  4.2,  "pg/mL", "pg/mL"),
        ("free t4",              0.8,  1.8,  "ng/dL", "ng/dL"),
        ("ft4",                  0.8,  1.8,  "ng/dL", "ng/dL"),
        ("t3",                   80,   200,  "ng/dL", "ng/dL"),
        ("t4",                   5,    12,   "µg/dL", "µg/dL"),
    ],
    "liver_function": [
        ("sgpt",                 7,    40,   "U/L",   "U/L"),
        ("alt",                  7,    40,   "U/L",   "U/L"),
        ("sgot",                 10,   40,   "U/L",   "U/L"),
        ("ast",                  10,   40,   "U/L",   "U/L"),
        ("alp",                  44,   147,  "U/L",   "U/L"),
        ("alkaline phosphatase", 44,   147,  "U/L",   "U/L"),
        ("ggt",                  8,    61,   "U/L",   "U/L"),
        ("bilirubin total",      0.1,  1.2,  "mg/dL", "mg/dL"),
        ("bilirubin",            0.1,  1.2,  "mg/dL", "mg/dL"),
        ("albumin",              3.5,  5.0,  "g/dL",  "g/dL"),
        ("total protein",        6.3,  8.2,  "g/dL",  "g/dL"),
        ("globulin",             2.0,  3.5,  "g/dL",  "g/dL"),
    ],
    "kidney_function": [
        ("creatinine",           0.6,  1.2,  "mg/dL", "mg/dL"),
        ("blood urea",           15,   45,   "mg/dL", "mg/dL"),
        ("urea",                 15,   45,   "mg/dL", "mg/dL"),
        ("bun",                  7,    20,   "mg/dL", "mg/dL"),
        ("uric acid",            2.4,  7.0,  "mg/dL", "mg/dL"),
        ("egfr",                 60,   120,  "mL/min/1.73m²", "mL/min"),
        ("gfr",                  60,   120,  "mL/min/1.73m²", "mL/min"),
    ],
    "vitamins": [
        ("vitamin d",            30,   100,  "ng/mL", "ng/mL"),
        ("vitamin b12",          200,  900,  "pg/mL", "pg/mL"),
        ("b12",                  200,  900,  "pg/mL", "pg/mL"),
        ("folate",               4,    20,   "ng/mL", "ng/mL"),
        ("ferritin",             12,   300,  "ng/mL", "ng/mL"),
        ("serum iron",           60,   170,  "µg/dL", "µg/dL"),
        ("calcium",              8.5,  10.5, "mg/dL", "mg/dL"),
        ("magnesium",            1.7,  2.2,  "mg/dL", "mg/dL"),
        ("zinc",                 70,   120,  "µg/dL", "µg/dL"),
    ],
    "blood_pressure": [
        ("systolic",             90,   120,  "mmHg", "mmHg"),
        ("diastolic",            60,   80,   "mmHg", "mmHg"),
        ("pulse",                60,   100,  "bpm",  "bpm"),
    ],
}

# ── Plausibility gate: (lo, hi) for numeric value ─────────────
# Values outside these physiological bounds are junk (lab IDs, dates, etc.)
PLAUSIBILITY: Dict[str, Tuple[float, float]] = {
    "lipid_profile":   (0,    1000),
    "cbc":             (0,    800),
    "glucose":         (0,    999),
    "thyroid":         (0,    200),
    "liver_function":  (0,    2000),
    "kidney_function": (0,    500),
    "vitamins":        (0,    5000),
    "blood_pressure":  (40,   300),
    "default":         (0,    9999),
}

BORDERLINE_FACTOR = 0.12   # 12% outside normal = borderline


def _classify_status(val: float, lo: float, hi: float) -> str:
    if lo <= val <= hi:
        return "normal"
    margin_lo = lo * BORDERLINE_FACTOR
    margin_hi = hi * BORDERLINE_FACTOR
    if (lo - margin_lo) <= val < lo:
        return "low"
    if hi < val <= (hi + margin_hi):
        return "borderline"
    if val < lo:
        return "low"
    return "high"


def detect_report_type(text: str) -> Tuple[str, str, str, str]:
    """Returns (report_key, label, icon, confidence)."""
    text_lower = text.lower()
    scores: Dict[str, int] = {}
    for key, meta in REPORT_KEYWORDS.items():
        count = sum(1 for kw in meta["keywords"] if kw in text_lower)
        if count > 0:
            scores[key] = count * meta["weight"]

    if not scores:
        return "unknown", "Unknown Report", "📄", "low"

    best_key  = max(scores, key=lambda k: scores[k])
    best_score = scores[best_key]
    meta = REPORT_KEYWORDS[best_key]

    confidence = "high" if best_score >= 6 else ("medium" if best_score >= 3 else "low")
    return best_key, meta["label"], meta["icon"], confidence


# ── Main extraction function ──────────────────────────────────
def extract_parameters(text: str, report_type: str) -> List[Dict]:
    """
    Extract ONLY whitelisted, clinically meaningful parameters.
    Uses strict keyword matching + plausibility checks.
    Returns list of {name, value, unit, status, normal_range}.
    """
    whitelist = PARAM_WHITELIST.get(report_type, [])
    if not whitelist:
        return []

    plaus_lo, plaus_hi = PLAUSIBILITY.get(report_type, PLAUSIBILITY["default"])

    # Flatten text: merge continuation lines for better regex matching
    # Replace multiple spaces with single tab-stop marker for table detection
    lines = [l.strip() for l in text.replace("\r", "\n").split("\n") if l.strip()]
    found: Dict[str, Dict] = {}   # key → param dict (dedup by whitelist entry key)

    def _add(wl_key: str, display_name: str, val_str: str, unit_override: str,
             lo: float, hi: float, display_unit: str):
        if wl_key in found:
            return
        try:
            val = float(val_str.replace(",", ""))
        except ValueError:
            return
        if not (plaus_lo <= val <= plaus_hi):
            return            # plausibility gate
        if val == 0:
            return            # zeros are almost always parsing artifacts
        status = _classify_status(val, lo, hi)
        unit = unit_override or display_unit
        found[wl_key] = {
            "name":         display_name,
            "value":        str(val),
            "unit":         unit,
            "status":       status,
            "normal_range": f"{lo}–{hi} {display_unit}".strip(),
        }

    # Pattern A: "Name  value  unit  ref" (multi-space table format)
    PATTERN_A = re.compile(
        r"^(.{3,80}?)\s{2,}(\d+\.?\d*)\s*([a-zA-Z/%µ][^\s]{0,14})?\s*",
        re.MULTILINE,
    )
    for m in PATTERN_A.finditer(text):
        raw_name = m.group(1).strip().rstrip(":").strip()
        val_str  = m.group(2)
        unit     = (m.group(3) or "").strip()
        name_lower = raw_name.lower()
        for (kw, lo, hi, du, dunit) in whitelist:
            if kw in name_lower:
                wl_key = kw
                _add(wl_key, raw_name, val_str, unit, lo, hi, dunit)
                break

    # Pattern B: "Name value" at end of line (no unit on same line)
    PATTERN_B = re.compile(r"^(.{3,80}?)\s+(\d+\.?\d*)$", re.MULTILINE)
    for m in PATTERN_B.finditer(text):
        raw_name  = m.group(1).strip()
        val_str   = m.group(2)
        name_lower = raw_name.lower()
        for (kw, lo, hi, du, dunit) in whitelist:
            if kw in name_lower:
                wl_key = kw
                _add(wl_key, raw_name, val_str, "", lo, hi, dunit)
                break

    # Pattern C: "Name\nValue\nUnit" vertical format
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for (kw, lo, hi, du, dunit) in whitelist:
            if kw in line_lower and len(line) < 80:
                # Hunt for the value in next few lines
                for j in range(i + 1, min(i + 6, len(lines))):
                    vm = re.match(r"^(\d+\.?\d*)$", lines[j])
                    if vm:
                        unit = ""
                        if j + 1 < len(lines):
                            u = lines[j + 1]
                            if len(u) < 20 and re.search(r"[a-zA-Z/%µ]", u) and not re.match(r"^\d", u):
                                unit = u
                        wl_key = kw
                        _add(wl_key, line, vm.group(1), unit, lo, hi, dunit)
                        break

    # Preserve ordering as in whitelist
    result = []
    for (kw, *_) in whitelist:
        if kw in found:
            result.append(found[kw])

    logger.info(f"extract_parameters({report_type}): {len(result)} params from {len(found)} found")
    return result
