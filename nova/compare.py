"""
nova/compare.py

Phase 3: Multi-source comparison.

extraction.py pulls structured data from ONE page. Real comparison tasks
("find AI internships across 3 job boards and compare them") need the
same fields extracted from SEVERAL pages, then combined into one table.

compare_across_sources() visits a list of URLs one at a time, extracts
the same fields from each using extraction.py, tags each row with which
source it came from, and returns one combined list ready for export.py.
"""

from nova.browser import NovaBrowser
from nova.extraction import extract_structured_data


def compare_across_sources(
    browser: NovaBrowser,
    urls: list[str],
    fields: list[str],
    item_description: str = "items",
) -> list[dict]:
    """
    Visit each URL in `urls`, extract `fields` from each page, and combine
    all results into one list - each row tagged with its source URL so
    you can tell where each item came from in the final spreadsheet.
    """
    combined: list[dict] = []

    for i, url in enumerate(urls, 1):
        print(f"\n[compare] Source {i}/{len(urls)}: {url}")
        try:
            browser.goto(url)
        except Exception as e:
            print(f"[compare] Failed to load {url}: {e}")
            continue

        items = extract_structured_data(
            page=browser.page,
            fields=fields,
            item_description=item_description,
        )
        print(f"[compare] Extracted {len(items)} items from {url}")

        for item in items:
            item["source_url"] = url
            combined.append(item)

    print(f"\n[compare] Total combined items across {len(urls)} sources: {len(combined)}")
    return combined