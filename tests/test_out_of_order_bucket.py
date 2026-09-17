from src.processing.completed_bucket import (
    CompletedMinuteBucketProcessor,
)


processor = CompletedMinuteBucketProcessor()


# --------------------------------------------------
# Transactions arrive out of order
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
        # Arrives second, but has a later timestamp
        "timestamp": "2026-09-16T10:20:48+00:00",
        "product_id": "P1002",
        "store_id": "S001",
        "quantity": 5,
        "revenue": 5000.0,
    },
    {
        # Arrives last, but has an earlier timestamp
        "timestamp": "2026-09-16T10:20:25+00:00",
        "product_id": "P1003",
        "store_id": "S002",
        "quantity": 4,
        "revenue": 4000.0,
    },
]


for transaction in transactions:
    processor.add_transaction(transaction)


# --------------------------------------------------
# Bucket is still incomplete
# --------------------------------------------------

completed = processor.get_completed_buckets(
    "2026-09-16T10:20:59+00:00"
)

print("Completed buckets before 10:21:")
print(completed)

assert completed == []


# --------------------------------------------------
# Bucket becomes complete
# --------------------------------------------------

completed = processor.get_completed_buckets(
    "2026-09-16T10:21:00+00:00"
)

print("\nCompleted buckets at 10:21:")
print(completed)

assert len(completed) == 1


bucket = completed[0]


# --------------------------------------------------
# Get all transactions
# --------------------------------------------------

bucket_transactions = processor.get_transactions(
    bucket
)

print("\nTransactions in completed bucket:")
print(bucket_transactions)


# All 3 transactions must be present
assert len(bucket_transactions) == 3


# --------------------------------------------------
# Verify transaction IDs/products
# --------------------------------------------------

product_ids = [
    transaction["product_id"]
    for transaction in bucket_transactions
]

print("\nProducts in bucket:")
print(product_ids)

assert "P1001" in product_ids
assert "P1002" in product_ids
assert "P1003" in product_ids


# --------------------------------------------------
# Verify aggregate values
# --------------------------------------------------

total_quantity = sum(
    transaction["quantity"]
    for transaction in bucket_transactions
)

total_revenue = sum(
    transaction["revenue"]
    for transaction in bucket_transactions
)

print("\nTotal quantity:")
print(total_quantity)

print("\nTotal revenue:")
print(total_revenue)


assert total_quantity == 12
assert total_revenue == 12000.0


# --------------------------------------------------
# Mark bucket processed
# --------------------------------------------------

processor.mark_processed(bucket)


completed = processor.get_completed_buckets(
    "2026-09-16T10:22:00+00:00"
)

print("\nCompleted buckets after processing:")
print(completed)

assert completed == []


print(
    "\nOut-of-order bucket test passed!"
)