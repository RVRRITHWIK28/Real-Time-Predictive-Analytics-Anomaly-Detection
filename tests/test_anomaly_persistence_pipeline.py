from datetime import datetime, timezone

from src.processing.anomaly_persistence_pipeline import (
    AnomalyPersistencePipeline,
)

from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_anomalies_collection,
)


pipeline = AnomalyPersistencePipeline()


# --------------------------------------------------
# Simulated detector output
# --------------------------------------------------

detection_result = {
    "is_anomaly": True,
    "reason": "Product quantity spike",
    "ratio": 2.33,
    "current_quantity": 120,
    "baseline_quantity": 51.4,
}


# --------------------------------------------------
# Process anomaly
# --------------------------------------------------

event, inserted_id = pipeline.process_anomaly(

    timestamp=datetime(
        2026,
        9,
        16,
        11,
        16,
        tzinfo=timezone.utc,
    ),

    bucket=datetime(
        2026,
        9,
        16,
        11,
        16,
        tzinfo=timezone.utc,
    ),

    anomaly_type="product_quantity_spike",

    entity_id="P1001",

    detection_result=detection_result,
)


print("Generated anomaly event:")
print(event.model_dump())


print("\nInserted MongoDB ID:")
print(inserted_id)


# --------------------------------------------------
# Verify MongoDB
# --------------------------------------------------

client = create_mongo_client()

try:

    database = get_database(client)

    collection = get_anomalies_collection(
        database
    )

    saved_event = collection.find_one(
        {"_id": inserted_id}
    )

    print("\nSaved MongoDB event:")
    print(saved_event)


    # --------------------------------------------------
    # Assertions
    # --------------------------------------------------

    assert saved_event is not None

    assert (
        saved_event["anomaly_type"]
        == "product_quantity_spike"
    )

    assert (
        saved_event["entity_id"]
        == "P1001"
    )

    assert (
        saved_event["current_value"]
        == 120.0
    )

    assert (
        saved_event["baseline_value"]
        == 51.4
    )

    assert (
        saved_event["ratio"]
        == 2.33
    )

    assert (
        saved_event["severity"]
        == "HIGH"
    )

    assert (
        "unusually high demand"
        in saved_event["business_impact"]
    )

    assert (
        "replenishment"
        in saved_event["recommendation"]
    )

finally:

    client.close()


print(
    "\nAnomaly persistence pipeline test passed!"
)