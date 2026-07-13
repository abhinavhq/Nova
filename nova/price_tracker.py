"""
nova/price_tracker.py

Phase 6: Shopping - price tracking.

Records a product's price each time it's checked, so you can see price
history and get flagged when the price drops below what you last saw
(or below a target you set).
"""

import json
import os
from datetime import datetime

DEFAULT_PRICES_PATH = "nova_price_history.json"


def _load(filepath: str = DEFAULT_PRICES_PATH) -> dict:
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        return json.load(f)


def _save(data: dict, filepath: str = DEFAULT_PRICES_PATH):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def record_price(
    product_name: str,
    price: float,
    url: str = "",
    target_price: float = None,
    filepath: str = DEFAULT_PRICES_PATH,
) -> dict:
    """
    Record a price check for a product. Returns a dict with the new
    entry and whether this counts as a "drop" (lower than the last
    recorded price, or at/below target_price if given).
    """
    data = _load(filepath)
    history = data.get(product_name, {"url": url, "target_price": target_price, "checks": []})

    previous_price = history["checks"][-1]["price"] if history["checks"] else None
    is_drop = previous_price is not None and price < previous_price
    hit_target = target_price is not None and price <= target_price

    history["checks"].append({
        "price": price,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    if url:
        history["url"] = url
    if target_price is not None:
        history["target_price"] = target_price

    data[product_name] = history
    _save(data, filepath)

    if is_drop:
        print(f"[price_tracker] Price DROP for {product_name}: {previous_price} -> {price}")
    if hit_target:
        print(f"[price_tracker] {product_name} hit target price ({target_price})! Current: {price}")

    return {"product_name": product_name, "price": price, "is_drop": is_drop, "hit_target": hit_target}


def get_price_history(product_name: str, filepath: str = DEFAULT_PRICES_PATH) -> list[dict]:
    """Return all recorded price checks for a product, oldest first."""
    data = _load(filepath)
    return data.get(product_name, {}).get("checks", [])


def list_tracked_products(filepath: str = DEFAULT_PRICES_PATH) -> list[str]:
    """Return the names of all products currently being tracked."""
    return list(_load(filepath).keys())