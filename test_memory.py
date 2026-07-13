"""
test_memory.py

Sanity check for session memory: store a preference, confirm it
persists, and confirm the agent's goal context actually reflects it
(not just that it's stored - that it would influence a real decision).
"""

from nova.memory import remember, recall, forget, all_memory, build_context_string


def main():
    # store a few preferences (in real usage, set once, reused across many runs)
    remember("budget_preference", "always prefer the cheapest option unless quality is clearly worse")
    remember("preferred_currency", "USD")
    remember("skip_sites_requiring_login", True)

    print("\n=== ALL STORED MEMORY ===")
    print(all_memory())

    print("\n=== RECALL SINGLE VALUE ===")
    print("budget_preference:", recall("budget_preference"))
    print("nonexistent_key (with default):", recall("nonexistent_key", default="not set"))

    print("\n=== CONTEXT STRING (what gets prepended to agent goals) ===")
    print(build_context_string())

    forget("preferred_currency")
    print("\n=== AFTER FORGETTING preferred_currency ===")
    print(all_memory())


if __name__ == "__main__":
    main()