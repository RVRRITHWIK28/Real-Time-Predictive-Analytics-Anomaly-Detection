from src.ml.bucket_anomaly_detector import (
    BucketVolumeDetector,
)


detector = BucketVolumeDetector(
    threshold=2.0,
    history_size=5,
)


print("Building baseline...\n")


historical_counts = [
    50,
    48,
    52,
    51,
    49,
]


for count in historical_counts:

    result = detector.detect(count)

    print(
        f"Observed: {count} | "
        f"Baseline: {result['baseline_count']} | "
        f"Anomaly: {result['is_anomaly']}"
    )


print("\nTesting normal bucket...\n")


normal_result = detector.detect(55)

print(normal_result)


print("\nTesting anomalous bucket...\n")


anomaly_result = detector.detect(120)

print(anomaly_result)