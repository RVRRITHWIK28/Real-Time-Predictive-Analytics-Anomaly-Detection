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
        time_scale=None,
        model_version=None,
        anomaly_score=None,
    ):
        is_anomaly = detection_result["is_anomaly"]
        reason = detection_result["reason"]
        ratio = detection_result["ratio"]

        if "current_revenue" in detection_result:
            current_value = detection_result["current_revenue"]
            baseline_value = detection_result["baseline_revenue"]
        elif "current_quantity" in detection_result:
            current_value = detection_result["current_quantity"]
            baseline_value = detection_result["baseline_quantity"]
        else:
            raise ValueError(
                "Detection result must contain revenue or quantity values."
            )

        severity_result = calculate_severity(
            ratio=ratio,
            is_anomaly=is_anomaly,
        )
        business_result = generate_business_impact(
            anomaly_type=anomaly_type,
            severity=severity_result["severity"],
            ratio=ratio,
        )

        return AnomalyEvent(
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
            business_impact=business_result["business_impact"],
            recommendation=business_result["recommendation"],
            time_scale=time_scale,
            model_version=model_version,
            anomaly_score=anomaly_score,
        )
