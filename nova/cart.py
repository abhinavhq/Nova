"""
nova/cart.py

Phase 6: Shopping - cart building.

Accumulate items you're considering across multiple sites/pages into one
list before deciding what to actually buy. Checkout itself is NOT part
of this module - that's a sensitive action and goes through NovaAgent's
confirmation gate (see agent.py SENSITIVE_KEYWORDS), same as any other
purchase-related click.
"""

import json
import os

DEFAULT_CART_PATH = "nova_cart.json"


def _load(filepath: str = DEFAULT_CART_PATH) -> list[dict]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)


def _save(items: list[dict], filepath: str = DEFAULT_CART_PATH):
    with open(filepath, "w") as f:
        json.dump(items, f, indent=2)


def add_to_cart(title: str, price: float, url: str = "", source: str = "", filepath: str = DEFAULT_CART_PATH) -> dict:
    """Add an item to Nova's running cart list."""
    items = _load(filepath)
    entry = {"title": title, "price": price, "url": url, "source": source}
    items.append(entry)
    _save(items, filepath)
    print(f"[cart] Added: {title} - {price}")
    return entry


def remove_from_cart(title: str, filepath: str = DEFAULT_CART_PATH) -> bool:
    """Remove an item from the cart by title."""
    items = _load(filepath)
    remaining = [i for i in items if i["title"] != title]
    if len(remaining) == len(items):
        print(f"[cart] No item found with title '{title}'")
        return False
    _save(remaining, filepath)
    print(f"[cart] Removed: {title}")
    return True


def list_cart(filepath: str = DEFAULT_CART_PATH) -> list[dict]:
    """List all items currently in the cart."""
    return _load(filepath)


def cart_total(filepath: str = DEFAULT_CART_PATH) -> float:
    """Sum of all item prices currently in the cart."""
    return sum(item["price"] for item in _load(filepath))