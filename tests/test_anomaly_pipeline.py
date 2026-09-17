from src.processing.time_bucket import (
    get_minute_bucket,
)

from src.ml.bucket_anomaly_detector import (
    BucketVolumeDetector,
)


print("=" * 60)
print("ANOMALY PIPELINE INTEGRATION TEST")
print("=" * 60)


# Simulated completed minute buckets.
bucket_counts = [
    50,
    48,
    52,
    51,
    49,
]


detector = BucketVolumeDetector(
    threshold=2.0,
    history_size=5,
)


print("\nBuilding historical baseline...\n")


for count in bucket_counts:

    result = detector.detect(count)

    print(
        f"Bucket volume: {count} | "
        f"Baseline: {result['baseline_count']} | "
        f"Anomaly: {result['is_anomaly']}"
    )


print("\nTesting normal bucket...\n")


normal_result = detector.detect(55)

print(
    f"Current volume : "
    f"{normal_result['current_count']}"
)

print(
    f"Baseline       : "
    f"{normal_result['baseline_count']}"
)

print(
    f"Ratio          : "
    f"{normal_result['ratio']}"
)

print(
    f"Anomaly        : "
    f"{normal_result['is_anomaly']}"
)

print(
    f"Reason         : "
    f"{normal_result['reason']}"
)


print("\nTesting anomaly bucket...\n")


anomaly_result = detector.detect(120)

print(
    f"Current volume : "
    f"{anomaly_result['current_count']}"
)

print(
    f"Baseline       : "
    f"{anomaly_result['baseline_count']}"
)

print(
    f"Ratio          : "
    f"{anomaly_result['ratio']}"
)

print(
    f"Anomaly        : "
    f"{anomaly_result['is_anomaly']}"
)

print(
    f"Reason         : "
    f"{anomaly_result['reason']}"
)


print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETED")
print("=" * 60)