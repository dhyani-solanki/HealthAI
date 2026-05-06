# ============================================================
#  routers/mediinsight_config.py
#  All constants, normal ranges, trusted sources, allowed types.
#  Import this in every other mediinsight module.
# ============================================================

from typing import Dict, List

# ── Allowed & Rejected ────────────────────────────────────────
ALLOWED_TYPES = [
    "CBC (Complete Blood Count)",
    "Liver Function Test (LFT)",
    "Renal Function Test (RFT)",
    "Lipid Profile",
    "Thyroid Function Test",
    "Blood Glucose / HbA1c",
    "Electrolyte Panel",
    "ESR / CRP",
    "Iron Studies",
]

REJECTED_KW = [
    "x-ray", "ct scan", "mri", "ultrasound", "ecg", "echo",
    "pathology slide", "imaging", "radiology", "sonography",
]

# ── Trusted sources per report type ──────────────────────────
TRUSTED_SOURCES: Dict[str, List[str]] = {
    "CBC (Complete Blood Count)": [
        "https://medlineplus.gov/lab-tests/complete-blood-count-cbc/",
        "https://www.healthline.com/health/cbc",
        "https://my.clevelandclinic.org/health/diagnostics/4053-complete-blood-count",
    ],
    "Liver Function Test (LFT)": [
        "https://medlineplus.gov/lab-tests/liver-function-tests/",
        "https://www.healthline.com/health/liver-function-tests",
        "https://my.clevelandclinic.org/health/diagnostics/17662-liver-function-tests",
    ],
    "Renal Function Test (RFT)": [
        "https://medlineplus.gov/lab-tests/basic-metabolic-panel/",
        "https://www.healthline.com/health/kidney-function-tests",
        "https://my.clevelandclinic.org/health/diagnostics/21659-kidney-function-tests",
    ],
    "Lipid Profile": [
        "https://medlineplus.gov/lab-tests/lipid-panel/",
        "https://www.healthline.com/health/cholesterol/lipid-panel",
        "https://my.clevelandclinic.org/health/diagnostics/17176-lipid-panel",
    ],
    "Thyroid Function Test": [
        "https://medlineplus.gov/lab-tests/tsh-thyroid-stimulating-hormone-test/",
        "https://www.healthline.com/health/thyroid-function-tests",
        "https://my.clevelandclinic.org/health/diagnostics/17658-thyroid-function-tests",
    ],
    "Blood Glucose / HbA1c": [
        "https://medlineplus.gov/lab-tests/hemoglobin-a1c-hba1c-test/",
        "https://www.cdc.gov/diabetes/diabetes-testing/a1c-test.html",
        "https://www.healthline.com/health/type-2-diabetes/ac1-test",
    ],
    "Electrolyte Panel": [
        "https://medlineplus.gov/lab-tests/electrolyte-panel/",
        "https://www.healthline.com/health/electrolytes",
        "https://my.clevelandclinic.org/health/diagnostics/electrolyte-tests",
    ],
    "ESR / CRP": [
        "https://medlineplus.gov/lab-tests/erythrocyte-sedimentation-rate-esr/",
        "https://medlineplus.gov/lab-tests/c-reactive-protein-crp-test/",
        "https://www.healthline.com/health/c-reactive-protein",
    ],
    "Iron Studies": [
        "https://medlineplus.gov/lab-tests/serum-iron-test/",
        "https://www.healthline.com/health/serum-iron",
        "https://my.clevelandclinic.org/health/diagnostics/iron-tests",
    ],
}

