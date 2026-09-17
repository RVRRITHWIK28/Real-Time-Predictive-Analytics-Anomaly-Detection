from src.processing.completed_anomaly_persistence import (
    CompletedAnomalyPersistencePipeline,
)

from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_anomalies_collection,
)


pipeline = CompletedAnomalyPersistencePipeline()


# --------------------------------------------------
# Historical baseline
# --------------------------------------------------

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
            f"2026-09-16T10:{index:02d}:00+00:00"
        ),
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": quantity,
        "revenue": revenue,
    }

    pipeline.add_transaction(transaction)


# Process historical buckets

results = pipeline.process_completed_buckets(
    "2026-09-16T10:05:00+00:00"
)

assert results == []


# --------------------------------------------------
# Normal bucket
# --------------------------------------------------

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

assert results == []


# --------------------------------------------------
# Anomalous bucket
# --------------------------------------------------

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


print("\nSaved anomaly events:")

for item in results:

    event = item["event"]
    inserted_id = item["inserted_id"]

    print(
        event.model_dump()
    )

    print(
        "MongoDB ID:",
        inserted_id
    )


# We expect two anomalies:
# 1. revenue spike
# 2. quantity spike

assert len(results) == 2


anomaly_types = {
    item["event"].anomaly_type
    for item in results
}

assert "revenue_spike" in anomaly_types
assert "quantity_spike" in anomaly_types


for item in results:

    event = item["event"]

    assert event.is_anomaly is True

    assert event.severity in {
        "HIGH",
        "CRITICAL",
    }

    assert event.entity_id == "GLOBAL"

    assert event.business_impact

    assert event.recommendation

    assert item["inserted_id"] is not None


# --------------------------------------------------
# Verify MongoDB
# --------------------------------------------------

client = create_mongo_client()

try:

    database = get_database(client)

    collection = get_anomalies_collection(
        database
    )

    documents = list(
        collection.find(
            {}
        ).sort(
            "_id",
            -1
        ).limit(10)
    )

    print(
        "\nLatest MongoDB anomaly documents:"
    )

    for document in documents:
        print(document)

    assert len(documents) >= 2

finally:

    client.close()


print(
    "\nCompleted anomaly persistence test passed!"
)