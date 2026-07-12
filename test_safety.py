"""
test_safety.py

Sanity check for Phase 5:
1. Dry-run mode: agent should PREVIEW actions without ever touching the
   page for real.
2. Confirmation gate: when NOT in dry-run, clicking something that looks
   like a sensitive action (Buy, Submit, etc.) should pause and ask
   before proceeding.

Uses books.toscrape.com's "Add to basket" button as a stand-in sensitive
action - safe to test against since it's a sandbox site, but the button
text matches real sensitive-action patterns.
"""

from nova import NovaBrowser
from nova.agent import NovaAgent


def main():
    goal = "Go to the first book on this page and add it to the basket."

    print("\n############ DRY RUN ############\n")
    with NovaBrowser(headless=False) as nb:
        nb.goto("https://books.toscrape.com")
        agent = NovaAgent(browser=nb, max_steps=5, dry_run=True)
        result = agent.run(goal)
        print("\nDry run result:", result)

    print("\n############ REAL RUN (with confirmation) ############\n")
    with NovaBrowser(headless=False) as nb:
        nb.goto("https://books.toscrape.com")
        agent = NovaAgent(browser=nb, max_steps=5, dry_run=False, require_confirmation=True)
        result = agent.run(goal)
        print("\nReal run result:", result)


if __name__ == "__main__":
    main()