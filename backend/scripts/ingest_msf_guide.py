#!/usr/bin/env python3
"""
Script to ingest the MSF Essential Drugs Guide PDF into MediScan RAG database.
This parser is specifically designed for the MSF guideline format.

Usage:
    python scripts/ingest_msf_guide.py
"""

import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fitz  # PyMuPDF

from services.mediscan_rag_service import get_mediscan_rag

PDF_PATH = Path(__file__).resolve().parent.parent / "medicine_pdf" / "guideline-339-en.pdf"


def extract_medicines_from_pdf(pdf_path: str):
    """Extract medicine information from MSF Essential Drugs Guide"""
    
    doc = fitz.open(pdf_path)
    medicines = []
    
    current_medicine = None
    current_content = []
    
    print(f"📄 Processing {len(doc)} pages...")
    
    # Patterns for medicine headers
    # e.g., "AZITHROMYCIN oral", "PARACETAMOL = ACETAMINOPHEN oral", "COLECALCIFEROL = VITAMIN D3 oral"
    medicine_header_pattern = re.compile(
        r'^([A-Z][A-Z0-9\s\-\(\)=/]+)\s*(oral|injection|IV|IM|topical|eye|ear|nasal|rectal|vaginal|inhalation|sublingual|parenteral|external|ophthalmic)?\s*$',
        re.IGNORECASE
    )
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines and page numbers
            if not line or line.startswith('Page ') or len(line) < 4:
                continue
            
            # Check if this looks like a medicine header
            match = medicine_header_pattern.match(line)
            if match:
                medicine_name = match.group(1).strip()
                route = match.group(2) if match.group(2) else ""
                
                # Validate: must have mostly uppercase letters and be reasonable length
                if len(medicine_name) >= 4 and len(medicine_name) <= 80:
                    upper_count = sum(1 for c in medicine_name if c.isupper())
                    if upper_count >= len(medicine_name.replace(' ', '').replace('=', '').replace('-', '')) * 0.5:
                        
                        # Check if next lines contain typical medicine info keywords
                        next_lines = ' '.join(lines[i+1:i+15]).lower()
                        if any(kw in next_lines for kw in ['therapeutic action', 'indication', 'dosage', 'prescription', 'forms and strengths', 'contra-indication']):
                            
                            # Save previous medicine if exists
                            if current_medicine and current_content:
                                medicines.append({
                                    'name': current_medicine,
                                    'content': '\n'.join(current_content)
                                })
                            
                            # Start new medicine
                            full_name = f"{medicine_name} {route}".strip() if route else medicine_name
                            current_medicine = full_name
                            current_content = []
                            print(f"  Found: {current_medicine}")
            
            # Add content to current medicine
            if current_medicine and line:
                current_content.append(line)
        
        # Progress indicator
        if page_num % 100 == 0:
            print(f"  Processed {page_num}/{len(doc)} pages...")
    
    # Save last medicine
    if current_medicine and current_content:
        medicines.append({
            'name': current_medicine,
            'content': '\n'.join(current_content)
        })
    
    doc.close()
    return medicines


def parse_medicine_content(content: str):
    """Parse medicine content into structured sections"""
    
    sections = {
        'use': '',
        'dosage': '',
        'precautions': '',
        'side_effects': '',
        'forms': ''
    }
    
    content_lower = content.lower()
    
    # Extract therapeutic action / indications as "use"
    if 'therapeutic action' in content_lower or 'indication' in content_lower:
        # Find the section
        match = re.search(r'(?:therapeutic action|indication[s]?)(.*?)(?:forms and strengths|dosage|contra|precaution|adverse|$)', 
                         content, re.IGNORECASE | re.DOTALL)
        if match:
            sections['use'] = match.group(1).strip()[:1500]
    
    # Extract dosage
    if 'dosage' in content_lower:
        match = re.search(r'dosage[s]?\s*(?:and duration)?(.*?)(?:contra|precaution|adverse|side effect|$)', 
                         content, re.IGNORECASE | re.DOTALL)
        if match:
            sections['dosage'] = match.group(1).strip()[:1500]
    
    # Extract contraindications/precautions
    if 'contra' in content_lower or 'precaution' in content_lower:
        match = re.search(r'(?:contra-?indication|precaution)[s]?(.*?)(?:adverse|side effect|drug interaction|$)', 
                         content, re.IGNORECASE | re.DOTALL)
        if match:
            sections['precautions'] = match.group(1).strip()[:1500]
    
    # Extract adverse effects / side effects
    if 'adverse' in content_lower or 'side effect' in content_lower:
        match = re.search(r'(?:adverse effect|side effect)[s]?(.*?)(?:drug interaction|remarks|$)', 
                         content, re.IGNORECASE | re.DOTALL)
        if match:
            sections['side_effects'] = match.group(1).strip()[:1000]
    
    # Extract forms and strengths
    if 'forms and strengths' in content_lower:
        match = re.search(r'forms and strengths(.*?)(?:dosage|$)', 
                         content, re.IGNORECASE | re.DOTALL)
        if match:
            sections['forms'] = match.group(1).strip()[:500]
    
    return sections


def main():
    if not PDF_PATH.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        sys.exit(1)
    
    print(f"📄 Loading PDF: {PDF_PATH}")
    
    # Extract medicines
    medicines = extract_medicines_from_pdf(str(PDF_PATH))
    print(f"\n📊 Found {len(medicines)} medicines")
    
    if not medicines:
        print("❌ No medicines found in PDF")
        sys.exit(1)
    
    # Initialize RAG
    print("\n🔄 Initializing RAG service...")
    rag = get_mediscan_rag()
    
    # Add medicines to database
    print("\n📥 Adding medicines to vector database...")
    added = 0
    
    for med in medicines:
        name = med['name']
        raw_content = med['content']
        
        # Parse into sections
        sections = parse_medicine_content(raw_content)
        
        # Build formatted content
        content_parts = []
        if sections['use']:
            content_parts.append(f"Use:\n{sections['use']}")
        if sections['forms']:
            content_parts.append(f"Forms and Strengths:\n{sections['forms']}")
        if sections['dosage']:
            content_parts.append(f"Dosage:\n{sections['dosage']}")
        if sections['precautions']:
            content_parts.append(f"Precautions:\n{sections['precautions']}")
        if sections['side_effects']:
            content_parts.append(f"Common Side Effects:\n{sections['side_effects']}")
        
        # If no structured content, use raw content
        if not content_parts:
            content_parts.append(raw_content[:3000])
        
        content = "\n\n".join(content_parts)
        
        # Add to RAG
        try:
            rag.add_medicine_document(name, content, {"source": "MSF Essential Drugs Guide"})
            added += 1
        except Exception as e:
            print(f"  ⚠️ Error adding {name}: {e}")
    
    print(f"\n✅ Successfully added {added} medicines to database")
    print(f"📊 Total medicines in database: {rag.collection.count()}")
    print(f"📋 Medicine names for autocomplete: {len(rag._medicine_names)}")
    
    # Test search
    print("\n🔍 Testing search...")
    test_queries = ["paracetamol", "azithromycin", "amoxicillin", "ibuprofen"]
    for q in test_queries:
        results = rag.search_medicines(q, n_results=1)
        if results:
            print(f"  '{q}' → {results[0]['medicine_name']} (similarity: {results[0]['similarity']:.2f})")
        else:
            print(f"  '{q}' → No results")
    
    print("\n✅ Done! MediScan RAG database is ready.")


if __name__ == "__main__":
    main()
