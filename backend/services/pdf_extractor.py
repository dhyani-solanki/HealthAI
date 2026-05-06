# ============================================================
#  services/pdf_extractor.py
#  Extract text from an uploaded PDF using pdfplumber.
#  Fallback to PyMuPDF (fitz) if pdfplumber is unavailable.
# ============================================================

import logging
from pathlib import Path

logger = logging.getLogger("data_insights.pdf_extractor")


def extract_text_from_pdf(file_path: str | Path) -> str:
    """
    Extract all text from a PDF file.
    Returns empty string on failure.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"PDF file not found: {file_path}")
        return ""

    # --- Try pdfplumber first ---
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        result = "\n".join(text_parts).strip()
        if result:
            logger.info(f"pdfplumber extracted {len(result)} chars from {path.name}")
            return result
    except ImportError:
        logger.warning("pdfplumber not installed, trying PyMuPDF...")
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}, trying PyMuPDF...")

    # --- Fallback: PyMuPDF (fitz) ---
    try:
        import fitz  # PyMuPDF
        text_parts = []
        doc = fitz.open(str(path))
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        result = "\n".join(text_parts).strip()
        if result:
            logger.info(f"PyMuPDF extracted {len(result)} chars from {path.name}")
            return result
    except ImportError:
        logger.error("Neither pdfplumber nor PyMuPDF is installed.")
    except Exception as e:
        logger.error(f"PyMuPDF also failed: {e}")

    return ""


def extract_text_from_txt(file_path: str | Path) -> str:
    """Read plain-text file."""
    try:
        return Path(file_path).read_text(encoding="utf-8", errors="ignore").strip()
    except Exception as e:
        logger.error(f"TXT read error: {e}")
        return ""


def extract_text(file_path: str | Path) -> str:
    """Auto-detect file type and extract text."""
    p = Path(file_path)
    if p.suffix.lower() == ".pdf":
        return extract_text_from_pdf(p)
    elif p.suffix.lower() in (".txt", ".csv"):
        return extract_text_from_txt(p)
    else:
        logger.warning(f"Unsupported file type: {p.suffix}")
        return ""
