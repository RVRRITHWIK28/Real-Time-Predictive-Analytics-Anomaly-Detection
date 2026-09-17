from src.processing.stream_processor import StreamAnalytics


analytics = StreamAnalytics()

transactions = [
    {
        "event_id": "test_001",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 2,
        "revenue": 1000.00,
    },
    {
        "event_id": "test_002",
        "product_id": "P1001",
        "store_id": "S002",
        "quantity": 3,
        "revenue": 1500.00,
    },
    {
        "event_id": "test_003",
        "product_id": "P1002",
        "store_id": "S001",
        "quantity": 1,
        "revenue": 500.00,
    },
]


for transaction in transactions:
    analytics.process_transaction(transaction)


metrics = analytics.get_metrics()

print("Stream analytics test completed!")

print(
    f"Total transactions : "
    f"{metrics['total_transactions']}"
)

print(
    f"Total quantity     : "
    f"{metrics['total_quantity']}"
)

print(
    f"Total revenue      : "
    f"Rs.{metrics['total_revenue']}"
)

print(
    f"Average order value: "
    f"Rs.{metrics['average_order_value']}"
)


print("\nProduct metrics:")

for product_id, data in analytics.get_product_metrics().items():
    print(
        f"{product_id} | "
        f"Transactions: {data['transactions']} | "
        f"Quantity: {data['quantity']} | "
        f"Revenue: Rs.{round(data['revenue'], 2)}"
    )


print("\nStore metrics:")

for store_id, data in analytics.get_store_metrics().items():
    print(
        f"{store_id} | "
        f"Transactions: {data['transactions']} | "
        f"Quantity: {data['quantity']} | "
        f"Revenue: Rs.{round(data['revenue'], 2)}"
    )