from src.ml.store_anomaly_detector import (
    StoreQuantityAnomalyDetector,
)


detector = StoreQuantityAnomalyDetector(
    upper_threshold=2.0,
    lower_threshold=0.5,
    history_size=5,
)


store_id = "S001"


print("Building store baseline...\n")


historical_quantities = [
    48,
    52,
    50,
    51,
    49,
]


for quantity in historical_quantities:

    result = detector.detect(
        store_id,
        quantity,
    )

    print(
        f"Store: {store_id} | "
        f"Quantity: {quantity} | "
        f"Baseline: "
        f"{result['baseline_quantity']} | "
        f"Anomaly: "
        f"{result['is_anomaly']}"
    )


print("\nTesting normal store quantity...\n")


normal_result = detector.detect(
    store_id,
    55,
)

print(normal_result)


print("\nTesting store quantity spike...\n")


spike_result = detector.detect(
    store_id,
    120,
)

print(spike_result)


print("\nTesting store quantity drop...\n")


drop_result = detector.detect(
    store_id,
    20,
)

print(drop_result)


# Assertions

assert normal_result["is_anomaly"] is False

assert (
    normal_result["reason"]
    == "Normal store quantity"
)

assert spike_result["is_anomaly"] is True

assert (
    spike_result["reason"]
    == "Store quantity spike"
)

assert drop_result["is_anomaly"] is True

assert (
    drop_result["reason"]
    == "Store quantity drop"
)


print(
    "\nStore anomaly detector test passed!"
)