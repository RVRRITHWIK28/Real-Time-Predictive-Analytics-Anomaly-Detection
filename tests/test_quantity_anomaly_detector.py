from src.ml.quantity_anomaly_detector import (
    QuantityAnomalyDetector,
)


detector = QuantityAnomalyDetector(
    upper_threshold=2.0,
    lower_threshold=0.5,
    history_size=5,
)


print("Building quantity baseline...\n")


historical_quantities = [
    48,
    52,
    50,
    51,
    49,
]


for quantity in historical_quantities:

    result = detector.detect(
        quantity
    )

    print(
        f"Quantity: {quantity} | "
        f"Baseline: "
        f"{result['baseline_quantity']} | "
        f"Anomaly: "
        f"{result['is_anomaly']}"
    )


print("\nTesting normal quantity...\n")


normal_result = detector.detect(
    55
)

print(normal_result)


print("\nTesting quantity spike...\n")


spike_result = detector.detect(
    120
)

print(spike_result)


print("\nTesting quantity drop...\n")


drop_result = detector.detect(
    20
)

print(drop_result)