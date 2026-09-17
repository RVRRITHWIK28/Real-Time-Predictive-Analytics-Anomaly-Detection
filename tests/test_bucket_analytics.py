from src.processing.bucket_analytics import (
    BucketAnalyticsProcessor,
)


processor = BucketAnalyticsProcessor()


# --------------------------------------------------
# Add transactions
# --------------------------------------------------

transactions = [

    {
        "timestamp": "2026-09-16T10:20:05+00:00",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 3,
        "revenue": 3000.0,
    },

    {
        "timestamp": "2026-09-16T10:20:25+00:00",
        "product_id": "P1002",
        "store_id": "S001",
        "quantity": 5,
        "revenue": 5000.0,
    },

    {
        "timestamp": "2026-09-16T10:20:48+00:00",
        "product_id": "P1003",
        "store_id": "S002",
        "quantity": 4,
        "revenue": 4000.0,
    },
]


for transaction in transactions:

    processor.add_transaction(
        transaction
    )


# --------------------------------------------------
# Before bucket completion
# --------------------------------------------------

results = processor.process_completed_buckets(
    "2026-09-16T10:20:59+00:00"
)

print("Before bucket completion:")
print(results)

assert results == []


# --------------------------------------------------
# Process completed bucket
# --------------------------------------------------

results = processor.process_completed_buckets(
    "2026-09-16T10:21:00+00:00"
)

print("\nCompleted bucket results:")
print(results)

assert len(results) == 1


result = results[0]


print("\nBucket:")
print(result["bucket"])

print("\nTransactions:")
print(result["transactions"])

print("\nQuantity:")
print(result["quantity"])

print("\nRevenue:")
print(result["revenue"])


# --------------------------------------------------
# Validate bucket metrics
# --------------------------------------------------

assert result["transactions"] == 3

assert result["quantity"] == 12

assert result["revenue"] == 12000.0


# --------------------------------------------------
# Validate StreamAnalytics
# --------------------------------------------------

metrics = processor.analytics.get_metrics()

print("\nStream analytics metrics:")
print(metrics)


assert metrics["total_transactions"] == 3

assert metrics["total_quantity"] == 12

assert metrics["total_revenue"] == 12000.0

assert metrics["average_order_value"] == 4000.0


# --------------------------------------------------
# Verify duplicate prevention
# --------------------------------------------------

results = processor.process_completed_buckets(
    "2026-09-16T10:22:00+00:00"
)

print("\nAfter processing:")
print(results)

assert results == []


print(
    "\nBucket analytics test passed!"
)