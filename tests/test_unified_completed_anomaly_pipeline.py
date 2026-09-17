from src.processing.unified_completed_anomaly_pipeline import (
    UnifiedCompletedAnomalyPipeline,
)


pipeline = UnifiedCompletedAnomalyPipeline()


# ==================================================
# BUILD GLOBAL + PRODUCT + STORE BASELINES
# ==================================================

historical_data = [
    (100000, 100),
    (105000, 105),
    (98000, 98),
    (102000, 102),
    (101000, 101),
]


for index, (revenue, quantity) in enumerate(
    historical_data
):

    transaction = {
        "timestamp": (
            f"2026-09-16T10:{index:02d}:10+00:00"
        ),
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": quantity,
        "revenue": revenue,
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
# NORMAL BUCKET
# ==================================================

normal_transaction = {
    "timestamp": "2026-09-16T10:05:10+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 110,
    "revenue": 110000.0,
}

pipeline.add_transaction(
    normal_transaction
)

results = pipeline.process_completed_buckets(
    "2026-09-16T10:06:00+00:00"
)

print("\nNormal results:")
print(results)

assert results == []


# ==================================================
# ANOMALOUS BUCKET
# ==================================================

spike_transaction = {
    "timestamp": "2026-09-16T10:06:10+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 250,
    "revenue": 250000.0,
}

pipeline.add_transaction(
    spike_transaction
)

results = pipeline.process_completed_buckets(
    "2026-09-16T10:07:00+00:00"
)


print("\nAnomalous results:")

for event in results:

    print(
        event.model_dump()
    )


# We expect:
#
# 1. revenue spike
# 2. quantity spike
# 3. product quantity spike
# 4. store quantity spike

assert len(results) == 4


anomaly_types = {
    event.anomaly_type
    for event in results
}


assert "revenue_spike" in anomaly_types

assert "quantity_spike" in anomaly_types

assert (
    "product_quantity_spike"
    in anomaly_types
)

assert (
    "store_quantity_spike"
    in anomaly_types
)


# Validate every unified event

for event in results:

    assert event.is_anomaly is True

    assert event.severity in {
        "HIGH",
        "CRITICAL",
    }

    assert event.business_impact

    assert event.recommendation

    assert event.bucket.isoformat() == (
        "2026-09-16T10:06:00+00:00"
    )


print(
    "\nUnified completed anomaly "
    "pipeline test passed!"
)