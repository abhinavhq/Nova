"""
test_price_tracker.py

Sanity check for price tracking: record a product's price multiple
times and confirm drops/target hits are detected correctly.
"""

from nova.price_tracker import record_price, get_price_history, list_tracked_products


def main():
    product = "Sony WH-1000XM5 Headphones"

    print("=== Recording price checks ===")
    record_price(product, price=349.99, url="https://example.com/headphones", target_price=280.00)
    record_price(product, price=329.99, url="https://example.com/headphones", target_price=280.00)
    record_price(product, price=279.99, url="https://example.com/headphones", target_price=280.00)
    record_price(product, price=299.99, url="https://example.com/headphones", target_price=280.00)  # price went back up

    print("\n=== Price history ===")
    for check in get_price_history(product):
        print(f"  {check}")

    print("\n=== Tracked products ===")
    print(list_tracked_products())


if __name__ == "__main__":
    main()