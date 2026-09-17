def generate_business_impact(
    anomaly_type,
    severity,
    ratio,
):
    """
    Convert an anomaly into a business impact
    and recommended action.
    """

    if not severity:
        severity = "NORMAL"

    # Normal activity
    if severity == "NORMAL":
        return {
            "business_impact": "No significant business impact detected.",
            "recommendation": "Continue normal operations.",
        }

    # Revenue anomaly
    if anomaly_type == "revenue_spike":

        return {
            "business_impact": (
                "Unusually high revenue activity detected. "
                "Demand may be significantly higher than normal."
            ),
            "recommendation": (
                "Check inventory availability and prepare "
                "for potential replenishment."
            ),
        }

    if anomaly_type == "revenue_drop":

        return {
            "business_impact": (
                "Revenue is significantly below the normal baseline. "
                "Potential demand or sales disruption may be occurring."
            ),
            "recommendation": (
                "Investigate sales channels, pricing, inventory "
                "availability, and transaction activity."
            ),
        }

    # Product quantity anomaly
    if anomaly_type == "product_quantity_spike":

        return {
            "business_impact": (
                "A product is experiencing unusually high demand."
            ),
            "recommendation": (
                "Check product inventory and consider replenishment."
            ),
        }

    if anomaly_type == "product_quantity_drop":

        return {
            "business_impact": (
                "Product demand is significantly below its "
                "normal level."
            ),
            "recommendation": (
                "Check product availability, pricing, promotions, "
                "and customer demand."
            ),
        }

    # Store quantity anomaly
    if anomaly_type == "store_quantity_spike":

        return {
            "business_impact": (
                "Store activity is significantly higher than normal."
            ),
            "recommendation": (
                "Check inventory levels and operational capacity "
                "at the store."
            ),
        }

    if anomaly_type == "store_quantity_drop":

        return {
            "business_impact": (
                "Store activity is significantly below normal."
            ),
            "recommendation": (
                "Investigate inventory, store operations, "
                "and transaction activity."
            ),
        }

    # Overall quantity anomaly
    if anomaly_type == "quantity_spike":

        return {
            "business_impact": (
                "Overall transaction quantity is "
                "significantly higher than normal."
            ),
            "recommendation": (
                "Check inventory availability and "
                "prepare for increased demand."
            ),
        }

    if anomaly_type == "quantity_drop":

        return {
            "business_impact": (
                "Overall transaction quantity is "
                "significantly below normal."
            ),
            "recommendation": (
                "Investigate inventory, sales channels, "
                "and transaction activity."
            ),
        }

    # Unknown anomaly
    return {
        "business_impact": (
            "An unusual activity pattern was detected."
        ),
        "recommendation": (
            "Investigate the underlying transaction activity."
        ),
    }