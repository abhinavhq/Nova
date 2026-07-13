"""
nova/travel.py

Phase 6: Travel planning.

Travel comparison reuses compare.py (multi-source extraction) and
generate.py's generate_itinerary() - the pieces already built. This
module adds the travel-specific logic on top: ranking/filtering options
by price, and a simple flexible-date helper.

Booking with confirmation is NOT special-cased here - it goes through
NovaAgent's existing sensitive-action confirmation gate (see agent.py
SENSITIVE_KEYWORDS, which already includes "book now", "reserve").
"""

import re


def _extract_price_value(price_str) -> float:
    """
    Pull a numeric value out of a price string like '£47.82' or
    '$1,234.00' for sorting/comparison. Returns float('inf') if no
    number can be parsed, so unparseable items sort last, not first.
    """
    if isinstance(price_str, (int, float)):
        return float(price_str)
    if not price_str:
        return float("inf")
    match = re.search(r"[\d,]+\.?\d*", str(price_str))
    if not match:
        return float("inf")
    try:
        return float(match.group().replace(",", ""))
    except ValueError:
        return float("inf")


def find_best_options(items: list[dict], price_field: str = "price", top_n: int = 5) -> list[dict]:
    """
    Rank a list of compared options (flights, hotels, activities) by
    price, ascending, and return the top N cheapest.
    """
    sortable = sorted(items, key=lambda item: _extract_price_value(item.get(price_field)))
    return sortable[:top_n]


def filter_by_max_price(items: list[dict], max_price: float, price_field: str = "price") -> list[dict]:
    """Filter a list of options down to those at or under max_price."""
    return [item for item in items if _extract_price_value(item.get(price_field)) <= max_price]


def summarize_price_range(items: list[dict], price_field: str = "price") -> dict:
    """Return min/max/avg price across a list of options, for a quick overview."""
    prices = [_extract_price_value(item.get(price_field)) for item in items]
    prices = [p for p in prices if p != float("inf")]
    if not prices:
        return {"min": None, "max": None, "avg": None, "count": 0}
    return {
        "min": min(prices),
        "max": max(prices),
        "avg": round(sum(prices) / len(prices), 2),
        "count": len(prices),
    }