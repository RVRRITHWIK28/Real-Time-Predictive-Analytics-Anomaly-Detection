from src.processing.completed_bucket import CompletedMinuteBucketProcessor
from src.ml.revenue_anomaly_detector import RevenueAnomalyDetector
from src.processing.unified_anomaly_pipeline import UnifiedAnomalyPipeline


class UnifiedCompletedAnomalyPipeline:
    """Detect unusual revenue from complete, chronologically ordered minute buckets."""

    def __init__(self):
        self.bucket_processor = CompletedMinuteBucketProcessor()
        self.revenue_detector = RevenueAnomalyDetector(
            upper_threshold=2.0,
            lower_threshold=0.5,
            history_size=5,
        )
        self.unified_pipeline = UnifiedAnomalyPipeline()

    def add_transaction(self, transaction):
        return self.bucket_processor.add_transaction(transaction)

    def process_bucket(self, bucket, transactions):
        """Analyze revenue in one completed minute bucket."""
        if not transactions:
            return []

        current_revenue = sum(float(row["revenue"]) for row in transactions)
        detection = self.revenue_detector.detect(current_revenue)
        if not detection["is_anomaly"]:
            return []

        anomaly_type = (
            "revenue_spike"
            if detection["reason"] == "Revenue spike"
            else "revenue_drop"
        )
        return [
            self.unified_pipeline.create_event(
                timestamp=bucket,
                bucket=bucket,
                anomaly_type=anomaly_type,
                entity_id="GLOBAL",
                detection_result=detection,
            )
        ]

    def process_completed_buckets(self, current_time):
        completed_buckets = self.bucket_processor.get_completed_buckets(current_time)
        results = []

        for bucket in completed_buckets:
            transactions = self.bucket_processor.get_transactions(bucket)
            results.extend(self.process_bucket(bucket, transactions))
            self.bucket_processor.mark_processed(bucket)
            # Release transaction rows once the detector has consumed this bucket.
            self.bucket_processor.buckets.pop(bucket, None)

        return results
