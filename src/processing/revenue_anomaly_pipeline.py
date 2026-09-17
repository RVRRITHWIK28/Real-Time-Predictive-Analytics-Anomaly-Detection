from src.processing.stream_processor import StreamAnalytics
from src.ml.revenue_anomaly_detector import RevenueAnomalyDetector
from src.ml.anomaly_severity import calculate_severity


class RevenueAnomalyPipeline:

    def __init__(self):
        self.analytics = StreamAnalytics()

        self.detector = RevenueAnomalyDetector(
            upper_threshold=2.0,
            lower_threshold=0.5,
            history_size=5,
        )

        self.processed_buckets = set()

    def process_transaction(self, transaction):

        # Step 1: Process transaction
        self.analytics.process_transaction(transaction)

        # Step 2: Get minute-level revenue
        minute_revenue = (
            self.analytics.get_minute_revenue()
        )

        if not minute_revenue:
            return None

        # Step 3: Get current minute bucket
        current_bucket = max(
            minute_revenue.keys()
        )

        # Step 4: Prevent duplicate processing
        if current_bucket in self.processed_buckets:
            return None

        # Step 5: Get current revenue
        current_revenue = minute_revenue[
            current_bucket
        ]

        # Step 6: Run revenue anomaly detector
        result = self.detector.detect(
            current_revenue
        )

        # Step 7: Calculate severity
        severity_result = calculate_severity(
            ratio=result["ratio"],
            is_anomaly=result["is_anomaly"],
        )

        # Step 8: Mark bucket as processed
        self.processed_buckets.add(
            current_bucket
        )

        # Step 9: Return combined result
        return {
            "timestamp": transaction["timestamp"],
            "bucket": current_bucket,
            **result,
            **severity_result,
        }