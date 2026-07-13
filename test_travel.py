"""
test_travel.py

Sanity check for travel helpers: ranking options by price, filtering by
budget, and summarizing the price range - all on sample "flight" data
(no browser needed, this tests the ranking logic itself).

Real usage would feed this the output of compare_across_sources() run
against actual flight/hotel comparison sites.
"""

from nova.travel import find_best_options, filter_by_max_price, summarize_price_range
from nova.generate import generate_itinerary


def main():
    sample_flights = [
        {"route": "BLR -> NRT", "airline": "ANA", "price": "$680.00", "date": "2026-09-10"},
        {"route": "BLR -> NRT", "airline": "JAL", "price": "$725.50", "date": "2026-09-10"},
        {"route": "BLR -> NRT", "airline": "Air India", "price": "$590.00", "date": "2026-09-12"},
        {"route": "BLR -> NRT", "airline": "Singapore Air", "price": "$810.00", "date": "2026-09-10"},
        {"route": "BLR -> NRT", "airline": "Emirates", "price": "$1,020.00", "date": "2026-09-11"},
    ]

    print("=== PRICE RANGE SUMMARY ===")
    print(summarize_price_range(sample_flights))

    print("\n=== TOP 3 CHEAPEST ===")
    for opt in find_best_options(sample_flights, top_n=3):
        print(f"  {opt}")

    print("\n=== UNDER $700 ===")
    for opt in filter_by_max_price(sample_flights, max_price=700):
        print(f"  {opt}")

    print("\n=== ITINERARY WRITE-UP (using existing generate_itinerary) ===")
    top_options = find_best_options(sample_flights, top_n=3)
    itinerary = generate_itinerary(top_options, trip_context="BLR to Tokyo, flexible dates mid-September 2026")
    print(itinerary)


if __name__ == "__main__":
    main()