# ============================================================
#  services/medreport_pdf_service.py
#  PDF text extraction for MedReport Analyzer module.
#  Uses PyMuPDF and/or pdfplumber (both optional with graceful fallback).
# ============================================================

import io
import re

# Try PyMuPDF (new import path first, then legacy)
HAS_PYMUPDF = False
pymupdf = None
try:
    import pymupdf as pymupdf
    HAS_PYMUPDF = True
except ImportError:
    try:
        import fitz as pymupdf
        HAS_PYMUPDF = True
    except ImportError:
        pass

# pdfplumber is optional
HAS_PDFPLUMBER = False
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF bytes.
    Tries pdfplumber first (better for tables), then PyMuPDF as fallback.
    If neither is available, raises an error.
    """
    if not HAS_PYMUPDF and not HAS_PDFPLUMBER:
        raise ImportError(
            "Neither PyMuPDF nor pdfplumber is available. "
            "Install at least one: pip install PyMuPDF pdfplumber"
        )

    text = ""

    if HAS_PDFPLUMBER:
        text = _extract_with_pdfplumber(file_bytes)

    if (not text or len(text.strip()) < 50) and HAS_PYMUPDF:
        text = _extract_with_pymupdf(file_bytes)

    if not text or len(text.strip()) < 10:
        raise ValueError("Could not extract meaningful text from the PDF.")

    return _clean_text(text)


def _extract_with_pdfplumber(file_bytes: bytes) -> str:
    """Extract text using pdfplumber — excellent for tabular data."""
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            if row:
                                cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                                text_parts.append(" | ".join(cleaned_row))
        return "\n".join(text_parts)
    except Exception:
        return ""


def _extract_with_pymupdf(file_bytes: bytes) -> str:
    """Extract text using PyMuPDF — general-purpose fallback."""
    try:
        text_parts = []
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    except Exception:
        return ""


def _clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\s*-\s*\d+\s*-\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'[ \t]+', ' ', text)
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)
