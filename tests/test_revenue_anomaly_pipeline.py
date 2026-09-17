from src.processing.revenue_anomaly_pipeline import (
    RevenueAnomalyPipeline,
)


pipeline = RevenueAnomalyPipeline()


print("Building revenue baseline...")


# Historical revenue
historical_revenues = [
    100000,
    105000,
    98000,
    102000,
    101000,
]


for index, revenue in enumerate(
    historical_revenues
):

    minute = 10 + index

    transaction = {
        "timestamp": (
            f"2026-09-16T10:{minute:02d}:00+00:00"
        ),
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 1,
        "revenue": revenue,
    }

    result = pipeline.process_transaction(
        transaction
    )

    print(result)


# Normal revenue
normal_transaction = {
    "timestamp": "2026-09-16T10:15:00+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 1,
    "revenue": 110000,
}

normal_result = pipeline.process_transaction(
    normal_transaction
)

print("\nNormal revenue:")
print(normal_result)


# Revenue spike
spike_transaction = {
    "timestamp": "2026-09-16T10:16:00+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 1,
    "revenue": 250000,
}

spike_result = pipeline.process_transaction(
    spike_transaction
)

print("\nRevenue spike:")
print(spike_result)


# Revenue drop
drop_transaction = {
    "timestamp": "2026-09-16T10:17:00+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 1,
    "revenue": 30000,
}

drop_result = pipeline.process_transaction(
    drop_transaction
)

print("\nRevenue drop:")
print(drop_result)


# Assertions

assert normal_result["is_anomaly"] is False
assert normal_result["severity"] == "NORMAL"

assert spike_result["is_anomaly"] is True
assert spike_result["reason"] == "Revenue spike"
assert spike_result["severity"] == "HIGH"

assert drop_result["is_anomaly"] is True
assert drop_result["reason"] == "Revenue drop"
assert drop_result["severity"] == "CRITICAL"


print(
    "\nRevenue anomaly pipeline test passed!"
)