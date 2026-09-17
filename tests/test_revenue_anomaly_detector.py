from src.ml.revenue_anomaly_detector import (
    RevenueAnomalyDetector,
)


detector = RevenueAnomalyDetector(
    upper_threshold=2.0,
    lower_threshold=0.5,
    history_size=5,
)


print("Building revenue baseline...\n")


historical_revenues = [
    100000,
    105000,
    98000,
    102000,
    101000,
]


for revenue in historical_revenues:

    result = detector.detect(
        revenue
    )

    print(
        f"Revenue: Rs.{revenue} | "
        f"Baseline: "
        f"Rs.{result['baseline_revenue']} | "
        f"Anomaly: "
        f"{result['is_anomaly']}"
    )


print("\nTesting normal revenue...\n")


normal_result = detector.detect(
    110000
)

print(normal_result)


print("\nTesting revenue spike...\n")


spike_result = detector.detect(
    250000
)

print(spike_result)


print("\nTesting revenue drop...\n")


drop_result = detector.detect(
    30000
)

print(drop_result)