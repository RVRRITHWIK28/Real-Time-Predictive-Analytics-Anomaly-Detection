from datetime import datetime, timezone

from src.processing.unified_anomaly_pipeline import (
    UnifiedAnomalyPipeline,
)


pipeline = UnifiedAnomalyPipeline()


# --------------------------------------------------
# Simulated product anomaly detector output
# --------------------------------------------------

detection_result = {
    "is_anomaly": True,
    "reason": "Product quantity spike",
    "ratio": 2.33,
    "current_quantity": 120,
    "baseline_quantity": 51.4,
}


event = pipeline.create_event(
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

    detection_result=detection_result,
)


print("Unified anomaly event:")
print(event.model_dump())


# --------------------------------------------------
# Validation
# --------------------------------------------------

assert event.anomaly_type == (
    "product_quantity_spike"
)

assert event.entity_id == "P1001"

assert event.is_anomaly is True

assert event.reason == (
    "Product quantity spike"
)

assert event.ratio == 2.33

assert event.current_value == 120

assert event.baseline_value == 51.4

assert event.severity == "HIGH"

assert (
    "unusually high demand"
    in event.business_impact
)

assert (
    "replenishment"
    in event.recommendation
)


print(
    "\nUnified anomaly pipeline test passed!"
)