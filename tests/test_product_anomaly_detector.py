from src.ml.product_anomaly_detector import (
    ProductQuantityAnomalyDetector,
)


detector = ProductQuantityAnomalyDetector(
    upper_threshold=2.0,
    lower_threshold=0.5,
    history_size=5,
)


product_id = "P1001"


print("Building product baseline...\n")


historical_quantities = [
    48,
    52,
    50,
    51,
    49,
]


for quantity in historical_quantities:

    result = detector.detect(
        product_id,
        quantity,
    )

    print(
        f"Product: {product_id} | "
        f"Quantity: {quantity} | "
        f"Baseline: "
        f"{result['baseline_quantity']} | "
        f"Anomaly: "
        f"{result['is_anomaly']}"
    )


print("\nTesting normal product quantity...\n")


normal_result = detector.detect(
    product_id,
    55,
)

print(normal_result)


print("\nTesting product quantity spike...\n")


spike_result = detector.detect(
    product_id,
    120,
)

print(spike_result)


print("\nTesting product quantity drop...\n")


drop_result = detector.detect(
    product_id,
    20,
)

print(drop_result)


# Assertions

assert normal_result["is_anomaly"] is False

assert normal_result["reason"] == (
    "Normal product quantity"
)

assert spike_result["is_anomaly"] is True

assert spike_result["reason"] == (
    "Product quantity spike"
)

assert drop_result["is_anomaly"] is True

assert drop_result["reason"] == (
    "Product quantity drop"
)


print(
    "\nProduct anomaly detector test passed!"
)