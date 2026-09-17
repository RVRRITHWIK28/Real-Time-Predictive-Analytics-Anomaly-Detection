from datetime import datetime, timezone

from src.ml.anomaly_event import AnomalyEvent
from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_anomalies_collection,
)
from src.database.anomaly_repository import (
    save_anomaly_event,
)


# Create test anomaly event

event = AnomalyEvent(
    timestamp=datetime(
        2026,
        9,
        16,
        10,
        16,
        tzinfo=timezone.utc,
    ),

    bucket=datetime(
        2026,
        9,
        16,
        10,
        16,
        tzinfo=timezone.utc,
    ),

    anomaly_type="product_quantity_spike",

    entity_id="P1001",

    is_anomaly=True,

    reason="Product quantity spike",

    ratio=2.33,

    current_value=120,

    baseline_value=51.4,

    severity="HIGH",

    message=(
        "Significant deviation from the normal baseline."
    ),

    business_impact=(
        "A product is experiencing unusually high demand."
    ),

    recommendation=(
        "Check product inventory and consider replenishment."
    ),
)


# Save event

inserted_id = save_anomaly_event(event)

print("Inserted anomaly ID:")
print(inserted_id)


# Verify from MongoDB

client = create_mongo_client()

try:

    database = get_database(client)

    collection = get_anomalies_collection(
        database
    )

    saved_event = collection.find_one(
        {"_id": inserted_id}
    )

    print("\nSaved anomaly:")
    print(saved_event)

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
        saved_event["severity"]
        == "HIGH"
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
        saved_event["business_impact"]
        == (
            "A product is experiencing unusually "
            "high demand."
        )
    )

finally:
    client.close()


print(
    "\nAnomaly MongoDB persistence test passed!"
)