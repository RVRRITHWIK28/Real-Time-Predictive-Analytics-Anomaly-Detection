from src.processing.unified_anomaly_persistence import (
    UnifiedAnomalyPersistencePipeline,
)

from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_anomalies_collection,
)


print("TEST FILE STARTED")


pipeline = UnifiedAnomalyPersistencePipeline()


# ==================================================
# BUILD BASELINES
# ==================================================

historical_data = [
    (100000, 50),
    (105000, 52),
    (98000, 50),
    (102000, 51),
    (101000, 49),
]


for minute, (revenue, quantity) in enumerate(
    historical_data
):

    transaction = {
        "timestamp": (
            f"2026-09-16T10:{minute:02d}:10+00:00"
        ),
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": quantity,
        "revenue": revenue,
    }

    pipeline.add_transaction(
        transaction
    )


# Process historical buckets

results = pipeline.process_completed_buckets(
    "2026-09-16T10:05:00+00:00"
)

assert results == []


# ==================================================
# NORMAL BUCKET
# ==================================================

normal_transaction = {
    "timestamp": "2026-09-16T10:05:10+00:00",
    "product_id": "P1001",
    "store_id": "S001",
    "quantity": 55,
    "revenue": 110000.0,
}

pipeline.add_transaction(
    normal_transaction
)


results = pipeline.process_completed_buckets(
    "2026-09-16T10:06:00+00:00"
)

assert results == []


# ==================================================
# ANOMALOUS BUCKET
# ==================================================

anomaly_transactions = [

    {
        "timestamp": "2026-09-16T10:06:10+00:00",
        "product_id": "P1001",
        "store_id": "S001",
        "quantity": 120,
        "revenue": 120000.0,
    },

    {
        "timestamp": "2026-09-16T10:06:20+00:00",
        "product_id": "P1002",
        "store_id": "S002",
        "quantity": 30,
        "revenue": 30000.0,
    },

]


for transaction in anomaly_transactions:

    pipeline.add_transaction(
        transaction
    )


print(
    "\nTransactions added:"
)

for transaction in anomaly_transactions:

    print(transaction)


# ==================================================
# PROCESS COMPLETED BUCKET
# ==================================================

results = pipeline.process_completed_buckets(
    "2026-09-16T10:07:00+00:00"
)


print(
    "\nResults count:",
    len(results)
)


print(
    "\nSaved events:"
)


for item in results:

    event = item["event"]

    print(
        event.model_dump()
    )

    print(
        "MongoDB ID:",
        item["inserted_id"]
    )


# ==================================================
# VERIFY EVENTS
# ==================================================

assert len(results) >= 2


product_events = [
    item
    for item in results
    if item["event"].anomaly_type
    == "product_quantity_spike"
]


store_events = [
    item
    for item in results
    if item["event"].anomaly_type
    == "store_quantity_spike"
]


assert len(product_events) == 1

assert len(store_events) == 1


assert (
    product_events[0]["event"].entity_id
    == "P1001"
)

assert (
    store_events[0]["event"].entity_id
    == "S001"
)


# ==================================================
# VERIFY MONGODB
# ==================================================

client = create_mongo_client()

try:

    database = get_database(client)

    collection = get_anomalies_collection(
        database
    )

    documents = list(
        collection.find(
            {
                "bucket": "2026-09-16T10:06:00Z"
            }
        )
    )

    print(
        "\nMongoDB documents found:",
        len(documents)
    )


    for document in documents:

        print(document)


    assert len(documents) >= 2


    anomaly_types = {
        document["anomaly_type"]
        for document in documents
    }


    assert (
        "product_quantity_spike"
        in anomaly_types
    )

    assert (
        "store_quantity_spike"
        in anomaly_types
    )


finally:

    client.close()


print(
    "\nUnified anomaly persistence "
    "test passed!"
)