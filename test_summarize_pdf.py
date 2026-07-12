"""
test_summarize_pdf.py

Sanity check for the last two Phase 3 pieces:
1. Summarize a real webpage's content
2. Download and extract text from a real PDF
"""

from nova import NovaBrowser
from nova.summarize import summarize_page
from nova.pdf_handler import read_pdf_from_url


def main():
    # --- Part 1: summarization ---
    with NovaBrowser(headless=False) as nb:
        nb.goto("https://en.wikipedia.org/wiki/Artificial_intelligence")
        summary = summarize_page(nb.page)
        print("\n=== PAGE SUMMARY ===")
        print(summary)

    # --- Part 2: PDF handling ---
    # W3C's dummy PDF - small, public, stable test file made for exactly this
    pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    print("\n=== PDF EXTRACTION ===")
    pdf_text = read_pdf_from_url(pdf_url)
    print(f"Extracted {len(pdf_text)} characters from PDF:")
    print(pdf_text[:500])


if __name__ == "__main__":
    main()