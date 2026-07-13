"""
test_shopping.py

Sanity check for the remaining shopping pieces: review aggregation
(sentiment + pros/cons from raw review text) and cart building
(accumulate items, compute total).
"""

from nova.reviews import aggregate_reviews
from nova.cart import add_to_cart, remove_from_cart, list_cart, cart_total


def main():
    # --- Review aggregation ---
    sample_reviews = """
    Review 1: Battery life is incredible, lasts almost a week. Sound quality
    is great for the price. Wish the app was less buggy though.
    Review 2: Really impressed with the noise cancellation. Battery easily
    lasts 5-6 days. The companion app crashes sometimes.
    Review 3: Comfortable to wear all day. Battery life is excellent.
    Bluetooth connection drops occasionally when the app is open.
    Review 4: Great sound, solid battery life. App needs work - laggy and
    sometimes doesn't sync settings properly.
    """
    print("=== REVIEW AGGREGATION ===")
    summary = aggregate_reviews(sample_reviews)
    print(summary)

    # --- Cart building ---
    print("\n=== CART BUILDING ===")
    add_to_cart("Wireless Earbuds Pro", price=89.99, url="https://example.com/1", source="Site A")
    add_to_cart("USB-C Charging Cable", price=12.50, url="https://example.com/2", source="Site B")
    add_to_cart("Laptop Stand", price=34.99, url="https://example.com/3", source="Site A")

    print("\nCurrent cart:")
    for item in list_cart():
        print(f"  {item}")

    print(f"\nCart total: {cart_total():.2f}")

    remove_from_cart("USB-C Charging Cable")
    print("\nCart after removal:")
    for item in list_cart():
        print(f"  {item}")
    print(f"New total: {cart_total():.2f}")


if __name__ == "__main__":
    main()