from datetime import datetime, timezone

from src.ingestion.data_generator import generate_transaction

from src.ingestion.historical_generator import get_transaction_count

from src.ingestion.historical_generator import generate_historical_data


print("HISTORICAL TRANSACTION TEST")
print("=" * 60)

event_times = [
    datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 1, 13, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 1, 19, 0, tzinfo=timezone.utc),
]


for i, event_time in enumerate(event_times, start=1):
    event = generate_transaction(event_time)

    print(f"\nTransaction {i}")
    print(f"Timestamp : {event.timestamp}")
    print(f"Product   : {event.product_id}")
    print(f"Quantity  : {event.quantity}")
    print(f"Revenue   : ₹{event.revenue}")


print("\nHistorical timestamp test completed successfully!")

print("\nTRANSACTION COUNT TEST")
print("=" * 60)

test_times = [
    datetime(2026, 9, 1, 2, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 1, 19, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 5, 19, 0, tzinfo=timezone.utc),
]

for event_time in test_times:
    count = get_transaction_count(
    event_time,
    datetime(
        2026,
        9,
        1,
        0,
        0,
        tzinfo=timezone.utc,
    ),
)

    print(
        f"{event_time} → "
        f"{count} transactions"
    )

print("\nHISTORICAL DATA GENERATION TEST")
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

print(f"Total transactions generated: {len(transactions)}")

print("\nFirst transaction:")
print(transactions[0])

print("\nLast transaction:")
print(transactions[-1])

print("\nHistorical data generation completed successfully!")