import json
from collections import defaultdict
from datetime import datetime

def flatten_inventory(inv):
    flat = {}
    def recurse(d):
        for k,v in d.items():
            if isinstance(v, dict) and "name" in v:
                flat[k] = v
            else:
                recurse(v)
    recurse(inv["inventory"])
    return flat

def main():
    with open("inventory.json") as f:
        inventory = json.load(f)
    with open("ledger.json") as f:
        ledger = json.load(f)

    inv_flat = flatten_inventory(inventory)
    consumption = defaultdict(lambda: {"quantity": 0, "unit": None})

    # Assume ledger covers 28 days (4 weeks)
    days = 28

    for entry in ledger["ledger"]:
        for item, data in entry["items"].items():
            consumption[item]["quantity"] += data["quantity"]
            consumption[item]["unit"] = data["unit"]

    recommendations = {}

    for item, cons in consumption.items():
        daily_use = cons["quantity"] / days
        if item in inv_flat:
            stock = inv_flat[item]["quantity"]
            unit = inv_flat[item]["unit"]
            days_left = stock / daily_use if daily_use > 0 else float("inf")
            if days_left <= 7:
                # Refill to 14 days worth
                needed = daily_use*14 - stock
                # Don't recommend less than last purchase size
                min_purchase = cons["quantity"] / len(ledger["ledger"])
                order_qty = max(needed, min_purchase)
                recommendations[item] = {
                    "name": inv_flat[item]["name"],
                    "recommend_quantity": round(order_qty,2),
                    "unit": unit
                }

    with open("recommendation.json", "w") as f:
        json.dump(recommendations, f, indent=2)

    print("Recommended grocery list for Week 5:")
    for r in recommendations.values():
        print(f"- {r['name']}: BUY {r['recommend_quantity']} {r['unit']}")

if __name__ == "__main__":
    main()
