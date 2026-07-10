"""
test_extraction.py

Sanity check for Phase 3: navigate to a page with a list of items,
extract structured data (title, price, rating) into real Python dicts,
and save it as an actual .xlsx spreadsheet file.

Uses books.toscrape.com - a public sandbox site specifically built for
practicing scraping/extraction, with placeholder book listings. This
mirrors exactly what a real task (e.g. internship listings, job postings)
would need: extract N items with structured fields, save to a spreadsheet.
"""

from nova import NovaBrowser
from nova.extraction import extract_structured_data
from nova.export import save_to_xlsx


def main():
    with NovaBrowser(headless=False) as nb:
        nb.goto("https://books.toscrape.com")

        items = extract_structured_data(
            page=nb.page,
            fields=["title", "price", "rating"],
            item_description="books listed on this page",
        )

        print(f"\nExtracted {len(items)} items:")
        for item in items:
            print(f"  {item}")

        save_to_xlsx(items, "nova_extracted_books.xlsx", sheet_title="Books")

        nb.screenshot("phase3_extraction_result.png")


if __name__ == "__main__":
    main()