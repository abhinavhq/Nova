"""
test_queue.py

Sanity check for Phase 2's final piece: give Nova a list of separate,
UNRELATED goals and confirm it runs each one independently and reports
back on all of them.
"""

from nova import NovaBrowser
from nova.planner import NovaOrchestrator


def main():
    goals = [
        "Go to Wikipedia and tell me the title of the featured article link, if any is visible on the homepage.",
        "Go to Wikipedia and search for 'Python programming language', then tell me the page title of the result.",
    ]

    with NovaBrowser(headless=False) as nb:
        nb.goto("https://www.wikipedia.org")

        orchestrator = NovaOrchestrator(browser=nb, max_steps_per_subtask=8)
        outcomes = orchestrator.run_queue(goals)

        print("\n=== QUEUE SUMMARY ===")
        for i, outcome in enumerate(outcomes, 1):
            print(f"\nGoal {i}: {outcome['goal']}")
            print(f"Result: {outcome['final_summary']}")

        nb.screenshot("phase2_queue_result.png")


if __name__ == "__main__":
    main()