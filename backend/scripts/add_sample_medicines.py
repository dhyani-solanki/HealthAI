#!/usr/bin/env python3
"""
Script to add sample medicines to the MediScan RAG database.
Run this to populate the database with some test data.

Usage:
    python scripts/add_sample_medicines.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.mediscan_rag_service import get_mediscan_rag


# Sample medicines data
SAMPLE_MEDICINES = [
    {
        "medicine_name": "TOPCID-40 (Famotidine I.P. 40 mg Tablets)",
        "use": "Famotidine is a histamine H2-receptor antagonist that works by decreasing the amount of acid the stomach produces. It is commonly used to treat and prevent ulcers in the stomach and intestines. It also treats conditions where the stomach produces too much acid, such as Zollinger-Ellison syndrome, and gastroesophageal reflux disease (GERD). It can also be used for short-term relief of heartburn, acid indigestion, and sour stomach.",
        "dosage": "As directed by the Physician. (Contains Famotidine I.P. 40 mg)",
        "precautions": "SCHEDULE H PRESCRIPTION DRUG - CAUTION: It is dangerous to take this preparation except under medical supervision.\n\nDo not be sold by retail without the prescription of a Registered Medical Practitioner.\n\nPROTECTED FROM LIGHT AND MOISTURE.\n\nKeep all medicines out of reach of children.",
        "side_effects": "Headache\nDizziness\nConstipation\nDiarrhea\nNausea\nAbdominal pain\nDry mouth\nFatigue"
    },
    {
        "medicine_name": "Paracetamol 500mg",
        "use": "Paracetamol is used to relieve mild to moderate pain from headaches, muscle aches, menstrual periods, colds and sore throats, toothaches, backaches, and reactions to vaccinations. It is also used to reduce fever.",
        "dosage": "Adults: 500mg to 1000mg every 4-6 hours as needed. Maximum 4000mg in 24 hours.",
        "precautions": "Do not exceed recommended dose. Avoid alcohol while taking this medication. Consult doctor if symptoms persist for more than 3 days.",
        "side_effects": "Rare side effects may include:\nAllergic reactions\nSkin rash\nLiver damage (with overdose)"
    },
    {
        "medicine_name": "Loperamide Hydrochloride (LOPAMIDE)",
        "use": "Loperamide is primarily used to treat sudden diarrhea (including traveler's diarrhea). It works by slowing down the movement of the gut, which helps to decrease the number of bowel movements and make the stool less watery.",
        "dosage": "Each uncoated tablet contains Loperamide Hydrochloride I.P. 2 mg.\nDose: As directed by the Physician.",
        "precautions": "STORE AT A TEMPERATURE NOT EXCEEDING 30°C, PROTECTED FROM LIGHT AND MOISTURE.\n\nNot to be administered in children below 12 years.\n\nSCHEDULE H PRESCRIPTION DRUG - CAUTION: Not to be sold by retail without the prescription of a Registered Medical Practitioner.",
        "side_effects": "Constipation\nDizziness\nDrowsiness\nNausea\nAbdominal cramps"
    },
    {
        "medicine_name": "Telsys CM 50 (Metoprolol Succinate Extended Release, Cilnidipine)",
        "use": "This combination medication is used to treat high blood pressure (hypertension). Metoprolol is a beta-blocker that works by slowing the heart rate and reducing the force of heart contractions. Cilnidipine is a calcium channel blocker that relaxes blood vessels.",
        "dosage": "As directed by the Physician. Take with or without food at the same time each day.",
        "precautions": "Do not stop taking this medication suddenly without consulting your doctor. May cause dizziness - avoid driving until you know how it affects you. Avoid alcohol.",
        "side_effects": "Dizziness\nFatigue\nHeadache\nNausea\nSlow heartbeat\nCold hands and feet"
    },
    {
        "medicine_name": "Combiflam Plus",
        "use": "Combiflam Plus is used for the treatment of pain and inflammation. It contains Ibuprofen and Paracetamol which work together to provide relief from various types of pain including headache, toothache, muscle pain, and fever.",
        "dosage": "Adults: 1 tablet every 6-8 hours as needed. Do not exceed 3 tablets in 24 hours.",
        "precautions": "Take with food to reduce stomach upset. Not recommended for patients with stomach ulcers, kidney problems, or heart conditions. Avoid alcohol.",
        "side_effects": "Stomach upset\nNausea\nDizziness\nHeartburn\nAllergic reactions (rare)"
    },
    {
        "medicine_name": "Azithromycin 500mg",
        "use": "Azithromycin is an antibiotic used to treat various bacterial infections including respiratory infections, skin infections, ear infections, and sexually transmitted diseases.",
        "dosage": "Usually 500mg once daily for 3 days, or as directed by physician.",
        "precautions": "Complete the full course of treatment. Take on empty stomach (1 hour before or 2 hours after meals). Inform doctor if you have liver or kidney problems.",
        "side_effects": "Nausea\nDiarrhea\nAbdominal pain\nVomiting\nHeadache"
    },
    {
        "medicine_name": "Omeprazole 20mg",
        "use": "Omeprazole is a proton pump inhibitor (PPI) used to treat gastroesophageal reflux disease (GERD), stomach ulcers, and conditions where the stomach produces too much acid.",
        "dosage": "20mg once daily before breakfast. Swallow whole, do not crush or chew.",
        "precautions": "Long-term use may increase risk of bone fractures. May interact with other medications. Consult doctor if symptoms persist.",
        "side_effects": "Headache\nNausea\nDiarrhea\nStomach pain\nFlatulence"
    },
    {
        "medicine_name": "Cetirizine 10mg",
        "use": "Cetirizine is an antihistamine used to relieve allergy symptoms such as watery eyes, runny nose, itching eyes/nose, sneezing, hives, and itching.",
        "dosage": "Adults and children over 12: 10mg once daily. May be taken with or without food.",
        "precautions": "May cause drowsiness. Avoid alcohol. Use caution when driving or operating machinery.",
        "side_effects": "Drowsiness\nDry mouth\nFatigue\nHeadache\nDizziness"
    },
    {
        "medicine_name": "Metformin 500mg",
        "use": "Metformin is used to treat type 2 diabetes. It helps control blood sugar levels by decreasing glucose production in the liver and improving insulin sensitivity.",
        "dosage": "Usually started at 500mg twice daily with meals. Dose may be increased gradually as directed by physician.",
        "precautions": "Take with meals to reduce stomach upset. Avoid excessive alcohol. Inform doctor before any surgery or imaging tests with contrast dye.",
        "side_effects": "Nausea\nDiarrhea\nStomach upset\nMetallic taste\nVitamin B12 deficiency (long-term use)"
    },
    {
        "medicine_name": "Amlodipine 5mg",
        "use": "Amlodipine is a calcium channel blocker used to treat high blood pressure and chest pain (angina). It works by relaxing blood vessels so blood can flow more easily.",
        "dosage": "Usually 5mg once daily. May be increased to 10mg if needed.",
        "precautions": "May cause swelling in ankles/feet. Avoid grapefruit juice. Do not stop suddenly without consulting doctor.",
        "side_effects": "Swelling of ankles/feet\nDizziness\nFlushing\nHeadache\nFatigue"
    }
]


def main():
    print("🔄 Initializing MediScan RAG service...")
    rag = get_mediscan_rag()
    
    print(f"📊 Current medicines in database: {rag.collection.count()}")
    
    print("\n📥 Adding sample medicines...")
    for med in SAMPLE_MEDICINES:
        name = med["medicine_name"]
        content_parts = []
        if med.get("use"):
            content_parts.append(f"Use:\n{med['use']}")
        if med.get("dosage"):
            content_parts.append(f"Dosage:\n{med['dosage']}")
        if med.get("precautions"):
            content_parts.append(f"Precautions:\n{med['precautions']}")
        if med.get("side_effects"):
            content_parts.append(f"Common Side Effects:\n{med['side_effects']}")
        
        content = "\n\n".join(content_parts)
        rag.add_medicine_document(name, content)
        print(f"  ✅ Added: {name}")
    
    print(f"\n📊 Total medicines in database: {rag.collection.count()}")
    print(f"📋 Medicine names available for autocomplete: {len(rag._medicine_names)}")
    
    # Test search
    print("\n🔍 Testing search for 'paracetamol'...")
    results = rag.search_medicines("paracetamol", n_results=3)
    for r in results:
        print(f"  - {r['medicine_name']} (similarity: {r['similarity']:.2f})")
    
    print("\n✅ Done! The MediScan RAG database is ready.")


if __name__ == "__main__":
    main()
