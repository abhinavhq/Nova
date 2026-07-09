"""
test_planner.py

Sanity check for Phase 2: give Nova a multi-part goal and watch it
break the goal into subtasks, then execute each one in order.
"""

from nova import NovaBrowser
from nova.planner import NovaOrchestrator


def main():
    goal = (
        "Go to Wikipedia and search for 'machine learning'. "
        "Then find and tell me the name of one related topic linked "
        "from that page."
    )

    with NovaBrowser(headless=False) as nb:
        nb.goto("https://www.wikipedia.org")

        orchestrator = NovaOrchestrator(browser=nb, max_steps_per_subtask=8)
        outcome = orchestrator.run(goal)

        print("\n=== PLAN ===")
        for i, st in enumerate(outcome["subtasks"], 1):
            print(f"{i}. {st}")

        print("\n=== RESULTS ===")
        for i, r in enumerate(outcome["results"], 1):
            print(f"{i}. {r}")

        print("\n=== FINAL SUMMARY ===")
        print(outcome["final_summary"])

        nb.screenshot("phase2_orchestrator_result.png")


if __name__ == "__main__":
    main()