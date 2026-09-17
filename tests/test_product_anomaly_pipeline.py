from src.processing.product_anomaly_pipeline import (
    ProductAnomalyPipeline,
)


pipeline = ProductAnomalyPipeline()


product_id = "P1001"


def create_transaction(
    minute,
    quantity,
):

    return {
        "timestamp": (
            f"2026-09-16T10:{minute:02d}:00"
            "+00:00"
        ),
        "product_id": product_id,
        "store_id": "S001",
        "quantity": quantity,
        "revenue": float(
            quantity * 100
        ),
    }


print("Building product baseline...\n")


historical_quantities = [
    48,
    52,
    50,
    51,
    49,
]


for minute, quantity in enumerate(
    historical_quantities
):

    result = pipeline.process_transaction(
        create_transaction(
            minute,
            quantity,
        )
    )

    print(result)


print("\nTesting normal quantity...\n")


normal_result = pipeline.process_transaction(
    create_transaction(
        5,
        55,
    )
)

print(normal_result)


print("\nTesting product quantity spike...\n")


spike_result = pipeline.process_transaction(
    create_transaction(
        6,
        120,
    )
)

print(spike_result)


print("\nTesting product quantity drop...\n")


drop_result = pipeline.process_transaction(
    create_transaction(
        7,
        20,
    )
)

print(drop_result)


# Assertions

assert normal_result["is_anomaly"] is False
assert normal_result["severity"] == "NORMAL"

assert spike_result["is_anomaly"] is True
assert spike_result["reason"] == "Product quantity spike"
assert spike_result["severity"] == "HIGH"

assert drop_result["is_anomaly"] is True
assert drop_result["reason"] == "Product quantity drop"
assert drop_result["severity"] == "CRITICAL"


print("\nProduct anomaly pipeline test passed!")