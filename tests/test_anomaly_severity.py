from src.ml.anomaly_severity import calculate_severity


# Normal
result = calculate_severity(
    ratio=1.10,
    is_anomaly=False,
)

print("Normal:")
print(result)

assert result["severity"] == "NORMAL"


# Medium anomaly
result = calculate_severity(
    ratio=1.60,
    is_anomaly=True,
)

print("\nMedium:")
print(result)

assert result["severity"] == "MEDIUM"


# High spike
result = calculate_severity(
    ratio=2.50,
    is_anomaly=True,
)

print("\nHigh spike:")
print(result)

assert result["severity"] == "HIGH"


# Critical spike
result = calculate_severity(
    ratio=3.50,
    is_anomaly=True,
)

print("\nCritical spike:")
print(result)

assert result["severity"] == "CRITICAL"


# High drop
result = calculate_severity(
    ratio=0.40,
    is_anomaly=True,
)

print("\nHigh drop:")
print(result)

assert result["severity"] == "HIGH"


# Critical drop
result = calculate_severity(
    ratio=0.20,
    is_anomaly=True,
)

print("\nCritical drop:")
print(result)

assert result["severity"] == "CRITICAL"


print("\nAnomaly severity test passed!")