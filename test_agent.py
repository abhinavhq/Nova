"""
test_agent.py

Sanity check for Step 3: give Nova a plain-English goal and watch it
decide + execute actions on its own, using perception + Cerebras.
"""

from nova import NovaBrowser
from nova.agent import NovaAgent


def main():
    goal = "Go to Wikipedia and search for 'artificial intelligence', then tell me the page title of the result."

    with NovaBrowser(headless=False) as nb:
        nb.goto("https://www.wikipedia.org")

        agent = NovaAgent(browser=nb, max_steps=10)
        result = agent.run(goal)

        print("\n=== FINAL RESULT ===")
        print(result)

        nb.screenshot("step3_agent_result.png")


if __name__ == "__main__":
    main()