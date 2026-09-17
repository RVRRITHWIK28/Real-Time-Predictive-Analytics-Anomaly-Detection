from datetime import datetime, timezone

from src.processing.stream_processor import StreamAnalytics


analytics = StreamAnalytics()


transactions = [
    {
        "timestamp": "2026-09-16T10:40:15+00:00",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 3,
        "revenue": 3000.0,
    },
    {
        "timestamp": "2026-09-16T10:40:42+00:00",
        "product_id": "P1002",
        "store_id": "S001",
        "quantity": 5,
        "revenue": 5000.0,
    },
    {
        "timestamp": "2026-09-16T10:41:10+00:00",
        "product_id": "P1003",
        "store_id": "S002",
        "quantity": 4,
        "revenue": 4000.0,
    },
    {
        "timestamp": "2026-09-16T10:41:30+00:00",
        "product_id": "P1004",
        "store_id": "S001",
        "quantity": 2,
        "revenue": 2000.0,
    },
]


for transaction in transactions:
    analytics.process_transaction(transaction)


store_quantity = (
    analytics.get_store_minute_quantity()
)


print("Store quantity per minute:")
print(store_quantity)


minute_1040 = datetime(
    2026,
    9,
    16,
    10,
    40,
    tzinfo=timezone.utc,
)

minute_1041 = datetime(
    2026,
    9,
    16,
    10,
    41,
    tzinfo=timezone.utc,
)


# S001:
# 10:40 → 3 + 5 = 8
# 10:41 → 2
assert store_quantity["S001"][
    minute_1040
] == 8

assert store_quantity["S001"][
    minute_1041
] == 2


# S002:
# 10:41 → 4
assert store_quantity["S002"][
    minute_1041
] == 4


print(
    "\nStore quantity analytics test passed!"
)