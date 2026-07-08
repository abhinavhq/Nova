"""
test_perception.py

Sanity check for Step 2: confirm Nova can look at a real page and
produce a compact, numbered list of interactive elements — the
foundation the LLM will reason over in Step 3.
"""

from nova import NovaBrowser
from nova.perception import get_page_summary


def main():
    with NovaBrowser(headless=False) as nb:
        nb.goto("https://www.wikipedia.org")

        summary, elements = get_page_summary(nb.page)
        print("\n=== What Nova sees on Wikipedia.org ===\n")
        print(summary)
        print(f"\nTotal interactive elements found: {len(elements)}")

        # Prove the ID -> action mapping actually works: find the
        # search box by matching text/attrs, then click + type into it.
        target = next(
            (e for e in elements if "search" in (e.text + e.attrs).lower()),
            None,
        )
        if target:
            print(f"\nUsing element [{target.id}] to search...")
            target.locator.click()
            target.locator.fill("large language models")
            nb.page.keyboard.press("Enter")
            nb.page.wait_for_timeout(2000)
            nb.screenshot("step2_search_result.png")
        else:
            print("\nCouldn't auto-find a search box in this snapshot.")


if __name__ == "__main__":
    main()