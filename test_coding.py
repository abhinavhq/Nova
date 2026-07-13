"""
test_coding.py

Sanity check for coding workflows: documentation lookup on Python's
official docs site (a stable, reliable target).
"""

from nova import NovaBrowser
from nova.coding_helper import lookup_documentation


def main():
    with NovaBrowser(headless=False) as nb:
        result = lookup_documentation(
            browser=nb,
            library_or_topic="Python",
            question="How do you create a list comprehension in Python? Give a brief example.",
            base_url="https://docs.python.org/3/",
        )
        print("\n=== DOCUMENTATION LOOKUP RESULT ===")
        print(result)


if __name__ == "__main__":
    main()