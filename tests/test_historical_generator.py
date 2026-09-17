from datetime import datetime, timezone

from src.ingestion.historical_generator import (
    generate_historical_data,
    save_transactions_to_csv,
    get_product_demand_multiplier,
    get_store_demand_multiplier,
    get_trend_multiplier,
)


print("HISTORICAL DATASET TEST")
print("=" * 60)

start_date = datetime(
    2026,
    9,
    1,
    0,
    0,
    tzinfo=timezone.utc,
)

transactions = generate_historical_data(
    start_date=start_date,
    number_of_days=1,
)

print(f"Transactions generated: {len(transactions)}")

save_transactions_to_csv(
    transactions,
    "data/raw/historical_transactions.csv",
)

print("\nDataset saved successfully!")
print("Location: data/raw/historical_transactions.csv")

print("\nPRODUCT DEMAND TEST")
print("=" * 60)

for product_id in ["P1001", "P1002", "P1020"]:
    multiplier = get_product_demand_multiplier(product_id)
    print(f"{product_id} → {multiplier:.2f}")


print("\nSTORE DEMAND TEST")
print("=" * 60)

for store_id in ["S001", "S004", "S008"]:
    multiplier = get_store_demand_multiplier(store_id)
    print(f"{store_id} → {multiplier:.2f}")

print("\nTREND TEST")
print("=" * 60)

start_date = datetime(
    2026,
    9,
    1,
    0,
    0,
    tzinfo=timezone.utc,
)

test_dates = [
    datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc),
    datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
]

for event_time in test_dates:
    multiplier = get_trend_multiplier(
        event_time,
        start_date,
    )

    print(
        f"{event_time.date()} → "
        f"{multiplier:.2f}x"
    )