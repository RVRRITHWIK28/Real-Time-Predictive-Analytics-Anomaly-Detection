from src.ml.anomaly_event import AnomalyEvent
from src.ml.anomaly_severity import calculate_severity
from src.ml.business_impact import generate_business_impact


class UnifiedAnomalyPipeline:

    def create_event(
        self,
        timestamp,
        bucket,
        anomaly_type,
        entity_id,
        detection_result,
    ):
        # Step 1: Extract detection information
        is_anomaly = detection_result["is_anomaly"]
        reason = detection_result["reason"]
        ratio = detection_result["ratio"]

        # Step 2: Determine current and baseline values
        if "current_revenue" in detection_result:
            current_value = detection_result[
                "current_revenue"
            ]
            baseline_value = detection_result[
                "baseline_revenue"
            ]

        elif "current_quantity" in detection_result:
            current_value = detection_result[
                "current_quantity"
            ]
            baseline_value = detection_result[
                "baseline_quantity"
            ]

        else:
            raise ValueError(
                "Detection result must contain "
                "revenue or quantity values."
            )

        # Step 3: Calculate severity
        severity_result = calculate_severity(
            ratio=ratio,
            is_anomaly=is_anomaly,
        )

        # Step 4: Generate business impact
        business_result = generate_business_impact(
            anomaly_type=anomaly_type,
            severity=severity_result["severity"],
            ratio=ratio,
        )

        # Step 5: Create unified anomaly event
        event = AnomalyEvent(
            timestamp=timestamp,
            bucket=bucket,
            anomaly_type=anomaly_type,
            entity_id=entity_id,
            is_anomaly=is_anomaly,
            reason=reason,
            ratio=ratio,
            current_value=current_value,
            baseline_value=baseline_value,
            severity=severity_result["severity"],
            message=severity_result["message"],
            business_impact=business_result[
                "business_impact"
            ],
            recommendation=business_result[
                "recommendation"
            ],
        )

        return event