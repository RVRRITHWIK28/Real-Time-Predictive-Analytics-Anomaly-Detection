from src.processing.bucket_analytics import (
    BucketAnalyticsProcessor,
)

from src.ml.revenue_anomaly_detector import (
    RevenueAnomalyDetector,
)

from src.ml.quantity_anomaly_detector import (
    QuantityAnomalyDetector,
)

from src.processing.unified_anomaly_pipeline import (
    UnifiedAnomalyPipeline,
)


class CompletedAnomalyPipeline:

    def __init__(self):

        self.bucket_processor = (
            BucketAnalyticsProcessor()
        )

        self.revenue_detector = (
            RevenueAnomalyDetector(
                upper_threshold=2.0,
                lower_threshold=0.5,
                history_size=5,
            )
        )

        self.quantity_detector = (
            QuantityAnomalyDetector(
                upper_threshold=2.0,
                lower_threshold=0.5,
                history_size=5,
            )
        )

        self.unified_pipeline = (
            UnifiedAnomalyPipeline()
        )

    def add_transaction(self, transaction):

        return self.bucket_processor.add_transaction(
            transaction
        )

    def process_completed_buckets(
        self,
        current_time,
    ):

        # Get completed buckets
        bucket_results = (
            self.bucket_processor
            .process_completed_buckets(
                current_time
            )
        )

        results = []

        for bucket_result in bucket_results:

            bucket = bucket_result["bucket"]

            current_revenue = (
                bucket_result["revenue"]
            )

            current_quantity = (
                bucket_result["quantity"]
            )

            # ------------------------------------------
            # Revenue anomaly detection
            # ------------------------------------------

            revenue_detection = (
                self.revenue_detector.detect(
                    current_revenue
                )
            )

            if revenue_detection["is_anomaly"]:

                revenue_event = (
                    self.unified_pipeline
                    .create_event(
                        timestamp=bucket,
                        bucket=bucket,
                        anomaly_type=(
                            "revenue_spike"
                            if revenue_detection["reason"]
                            == "Revenue spike"
                            else "revenue_drop"
                        ),
                        entity_id="GLOBAL",
                        detection_result=(
                            revenue_detection
                        ),
                    )
                )

                results.append(
                    revenue_event
                )

            # ------------------------------------------
            # Quantity anomaly detection
            # ------------------------------------------

            quantity_detection = (
                self.quantity_detector.detect(
                    current_quantity
                )
            )

            if quantity_detection["is_anomaly"]:

                quantity_event = (
                    self.unified_pipeline
                    .create_event(
                        timestamp=bucket,
                        bucket=bucket,
                        anomaly_type=(
                            "quantity_spike"
                            if quantity_detection["reason"]
                            == "Quantity spike"
                            else "quantity_drop"
                        ),
                        entity_id="GLOBAL",
                        detection_result=(
                            quantity_detection
                        ),
                    )
                )

                results.append(
                    quantity_event
                )

        return results