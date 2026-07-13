"""
test_headless.py

Sanity check for Phase 7: confirm headless mode actually works - Nova
running with no visible browser window, suitable for background/
unattended use once you trust a task.
"""

from nova import NovaBrowser
from nova.agent import NovaAgent


def main():
    print("Running in HEADLESS mode - no browser window should appear.\n")

    with NovaBrowser(headless=True) as nb:
        nb.goto("https://www.wikipedia.org")
        agent = NovaAgent(browser=nb, max_steps=6)
        result = agent.run("Search Wikipedia for 'machine learning' and tell me the resulting page title.")
        print("\nResult:", result)
        nb.screenshot("phase7_headless_result.png")

    print("\nDone. Check phase7_headless_result.png to confirm it actually ran correctly, "
          "even though no window was visible.")


if __name__ == "__main__":
    main()