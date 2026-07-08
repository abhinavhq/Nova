"""
test_browser.py

Sanity check for Step 1: confirm Playwright + NovaBrowser work end to end.
Run this directly in PyCharm. You should see a real Chromium window open,
navigate to a page, and a screenshot saved next to this file.
"""

from nova.browser import NovaBrowser

def main():
    with NovaBrowser(headless=False) as nb:
        nb.goto("https://example.com")
        print("Title:", nb.get_title())
        print("URL:", nb.get_url())
        nb.screenshot("step1_screenshot.png")

        # try a second nav + a small interaction to prove clicking works
        nb.goto("https://www.wikipedia.org")
        nb.type_into("#searchInput", "artificial intelligence", press_enter=True)
        nb.page.wait_for_timeout(2000)
        nb.screenshot("step1_wiki_search.png")

if __name__ == "__main__":
    main()