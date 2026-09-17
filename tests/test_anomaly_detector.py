from src.ml.anomaly_detector import TransactionVolumeDetector


detector = TransactionVolumeDetector(
    threshold=2.0,
)


print("Building baseline...")

for count in [10, 11, 9, 10, 12]:
    result = detector.detect(count)

    print(
        f"Observed: {count} | "
        f"Baseline: {result['baseline_count'] if result['baseline_count'] is not None else 'N/A'}"
    )


print("\nTesting normal volume:")

normal_result = detector.detect(12)

print(normal_result)


print("\nTesting anomalous volume:")

anomaly_result = detector.detect(25)

print(anomaly_result)