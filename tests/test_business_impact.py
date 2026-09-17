from src.ml.business_impact import (
    generate_business_impact,
)


# --------------------------------------------------
# Normal activity
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="product_quantity_spike",
    severity="NORMAL",
    ratio=1.10,
)

print("Normal:")
print(result)

assert (
    result["business_impact"]
    == "No significant business impact detected."
)

assert (
    result["recommendation"]
    == "Continue normal operations."
)


# --------------------------------------------------
# Revenue spike
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="revenue_spike",
    severity="HIGH",
    ratio=2.42,
)

print("\nRevenue spike:")
print(result)

assert (
    "high revenue activity"
    in result["business_impact"]
)

assert (
    "inventory"
    in result["recommendation"]
)


# --------------------------------------------------
# Revenue drop
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="revenue_drop",
    severity="CRITICAL",
    ratio=0.23,
)

print("\nRevenue drop:")
print(result)

assert (
    "Revenue is significantly below"
    in result["business_impact"]
)

assert (
    "Investigate"
    in result["recommendation"]
)


# --------------------------------------------------
# Product quantity spike
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="product_quantity_spike",
    severity="HIGH",
    ratio=2.33,
)

print("\nProduct quantity spike:")
print(result)

assert (
    "unusually high demand"
    in result["business_impact"]
)

assert (
    "replenishment"
    in result["recommendation"]
)


# --------------------------------------------------
# Product quantity drop
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="product_quantity_drop",
    severity="CRITICAL",
    ratio=0.31,
)

print("\nProduct quantity drop:")
print(result)

assert (
    "below"
    in result["business_impact"]
)

assert (
    "pricing"
    in result["recommendation"]
)


# --------------------------------------------------
# Store quantity spike
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="store_quantity_spike",
    severity="HIGH",
    ratio=2.33,
)

print("\nStore quantity spike:")
print(result)

assert (
    "Store activity"
    in result["business_impact"]
)

assert (
    "operational capacity"
    in result["recommendation"]
)


# --------------------------------------------------
# Store quantity drop
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="store_quantity_drop",
    severity="CRITICAL",
    ratio=0.27,
)

print("\nStore quantity drop:")
print(result)

assert (
    "below normal"
    in result["business_impact"]
)

assert (
    "store operations"
    in result["recommendation"]
)

# --------------------------------------------------
# Overall quantity spike
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="quantity_spike",
    severity="HIGH",
    ratio=2.42,
)

print("\nOverall quantity spike:")
print(result)

assert (
    "Overall transaction quantity"
    in result["business_impact"]
)

assert (
    "inventory"
    in result["recommendation"]
)


# --------------------------------------------------
# Overall quantity drop
# --------------------------------------------------

result = generate_business_impact(
    anomaly_type="quantity_drop",
    severity="CRITICAL",
    ratio=0.23,
)

print("\nOverall quantity drop:")
print(result)

assert (
    "Overall transaction quantity"
    in result["business_impact"]
)

assert (
    "Investigate"
    in result["recommendation"]
)


print("\nBusiness impact test passed!")