"""
nova/memory.py

Phase 7: Session memory.

Preferences that should persist across separate Nova runs (not just
within one script) - e.g. "always prefer the cheapest option", "skip
sites that require login", "my budget is usually under $500". This is
intentionally simple (a JSON key-value store), designed to be easy to
fold into JOI's existing SQLite memory system later if/when Nova merges
into JOI as a skill.
"""

import json
import os

DEFAULT_MEMORY_PATH = "nova_memory.json"


def _load(filepath: str = DEFAULT_MEMORY_PATH) -> dict:
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        return json.load(f)


def _save(memory: dict, filepath: str = DEFAULT_MEMORY_PATH):
    with open(filepath, "w") as f:
        json.dump(memory, f, indent=2)


def remember(key: str, value, filepath: str = DEFAULT_MEMORY_PATH):
    """Store a preference/fact for future runs."""
    memory = _load(filepath)
    memory[key] = value
    _save(memory, filepath)
    print(f"[memory] Remembered: {key} = {value}")


def recall(key: str, default=None, filepath: str = DEFAULT_MEMORY_PATH):
    """Retrieve a previously stored preference/fact."""
    return _load(filepath).get(key, default)


def forget(key: str, filepath: str = DEFAULT_MEMORY_PATH) -> bool:
    """Remove a stored preference/fact."""
    memory = _load(filepath)
    if key in memory:
        del memory[key]
        _save(memory, filepath)
        print(f"[memory] Forgot: {key}")
        return True
    return False


def all_memory(filepath: str = DEFAULT_MEMORY_PATH) -> dict:
    """Return everything currently remembered."""
    return _load(filepath)


def build_context_string(filepath: str = DEFAULT_MEMORY_PATH) -> str:
    """
    Format all stored memory as a short text block, ready to prepend to
    a NovaAgent goal so the agent's decisions can account for known
    preferences (e.g. "user prefers cheapest options").
    """
    memory = _load(filepath)
    if not memory:
        return ""
    lines = [f"- {k}: {v}" for k, v in memory.items()]
    return "KNOWN USER PREFERENCES:\n" + "\n".join(lines)