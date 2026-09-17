from src.processing.stream_processor import StreamAnalytics


analytics = StreamAnalytics()


transactions = [
    {
        "event_id": "event_1",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 2,
        "revenue": 1000.00,
        "timestamp": "2026-09-16T10:00:00+00:00",
    },
    {
        "event_id": "event_2",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 3,
        "revenue": 1500.00,
        "timestamp": "2026-09-16T10:00:30+00:00",
    },
    {
        "event_id": "event_3",
        "product_id": "P1002",
        "store_id": "S002",
        "quantity": 1,
        "revenue": 500.00,
        "timestamp": "2026-09-16T10:01:10+00:00",
    },
]


for transaction in transactions:
    analytics.process_transaction(transaction)


window = analytics.get_window_metrics()


print("Time-window test completed!")

print(
    f"Last 60 seconds transactions: "
    f"{window['transactions']}"
)

print(
    f"Last 60 seconds quantity: "
    f"{window['quantity']}"
)

print(
    f"Last 60 seconds revenue: "
    f"Rs.{window['revenue']}"
)