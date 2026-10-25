from collections import defaultdict

from src.processing.completed_bucket import (
    CompletedMinuteBucketProcessor,
)
from src.ml.revenue_anomaly_detector import RevenueAnomalyDetector
from src.ml.quantity_anomaly_detector import QuantityAnomalyDetector
from src.ml.product_anomaly_detector import ProductQuantityAnomalyDetector
from src.ml.store_anomaly_detector import StoreQuantityAnomalyDetector
from src.processing.unified_anomaly_pipeline import UnifiedAnomalyPipeline


class UnifiedCompletedAnomalyPipeline:
    """Detect anomalies from complete, chronologically ordered minute buckets."""

    def __init__(self):
        self.bucket_processor = CompletedMinuteBucketProcessor()
        self.revenue_detector = RevenueAnomalyDetector(
            upper_threshold=2.0,
            lower_threshold=0.5,
            history_size=5,
        )
        self.quantity_detector = QuantityAnomalyDetector(
            upper_threshold=2.0,
            lower_threshold=0.5,
            history_size=5,
        )
        self.product_detector = ProductQuantityAnomalyDetector(
            upper_threshold=2.0,
            lower_threshold=0.5,
            history_size=5,
        )
        self.store_detector = StoreQuantityAnomalyDetector(
            upper_threshold=2.0,
            lower_threshold=0.5,
            history_size=5,
        )
        self.unified_pipeline = UnifiedAnomalyPipeline()

    def add_transaction(self, transaction):
        return self.bucket_processor.add_transaction(transaction)

    def process_bucket(self, bucket, transactions):
        """Analyze one completed minute; also used by the MongoDB backfill."""
        if not transactions:
            return []

        results = []
        current_revenue = sum(float(row["revenue"]) for row in transactions)
        current_quantity = sum(float(row["quantity"]) for row in transactions)

        revenue_detection = self.revenue_detector.detect(current_revenue)
        if revenue_detection["is_anomaly"]:
            results.append(
                self.unified_pipeline.create_event(
                    timestamp=bucket,
                    bucket=bucket,
                    anomaly_type=(
                        "revenue_spike"
                        if revenue_detection["reason"] == "Revenue spike"
                        else "revenue_drop"
                    ),
                    entity_id="GLOBAL",
                    detection_result=revenue_detection,
                )
            )

        quantity_detection = self.quantity_detector.detect(current_quantity)
        if quantity_detection["is_anomaly"]:
            results.append(
                self.unified_pipeline.create_event(
                    timestamp=bucket,
                    bucket=bucket,
                    anomaly_type=(
                        "quantity_spike"
                        if quantity_detection["reason"] == "Quantity spike"
                        else "quantity_drop"
                    ),
                    entity_id="GLOBAL",
                    detection_result=quantity_detection,
                )
            )

        product_quantities = defaultdict(float)
        store_quantities = defaultdict(float)
        for row in transactions:
            product_quantities[str(row["product_id"])] += float(row["quantity"])
            store_quantities[str(row["store_id"])] += float(row["quantity"])

        for product_id, quantity in product_quantities.items():
            detection = self.product_detector.detect(product_id, quantity)
            if detection["is_anomaly"]:
                results.append(
                    self.unified_pipeline.create_event(
                        timestamp=bucket,
                        bucket=bucket,
                        anomaly_type=(
                            "product_quantity_spike"
                            if detection["reason"] == "Product quantity spike"
                            else "product_quantity_drop"
                        ),
                        entity_id=product_id,
                        detection_result=detection,
                    )
                )

        for store_id, quantity in store_quantities.items():
            detection = self.store_detector.detect(store_id, quantity)
            if detection["is_anomaly"]:
                results.append(
                    self.unified_pipeline.create_event(
                        timestamp=bucket,
                        bucket=bucket,
                        anomaly_type=(
                            "store_quantity_spike"
                            if detection["reason"] == "Store quantity spike"
                            else "store_quantity_drop"
                        ),
                        entity_id=store_id,
                        detection_result=detection,
                    )
                )

        return results

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

