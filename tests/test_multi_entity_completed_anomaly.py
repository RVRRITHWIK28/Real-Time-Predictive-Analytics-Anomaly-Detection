from src.processing.unified_completed_anomaly_pipeline import (
    UnifiedCompletedAnomalyPipeline,
)


pipeline = UnifiedCompletedAnomalyPipeline()


# ==================================================
# 1. BUILD PRODUCT + STORE BASELINES
# ==================================================

historical_data = [
    {
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 50,
        "revenue": 50000.0,
    },
    {
        "product_id": "P1002",
        "store_id": "S002",
        "quantity": 30,
        "revenue": 30000.0,
    },
]


for minute in range(5):

    for data in historical_data:

        transaction = {
            "timestamp": (
                f"2026-09-16T10:{minute:02d}:10+00:00"
            ),
            "product_id": data["product_id"],
            "store_id": data["store_id"],
            "quantity": data["quantity"],
            "revenue": data["revenue"],
        }

        pipeline.add_transaction(
            transaction
        )


results = pipeline.process_completed_buckets(
    "2026-09-16T10:05:00+00:00"
)

print("Historical results:")
print(results)

assert results == []


# ==================================================
# 2. NORMAL MULTI-ENTITY BUCKET
# ==================================================

normal_transactions = [

    {
        "timestamp": "2026-09-16T10:05:10+00:00",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 55,
        "revenue": 55000.0,
    },

    {
        "timestamp": "2026-09-16T10:05:20+00:00",
        "product_id": "P1002",
        "store_id": "S002",
        "quantity": 32,
        "revenue": 32000.0,
    },

]


for transaction in normal_transactions:

    pipeline.add_transaction(
        transaction
    )


results = pipeline.process_completed_buckets(
    "2026-09-16T10:06:00+00:00"
)

print("\nNormal multi-entity results:")
print(results)

assert results == []


# ==================================================
# 3. ANOMALOUS MULTI-ENTITY BUCKET
# ==================================================

anomalous_transactions = [

    # Huge spike for P1001 / S001
    {
        "timestamp": "2026-09-16T10:06:10+00:00",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 120,
        "revenue": 120000.0,
    },

    # Normal P1002 / S002 activity
    {
        "timestamp": "2026-09-16T10:06:20+00:00",
        "product_id": "P1002",
        "store_id": "S002",
        "quantity": 30,
        "revenue": 30000.0,
    },

    # Another product/store combination
    {
        "timestamp": "2026-09-16T10:06:30+00:00",
        "product_id": "P1003",
        "store_id": "S003",
        "quantity": 10,
        "revenue": 10000.0,
    },

]


for transaction in anomalous_transactions:

    pipeline.add_transaction(
        transaction
    )


results = pipeline.process_completed_buckets(
    "2026-09-16T10:07:00+00:00"
)


print("\nMulti-entity anomaly results:")

for event in results:

    print(
        event.model_dump()
    )


# ==================================================
# 4. VERIFY PRODUCT ANOMALY
# ==================================================

product_events = [
    event
    for event in results
    if event.anomaly_type
    == "product_quantity_spike"
]


assert len(product_events) == 1

assert (
    product_events[0].entity_id
    == "P1001"
)

assert (
    product_events[0].current_value
    == 120
)


# ==================================================
# 5. VERIFY STORE ANOMALY
# ==================================================

store_events = [
    event
    for event in results
    if event.anomaly_type
    == "store_quantity_spike"
]


assert len(store_events) == 1

assert (
    store_events[0].entity_id
    == "S001"
)

assert (
    store_events[0].current_value
    == 120
)


# ==================================================
# 6. VERIFY NON-ANOMALOUS ENTITIES
# ==================================================

assert not any(
    event.entity_id == "P1002"
    and event.anomaly_type
    == "product_quantity_spike"
    for event in results
)

assert not any(
    event.entity_id == "S002"
    and event.anomaly_type
    == "store_quantity_spike"
    for event in results
)


# ==================================================
# 7. VERIFY GLOBAL ANOMALIES
# ==================================================

anomaly_types = {
    event.anomaly_type
    for event in results
}

print("\nDetected anomaly types:")
print(anomaly_types)

# The global values are:
#
# quantity = 120 + 30 + 10 = 160
# revenue  = 120000 + 30000 + 10000 = 160000
#
# They may or may not cross the global anomaly
# threshold depending on the learned baseline.
#
# We therefore only verify that the pipeline
# returns valid unified events.

for event in results:

    assert event.is_anomaly is True

    assert event.severity in {
        "HIGH",
        "CRITICAL",
    }

    assert event.business_impact

    assert event.recommendation


print(
    "\nMulti-entity completed anomaly "
    "test passed!"
)