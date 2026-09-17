def calculate_severity(ratio, is_anomaly):
    """
    Calculate the severity of an anomaly
    based on its deviation ratio.
    """

    if not is_anomaly:
        return {
            "severity": "NORMAL",
            "message": "Activity is within the expected range.",
        }

    if ratio >= 3.0 or ratio <= 0.33:
        severity = "CRITICAL"

    elif ratio >= 2.0 or ratio <= 0.5:
        severity = "HIGH"

    else:
        severity = "MEDIUM"

    if severity == "CRITICAL":
        message = "Extreme deviation from the normal baseline."

    elif severity == "HIGH":
        message = "Significant deviation from the normal baseline."

    else:
        message = "Moderate deviation from the normal baseline."

    return {
        "severity": severity,
        "message": message,
    }