# ============================================================
#  services/report_info_cache.py
#  Static pre-fetched report info — inspired by MedlinePlus
#  and Apollo Hospitals content.
#  No live scraping to keep startup fast and reliable.
# ============================================================

from typing import List, Dict

REPORT_INFO: List[Dict] = [
    {
        "key": "hydration",
        "label": "Water / Hydration",
        "icon": "💧",
        "short_desc": "Measures body fluid balance and hydration status.",
        "what_it_measures": (
            "Body water percentage, serum osmolality, urine specific gravity, "
            "and electrolyte levels (sodium, potassium). Assesses how well the "
            "body is maintaining fluid homeostasis."
        ),
        "why_important": (
            "Proper hydration is critical for kidney function, temperature regulation, "
            "nutrient transport, and cognitive performance. Dehydration even at 2% body "
            "weight loss can impair physical and mental performance."
        ),
        "normal_ranges": [
            {"parameter": "Serum Osmolality",     "range": "285–295 mOsm/kg"},
            {"parameter": "Urine Specific Gravity","range": "1.005–1.030"},
            {"parameter": "Serum Sodium",          "range": "135–145 mEq/L"},
            {"parameter": "Serum Potassium",       "range": "3.5–5.0 mEq/L"},
        ],
        "conditions_detected": ["Dehydration", "Hyponatremia", "Hypernatremia", "SIADH"],
    },
    {
        "key": "vitamins",
        "label": "Vitamins & Minerals",
        "icon": "🧪",
        "short_desc": "Checks levels of essential vitamins and trace minerals.",
        "what_it_measures": (
            "Vitamin D, B12, folate, iron panel (ferritin, serum iron, TIBC), "
            "calcium, magnesium, zinc, and other micronutrients. "
        ),
        "why_important": (
            "Vitamin and mineral deficiencies are among the most common and under-diagnosed "
            "health issues. Vitamin D deficiency affects bone density and immunity; "
            "B12 deficiency causes neurological damage; iron deficiency causes anaemia."
        ),
        "normal_ranges": [
            {"parameter": "Vitamin D (25-OH)",    "range": "30–100 ng/mL"},
            {"parameter": "Vitamin B12",           "range": "200–900 pg/mL"},
            {"parameter": "Ferritin (M/F)",        "range": "12–300 / 12–150 ng/mL"},
            {"parameter": "Calcium (serum)",       "range": "8.5–10.5 mg/dL"},
            {"parameter": "Magnesium",             "range": "1.7–2.2 mg/dL"},
        ],
        "conditions_detected": ["Anaemia", "Osteoporosis", "Rickets", "Pernicious Anaemia", "Iron Deficiency"],
    },
    {
        "key": "glucose",
        "label": "Glucose / Blood Sugar",
        "icon": "🩸",
        "short_desc": "Monitors blood sugar levels and diabetes markers.",
        "what_it_measures": (
            "Fasting plasma glucose (FPG), postprandial glucose (PPBS), "
            "HbA1c (glycated hemoglobin). Provides both immediate and 3-month "
            "average blood sugar picture."
        ),
        "why_important": (
            "Diabetes affects over 77 million Indians and is a leading cause of "
            "kidney disease, blindness, and cardiovascular complications. "
            "Early detection through HbA1c can prevent or delay complications."
        ),
        "normal_ranges": [
            {"parameter": "Fasting Glucose",     "range": "70–100 mg/dL"},
            {"parameter": "Postprandial (2h)",   "range": "< 140 mg/dL"},
            {"parameter": "HbA1c",               "range": "< 5.7%"},
            {"parameter": "HbA1c (Prediabetes)", "range": "5.7–6.4%"},
            {"parameter": "HbA1c (Diabetes)",    "range": "≥ 6.5%"},
        ],
        "conditions_detected": ["Type 2 Diabetes", "Type 1 Diabetes", "Prediabetes", "Hypoglycaemia", "Gestational Diabetes"],
    },
    {
        "key": "blood_pressure",
        "label": "Blood Pressure",
        "icon": "❤️",
        "short_desc": "Measures the force of blood against artery walls.",
        "what_it_measures": (
            "Systolic pressure (pressure when heart beats) and diastolic pressure "
            "(pressure when heart rests between beats), measured in mmHg. "
            "Also includes pulse rate."
        ),
        "why_important": (
            "Hypertension is called the 'silent killer' as it usually has no symptoms "
            "but doubles the risk of heart disease and stroke. "
            "Regular monitoring is essential for cardiovascular health."
        ),
        "normal_ranges": [
            {"parameter": "Normal BP",          "range": "< 120/80 mmHg"},
            {"parameter": "Elevated",           "range": "120–129 / < 80 mmHg"},
            {"parameter": "Hypertension Stage 1","range": "130–139 / 80–89 mmHg"},
            {"parameter": "Hypertension Stage 2","range": "≥ 140 / ≥ 90 mmHg"},
            {"parameter": "Pulse Rate",          "range": "60–100 bpm"},
        ],
        "conditions_detected": ["Hypertension", "Hypotension", "Hypertensive Crisis", "White Coat Hypertension"],
    },
    {
        "key": "cbc",
        "label": "CBC (Complete Blood Count)",
        "icon": "🫀",
        "short_desc": "Comprehensive snapshot of blood cell health.",
        "what_it_measures": (
            "Red blood cells (RBC, Hemoglobin, Hematocrit, MCV, MCH, MCHC, RDW), "
            "White blood cells (WBC/TLC with differential: Neutrophils, Lymphocytes, "
            "Monocytes, Eosinophils, Basophils), and Platelets."
        ),
        "why_important": (
            "CBC is the most frequently ordered blood test. It screens for anaemia, "
            "infections, immune disorders, and blood cancers. Platelets indicate clotting ability."
        ),
        "normal_ranges": [
            {"parameter": "Hemoglobin (M/F)",  "range": "13.5–17.5 / 12.0–15.5 g/dL"},
            {"parameter": "WBC/TLC",           "range": "4,000–11,000 /µL"},
            {"parameter": "Platelets",         "range": "1.5–4.0 Lac /µL"},
            {"parameter": "MCV",               "range": "80–100 fL"},
            {"parameter": "Neutrophils",       "range": "40–75%"},
        ],
        "conditions_detected": ["Anaemia", "Leukaemia", "Infection", "Thrombocytopenia", "Polycythaemia"],
    },
    {
        "key": "lipid_profile",
        "label": "Lipid Profile",
        "icon": "🧬",
        "short_desc": "Evaluates cholesterol and triglyceride levels.",
        "what_it_measures": (
            "Total Cholesterol, LDL (bad cholesterol), HDL (good cholesterol), "
            "VLDL, Triglycerides, and non-HDL cholesterol. "
            "Requires 9–12 hour fasting for accuracy."
        ),
        "why_important": (
            "High LDL and triglycerides combined with low HDL are the primary risk "
            "factors for atherosclerosis, coronary artery disease, and stroke. "
            "Regular monitoring helps guide diet and medication decisions."
        ),
        "normal_ranges": [
            {"parameter": "Total Cholesterol", "range": "< 200 mg/dL"},
            {"parameter": "LDL Cholesterol",   "range": "< 100 mg/dL (optimal)"},
            {"parameter": "HDL Cholesterol",   "range": "> 40 (M) / > 50 (F) mg/dL"},
            {"parameter": "Triglycerides",     "range": "< 150 mg/dL"},
            {"parameter": "VLDL",              "range": "2–30 mg/dL"},
        ],
        "conditions_detected": ["Hypercholesterolaemia", "Hypertriglyceridaemia", "Coronary Artery Disease Risk", "Familial Hypercholesterolaemia"],
    },
    {
        "key": "thyroid",
        "label": "Thyroid Profile (TSH/T3/T4)",
        "icon": "🦠",
        "short_desc": "Evaluates thyroid gland function and hormone levels.",
        "what_it_measures": (
            "TSH (Thyroid Stimulating Hormone) — the primary screening test. "
            "Free T3 (fT3) and Free T4 (fT4) for active thyroid hormones. "
            "Sometimes includes anti-TPO antibodies for autoimmune thyroid disease."
        ),
        "why_important": (
            "The thyroid regulates metabolism, heart rate, body temperature, and mood. "
            "Hypothyroidism causes fatigue and weight gain; hyperthyroidism causes "
            "anxiety and heart palpitations. Both are highly treatable when caught early."
        ),
        "normal_ranges": [
            {"parameter": "TSH",     "range": "0.4–4.0 mIU/L"},
            {"parameter": "Free T3", "range": "2.3–4.2 pg/mL"},
            {"parameter": "Free T4", "range": "0.8–1.8 ng/dL"},
            {"parameter": "T3 (Total)","range": "80–200 ng/dL"},
            {"parameter": "T4 (Total)","range": "5.0–12.0 µg/dL"},
        ],
        "conditions_detected": ["Hypothyroidism", "Hyperthyroidism", "Hashimoto's Thyroiditis", "Graves' Disease", "Thyroid Nodules"],
    },
    {
        "key": "liver_function",
        "label": "Liver Function Test (LFT)",
        "icon": "🧫",
        "short_desc": "Assesses liver health and detoxification capacity.",
        "what_it_measures": (
            "Liver enzymes (ALT/SGPT, AST/SGOT, ALP, GGT), "
            "bilirubin (total, direct, indirect), total protein, albumin, "
            "and globulin. Provides a comprehensive picture of liver inflammation and function."
        ),
        "why_important": (
            "The liver performs over 500 functions including detoxification, protein synthesis, "
            "and bile production. LFT can detect hepatitis, fatty liver, cirrhosis, "
            "and drug-induced liver injury before symptoms appear."
        ),
        "normal_ranges": [
            {"parameter": "ALT/SGPT",         "range": "7–56 U/L"},
            {"parameter": "AST/SGOT",         "range": "10–40 U/L"},
            {"parameter": "ALP",              "range": "44–147 U/L"},
            {"parameter": "Total Bilirubin",  "range": "0.1–1.2 mg/dL"},
            {"parameter": "Serum Albumin",    "range": "3.4–5.4 g/dL"},
        ],
        "conditions_detected": ["Hepatitis", "Fatty Liver (NAFLD)", "Cirrhosis", "Cholestasis", "Drug-induced Liver Injury"],
    },
    {
        "key": "kidney_function",
        "label": "Kidney Function Test (KFT/RFT)",
        "icon": "🫁",
        "short_desc": "Evaluates kidney filtration and waste removal.",
        "what_it_measures": (
            "Serum creatinine, blood urea nitrogen (BUN), uric acid, "
            "eGFR (estimated glomerular filtration rate), and electrolytes "
            "(sodium, potassium, chloride, bicarbonate). "
            "Sometimes includes urine microalbumin."
        ),
        "why_important": (
            "Kidney disease is often asymptomatic until 60–70% of function is lost. "
            "Early detection through creatinine and eGFR allows interventions to slow "
            "progression. Kidneys filter ~200 litres of blood daily."
        ),
        "normal_ranges": [
            {"parameter": "Serum Creatinine (M/F)", "range": "0.7–1.2 / 0.6–1.1 mg/dL"},
            {"parameter": "BUN",                    "range": "7–20 mg/dL"},
            {"parameter": "eGFR",                   "range": "> 60 mL/min/1.73m²"},
            {"parameter": "Uric Acid (M/F)",        "range": "3.4–7.0 / 2.4–6.0 mg/dL"},
            {"parameter": "Serum Sodium",           "range": "135–145 mEq/L"},
        ],
        "conditions_detected": ["Chronic Kidney Disease", "Acute Kidney Injury", "Gout", "Diabetic Nephropathy", "Hypertensive Nephropathy"],
    },
]


def get_all_report_info() -> List[Dict]:
    """Return all report info cards."""
    return REPORT_INFO


def get_report_info_by_key(key: str) -> Dict | None:
    """Return a single report info card by key."""
    for item in REPORT_INFO:
        if item["key"] == key:
            return item
    return None
