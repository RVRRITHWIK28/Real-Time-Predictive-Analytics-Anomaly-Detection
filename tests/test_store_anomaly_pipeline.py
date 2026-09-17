from src.processing.store_anomaly_pipeline import StoreAnomalyPipeline


pipeline = StoreAnomalyPipeline()


# Build historical baseline
historical_quantities = [48, 52, 50, 51, 49]

for quantity in historical_quantities:

    transaction = {
        "timestamp": "2026-09-16T10:00:00+00:00",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": quantity,
        "revenue": quantity * 1000.0,
    }

    result = pipeline.process_transaction(transaction)

    print(
        f"Historical quantity: {quantity} | "
        f"Result: {result}"
    )


# Normal quantity
normal_transaction = {
    "timestamp": "2026-09-16T10:05:00+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 55,
    "revenue": 55000.0,
}

normal_result = pipeline.process_transaction(
    normal_transaction
)

print("\nNormal:")
print(normal_result)


# Spike
spike_transaction = {
    "timestamp": "2026-09-16T10:06:00+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 120,
    "revenue": 120000.0,
}

spike_result = pipeline.process_transaction(
    spike_transaction
)

print("\nSpike:")
print(spike_result)


# Drop
drop_transaction = {
    "timestamp": "2026-09-16T10:07:00+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 20,
    "revenue": 20000.0,
}

drop_result = pipeline.process_transaction(
    drop_transaction
)

print("\nDrop:")
print(drop_result)


assert normal_result["is_anomaly"] is False
assert normal_result["severity"] == "NORMAL"

assert spike_result["is_anomaly"] is True
assert spike_result["reason"] == "Store quantity spike"
assert spike_result["severity"] == "HIGH"

assert drop_result["is_anomaly"] is True
assert drop_result["reason"] == "Store quantity drop"
assert drop_result["severity"] == "CRITICAL"


print("\nStore anomaly pipeline test passed!")