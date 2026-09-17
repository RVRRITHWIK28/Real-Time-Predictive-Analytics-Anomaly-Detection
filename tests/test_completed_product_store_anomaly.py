from src.processing.completed_product_store_anomaly import (
    CompletedProductStoreAnomalyPipeline,
)


pipeline = CompletedProductStoreAnomalyPipeline()


# ==================================================
# PRODUCT BASELINE
# ==================================================

product_history = [
    (48, "P1001"),
    (52, "P1001"),
    (50, "P1001"),
    (51, "P1001"),
    (49, "P1001"),
]


for index, (quantity, product_id) in enumerate(
    product_history
):

    transaction = {
        "timestamp": (
            f"2026-09-16T10:{index:02d}:10+00:00"
        ),
        "product_id": product_id,
        "store_id": "S001",
        "quantity": quantity,
        "revenue": quantity * 1000.0,
    }

    pipeline.add_transaction(transaction)


results = pipeline.process_completed_buckets(
    "2026-09-16T10:05:00+00:00"
)

print("Historical product results:")
print(results)

assert results == []


# ==================================================
# PRODUCT NORMAL
# ==================================================

transaction = {
    "timestamp": "2026-09-16T10:05:10+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 55,
    "revenue": 55000.0,
}

pipeline.add_transaction(transaction)

results = pipeline.process_completed_buckets(
    "2026-09-16T10:06:00+00:00"
)

print("\nNormal product:")
print(results)

assert results == []


# ==================================================
# PRODUCT SPIKE
# ==================================================

transaction = {
    "timestamp": "2026-09-16T10:06:10+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 120,
    "revenue": 120000.0,
}

pipeline.add_transaction(transaction)

results = pipeline.process_completed_buckets(
    "2026-09-16T10:07:00+00:00"
)

print("\nProduct spike:")

for event in results:
    print(event.model_dump())


assert len(results) == 2

anomaly_types = {
    event.anomaly_type
    for event in results
}

assert "product_quantity_spike" in anomaly_types
assert "store_quantity_spike" in anomaly_types

product_events = [
    event
    for event in results
    if event.anomaly_type
    == "product_quantity_spike"
]

assert len(product_events) == 1

event = product_events[0]

assert event.entity_id == "P1001"

assert event.is_anomaly is True

assert event.severity in {
    "HIGH",
    "CRITICAL",
}

assert event.business_impact

assert event.recommendation


# ==================================================
# STORE BASELINE
# ==================================================

store_pipeline = (
    CompletedProductStoreAnomalyPipeline()
)


store_history = [
    48,
    52,
    50,
    51,
    49,
]


for index, quantity in enumerate(
    store_history
):

    transaction = {
        "timestamp": (
            f"2026-09-16T11:{index:02d}:10+00:00"
        ),
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": quantity,
        "revenue": quantity * 1000.0,
    }

    store_pipeline.add_transaction(
        transaction
    )


results = (
    store_pipeline
    .process_completed_buckets(
        "2026-09-16T11:05:00+00:00"
    )
)

print("\nHistorical store results:")
print(results)

assert results == []


# ==================================================
# STORE NORMAL
# ==================================================

transaction = {
    "timestamp": "2026-09-16T11:05:10+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 55,
    "revenue": 55000.0,
}

store_pipeline.add_transaction(
    transaction
)

results = (
    store_pipeline
    .process_completed_buckets(
        "2026-09-16T11:06:00+00:00"
    )
)

print("\nNormal store:")
print(results)

assert results == []


# ==================================================
# STORE SPIKE
# ==================================================

transaction = {
    "timestamp": "2026-09-16T11:06:10+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 120,
    "revenue": 120000.0,
}

store_pipeline.add_transaction(
    transaction
)

results = (
    store_pipeline
    .process_completed_buckets(
        "2026-09-16T11:07:00+00:00"
    )
)

print("\nStore spike:")

for event in results:
    print(event.model_dump())


assert len(results) == 2

anomaly_types = {
    event.anomaly_type
    for event in results
}

assert "product_quantity_spike" in anomaly_types
assert "store_quantity_spike" in anomaly_types

product_events = [
    event
    for event in results
    if event.anomaly_type
    == "product_quantity_spike"
]

assert len(results) == 2

anomaly_types = {
    event.anomaly_type
    for event in results
}

assert "product_quantity_spike" in anomaly_types
assert "store_quantity_spike" in anomaly_types

product_events = [
    event
    for event in results
    if event.anomaly_type
    == "product_quantity_spike"
]

assert len(product_events) == 1

event = product_events[0]

assert event.entity_id == "P1001"

assert event.is_anomaly is True

assert event.severity in {
    "HIGH",
    "CRITICAL",
}

assert event.business_impact

assert event.recommendation

print(
    "\nCompleted product/store anomaly "
    "pipeline test passed!"
)