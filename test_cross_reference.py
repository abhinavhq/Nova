"""
test_cross_reference.py

Sanity check for multi-site cross-referencing: find information on ONE
site, then use that specific information to search a DIFFERENT site,
and report combined findings. This proves NovaOrchestrator (built in
Phase 2) genuinely handles cross-site workflows, not just same-site
multi-step tasks.
"""

from nova import NovaBrowser
from nova.planner import NovaOrchestrator


def main():
    goal = (
        "First, go to Wikipedia and find out who created the Python programming "
        "language. Then, go to the Python Software Foundation website (python.org) "
        "and find out what year the current stable Python version was released. "
        "Report both findings together."
    )

    with NovaBrowser(headless=False) as nb:
        nb.goto("https://www.wikipedia.org")

        orchestrator = NovaOrchestrator(browser=nb, max_steps_per_subtask=10)
        outcome = orchestrator.run(goal)

        print("\n=== PLAN ===")
        for i, st in enumerate(outcome["subtasks"], 1):
            print(f"{i}. {st}")

        print("\n=== RESULTS PER SUBTASK ===")
        for i, r in enumerate(outcome["results"], 1):
            print(f"{i}. {r}")

        print("\n=== FINAL COMBINED SUMMARY ===")
        print(outcome["final_summary"])


if __name__ == "__main__":
    main()