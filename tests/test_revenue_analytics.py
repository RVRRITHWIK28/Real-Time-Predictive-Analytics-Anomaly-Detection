from src.processing.stream_processor import (
    StreamAnalytics,
)


analytics = StreamAnalytics()


transactions = [

    {
        "event_id": "revenue_001",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 2,
        "revenue": 1000.00,
        "timestamp": (
            "2026-09-16T10:40:15+00:00"
        ),
    },

    {
        "event_id": "revenue_002",
        "product_id": "P1002",
        "store_id": "S001",
        "quantity": 1,
        "revenue": 500.00,
        "timestamp": (
            "2026-09-16T10:40:45+00:00"
        ),
    },

    {
        "event_id": "revenue_003",
        "product_id": "P1003",
        "store_id": "S002",
        "quantity": 3,
        "revenue": 1500.00,
        "timestamp": (
            "2026-09-16T10:41:10+00:00"
        ),
    },
]


for transaction in transactions:

    analytics.process_transaction(
        transaction
    )


print(
    "Revenue analytics test completed!"
)


print("\nRevenue by minute:")

minute_revenue = (
    analytics.get_minute_revenue()
)


for bucket, revenue in (
    minute_revenue.items()
):

    print(
        f"{bucket} | "
        f"Revenue: Rs.{revenue}"
    )