# ── Standard normal ranges ────────────────────────────────────
# Keys are lowercase parameter names.
# Dict values: {"male":..., "female":..., "general":...}
STANDARD_RANGES: Dict[str, Dict[str, str]] = {
    # CBC
    "hemoglobin":                  {"male": "13.5-17.5 g/dL",  "female": "12.0-15.5 g/dL", "general": "12.0-17.5 g/dL"},
    "packed cell volume":          {"male": "40-50%",           "female": "36-46%",          "general": "36-50%"},
    "hematocrit":                  {"male": "40-50%",           "female": "36-46%",          "general": "36-50%"},
    "pcv":                         {"male": "40-50%",           "female": "36-46%",          "general": "36-50%"},
    "rbc":                         {"male": "4.5-5.9 M/uL",    "female": "4.0-5.2 M/uL",   "general": "4.0-5.9 M/uL"},
    "rbc count":                   {"male": "4.5-5.9 M/uL",    "female": "4.0-5.2 M/uL",   "general": "4.0-5.9 M/uL"},
    "wbc":                         {"general": "4.0-11.0 thou/mm3"},
    "tlc":                         {"general": "4.0-11.0 thou/mm3"},
    "total leukocyte count":       {"general": "4.0-11.0 thou/mm3"},
    "platelet count":              {"general": "150-410 thou/mm3"},
    "platelets":                   {"general": "150-410 thou/mm3"},
    "mcv":                         {"general": "83-101 fL"},
    "mch":                         {"general": "27-32 pg"},
    "mchc":                        {"general": "31.5-34.5 g/dL"},
    "rdw":                         {"general": "11.6-14.0%"},
    "neutrophils":                 {"general": "40-80%"},
    "segmented neutrophils":       {"general": "40-80%"},
    "lymphocytes":                 {"general": "20-40%"},
    "monocytes":                   {"general": "2-10%"},
    "eosinophils":                 {"general": "1-6%"},
    "basophils":                   {"general": "0-2%"},
    "mean platelet volume":        {"general": "6.5-12.0 fL"},
    "mpv":                         {"general": "6.5-12.0 fL"},
    # LFT
    "alt":                         {"general": "7-56 U/L"},
    "sgpt":                        {"general": "7-56 U/L"},
    "ast":                         {"general": "10-40 U/L"},
    "sgot":                        {"general": "10-40 U/L"},
    "alp":                         {"general": "44-147 U/L"},
    "bilirubin total":             {"general": "0.2-1.2 mg/dL"},
    "bilirubin direct":            {"general": "0.0-0.3 mg/dL"},
    "bilirubin indirect":          {"general": "0.1-1.0 mg/dL"},
    "albumin":                     {"general": "3.4-5.4 g/dL"},
    "total protein":               {"general": "6.0-8.3 g/dL"},
    # RFT
    "creatinine":                  {"male": "0.74-1.35 mg/dL", "female": "0.59-1.04 mg/dL","general": "0.59-1.35 mg/dL"},
    "urea":                        {"general": "7-20 mg/dL"},
    "bun":                         {"general": "7-20 mg/dL"},
    "uric acid":                   {"male": "3.4-7.0 mg/dL",   "female": "2.4-6.0 mg/dL",  "general": "2.4-7.0 mg/dL"},
    # Lipid — all name variants to match Dr Lal format
    "total cholesterol":           {"general": "<200 mg/dL"},
    "cholesterol total":           {"general": "<200 mg/dL"},
    "cholesterol":                 {"general": "<200 mg/dL"},
    "ldl":                         {"general": "<100 mg/dL"},
    "ldl cholesterol":             {"general": "<100 mg/dL"},
    "ldl cholesterol,direct":      {"general": "<100 mg/dL"},
    "ldl cholesterol direct":      {"general": "<100 mg/dL"},
    "hdl":                         {"male": ">40 mg/dL", "female": ">50 mg/dL", "general": ">40 mg/dL"},
    "hdl cholesterol":             {"male": ">40 mg/dL", "female": ">50 mg/dL", "general": ">40 mg/dL"},
    "triglycerides":               {"general": "<150 mg/dL"},
    "triglyceride":                {"general": "<150 mg/dL"},
    "vldl":                        {"general": "<30 mg/dL"},
    "vldl cholesterol":            {"general": "<30 mg/dL"},
    "non-hdl cholesterol":         {"general": "<130 mg/dL"},
    "non-hdl":                     {"general": "<130 mg/dL"},
    "non hdl cholesterol":         {"general": "<130 mg/dL"},
    # Thyroid
    "tsh":                         {"general": "0.4-4.0 mIU/L"},
    "t3":                          {"general": "80-200 ng/dL"},
    "t4":                          {"general": "5.0-12.0 ug/dL"},
    "free t3":                     {"general": "2.3-4.2 pg/mL"},
    "free t4":                     {"general": "0.8-1.8 ng/dL"},
    # Glucose
    "fasting glucose":             {"general": "70-100 mg/dL"},
    "glucose":                     {"general": "70-100 mg/dL"},
    "hba1c":                       {"general": "<5.7%"},
    "random glucose":              {"general": "<140 mg/dL"},
    # Electrolytes
    "sodium":                      {"general": "136-145 mEq/L"},
    "potassium":                   {"general": "3.5-5.0 mEq/L"},
    "chloride":                    {"general": "98-107 mEq/L"},
    "calcium":                     {"general": "8.5-10.5 mg/dL"},
    "magnesium":                   {"general": "1.7-2.2 mg/dL"},
    # ESR/CRP
    "esr":                         {"male": "<15 mm/hr",        "female": "<20 mm/hr",       "general": "<20 mm/hr"},
    "crp":                         {"general": "<1.0 mg/dL"},
    # Iron
    "serum iron":                  {"male": "65-175 ug/dL",     "female": "50-170 ug/dL",    "general": "50-175 ug/dL"},
    "ferritin":                    {"male": "12-300 ng/mL",     "female": "12-150 ng/mL",    "general": "12-300 ng/mL"},
    "tibc":                        {"general": "250-370 ug/dL"},
}

# ── Key parameters to extract per report type ──────────────────
# Only these are shown — irrelevant/derived values are filtered out
KEY_PARAMS: Dict[str, List[str]] = {
    "CBC (Complete Blood Count)": [
        "Hemoglobin", "Packed Cell Volume", "PCV",
        "RBC Count", "MCV", "MCH", "MCHC", "RDW",
        "Total Leukocyte Count", "TLC",
        "Segmented Neutrophils", "Neutrophils",
        "Lymphocytes", "Monocytes", "Eosinophils", "Basophils",
        "Platelet Count", "Mean Platelet Volume",
    ],
    "Liver Function Test (LFT)": [
        "ALT", "SGPT", "AST", "SGOT", "ALP",
        "Bilirubin Total", "Bilirubin Direct", "Bilirubin Indirect",
        "Albumin", "Total Protein",
    ],
    "Renal Function Test (RFT)": [
        "Creatinine", "Urea", "BUN", "Uric Acid",
        "Sodium", "Potassium", "Chloride", "Calcium",
    ],
    "Lipid Profile": [
        "Cholesterol Total", "Total Cholesterol", "Cholesterol",
        "Triglycerides", "Triglyceride",
        "HDL Cholesterol", "HDL",
        "LDL Cholesterol", "LDL",
        "VLDL Cholesterol", "VLDL",
        "Non-HDL Cholesterol", "Non-HDL",
    ],
    "Thyroid Function Test": [
        "TSH", "T3", "T4", "Free T3", "Free T4",
    ],
    "Blood Glucose / HbA1c": [
        "Fasting Glucose", "Glucose", "HbA1c", "Random Glucose",
    ],
    "Electrolyte Panel": [
        "Sodium", "Potassium", "Chloride", "Calcium", "Magnesium",
    ],
    "ESR / CRP": ["ESR", "CRP"],
    "Iron Studies": ["Serum Iron", "Ferritin", "TIBC"],
}