"""
nova/pdf_handler.py

Phase 3: PDF handling.

Nova will sometimes encounter a PDF mid-task (a job posting spec sheet,
a report, a form). This downloads a PDF from a URL and extracts its
text so the rest of Nova (extraction, summarization, the agent loop)
can reason about it the same way it reasons about a webpage.
"""

import os
import requests
from pypdf import PdfReader


def download_pdf(url: str, save_dir: str = "nova_downloads") -> str:
    """Download a PDF from a direct URL, return the local filepath."""
    os.makedirs(save_dir, exist_ok=True)
    filename = url.split("/")[-1].split("?")[0]
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    filepath = os.path.join(save_dir, filename)

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(response.content)

    print(f"[pdf_handler] Downloaded PDF to {filepath}")
    return filepath


def extract_pdf_text(filepath: str, max_chars: int = 8000) -> str:
    """Extract visible text from a local PDF file."""
    try:
        reader = PdfReader(filepath)
        text_parts = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n".join(text_parts)
        return full_text[:max_chars]
    except Exception as e:
        print(f"[pdf_handler] Failed to extract text from {filepath}: {e}")
        return ""


def read_pdf_from_url(url: str, save_dir: str = "nova_downloads") -> str:
    """Convenience: download a PDF and return its extracted text in one call."""
    filepath = download_pdf(url, save_dir)
    return extract_pdf_text(filepath)