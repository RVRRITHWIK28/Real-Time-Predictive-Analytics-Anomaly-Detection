from datetime import datetime, timezone

from src.ml.anomaly_event import AnomalyEvent


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

    message="Significant deviation from the normal baseline.",

    business_impact=(
        "A product is experiencing unusually high demand."
    ),

    recommendation=(
        "Check product inventory and consider replenishment."
    ),
)


print("Unified anomaly event:")
print(event.model_dump())


# Validation checks

assert event.anomaly_type == (
    "product_quantity_spike"
)

assert event.entity_id == "P1001"

assert event.is_anomaly is True

assert event.ratio == 2.33

assert event.current_value == 120

assert event.baseline_value == 51.4

assert event.severity == "HIGH"


print("\nUnified anomaly event test passed!")