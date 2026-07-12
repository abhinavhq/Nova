"""
test_compare.py

Sanity check for multi-source comparison: extract the same fields
(title, price) from TWO different category pages on books.toscrape.com,
combine them into one dataset tagged by source, and save one spreadsheet.

This mirrors a real comparison task like "check job listings across 3
job boards" - same fields, multiple sources, one combined output.
"""

from nova import NovaBrowser
from nova.compare import compare_across_sources
from nova.export import save_to_xlsx


def main():
    urls = [
        "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
        "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
    ]

    with NovaBrowser(headless=False) as nb:
        combined = compare_across_sources(
            browser=nb,
            urls=urls,
            fields=["title", "price"],
            item_description="books listed on this page",
        )

        print(f"\nCombined {len(combined)} total items:")
        for item in combined:
            print(f"  {item}")

        save_to_xlsx(combined, "nova_comparison.xlsx", sheet_title="Comparison")


if __name__ == "__main__":
    main()