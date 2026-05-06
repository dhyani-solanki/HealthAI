#!/usr/bin/env python3
"""
Script to ingest medicine PDF into the MediScan RAG vector database.

Usage:
    python scripts/ingest_medicine_pdf.py path/to/medicine.pdf

Or place your PDF in backend/mediscan_data/ and run:
    python scripts/ingest_medicine_pdf.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.mediscan_rag_service import get_mediscan_rag


def ingest_pdf(pdf_path: str):
    """Ingest a single PDF file"""
    print(f"📄 Ingesting: {pdf_path}")
    
    rag = get_mediscan_rag()
    count = rag.ingest_pdf(pdf_path)
    
    print(f"✅ Ingested {count} medicines from {pdf_path}")
    return count


def ingest_all_pdfs_in_directory(directory: str):
    """Ingest all PDFs in a directory"""
    pdf_dir = Path(directory)
    if not pdf_dir.exists():
        print(f"❌ Directory not found: {directory}")
        return 0
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"⚠️ No PDF files found in {directory}")
        return 0
    
    total = 0
    for pdf_file in pdf_files:
        total += ingest_pdf(str(pdf_file))
    
    return total


def main():
    if len(sys.argv) > 1:
        # Ingest specific PDF file
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"❌ File not found: {pdf_path}")
            sys.exit(1)
        
        if pdf_path.endswith('.pdf'):
            ingest_pdf(pdf_path)
        else:
            print("❌ Please provide a PDF file")
            sys.exit(1)
    else:
        # Ingest all PDFs from default directory
        default_dir = Path(__file__).resolve().parent.parent / "mediscan_data"
        default_dir.mkdir(exist_ok=True)
        
        print(f"📁 Looking for PDFs in: {default_dir}")
        total = ingest_all_pdfs_in_directory(str(default_dir))
        
        if total == 0:
            print(f"\n💡 To ingest medicines:")
            print(f"   1. Place your medicine PDF in: {default_dir}")
            print(f"   2. Run this script again")
            print(f"\n   Or specify a PDF path:")
            print(f"   python {sys.argv[0]} path/to/medicine.pdf")
    
    # Show stats
    rag = get_mediscan_rag()
    print(f"\n📊 Total medicines in database: {rag.collection.count()}")
    print(f"📋 Medicine names available: {len(rag._medicine_names)}")


if __name__ == "__main__":
    main()
