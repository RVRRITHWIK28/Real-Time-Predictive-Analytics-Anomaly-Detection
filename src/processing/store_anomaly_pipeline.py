from src.processing.stream_processor import StreamAnalytics
from src.ml.store_anomaly_detector import StoreQuantityAnomalyDetector
from src.ml.anomaly_severity import calculate_severity


class StoreAnomalyPipeline:

    def __init__(self):
        self.analytics = StreamAnalytics()

        self.detector = StoreQuantityAnomalyDetector(
            upper_threshold=2.0,
            lower_threshold=0.5,
            history_size=5,
        )

        self.processed_buckets = {}

    def process_transaction(self, transaction):

        # Step 1: Process transaction
        self.analytics.process_transaction(transaction)

        # Step 2: Identify store
        store_id = transaction["store_id"]
        timestamp = transaction["timestamp"]

        # Step 3: Get store-level minute quantity
        store_data = self.analytics.get_store_minute_quantity()

        store_buckets = store_data.get(store_id, {})

        if not store_buckets:
            return None

        # Step 4: Get current minute bucket
        current_bucket = max(store_buckets.keys())

        # Step 5: Prevent duplicate processing
        if store_id not in self.processed_buckets:
            self.processed_buckets[store_id] = set()

        if current_bucket in self.processed_buckets[store_id]:
            return None

        # Step 6: Get current quantity
        current_quantity = store_buckets[current_bucket]

        # Step 7: Run store anomaly detector
        result = self.detector.detect(
            store_id,
            current_quantity,
        )

        # Step 8: Calculate severity
        severity_result = calculate_severity(
            ratio=result["ratio"],
            is_anomaly=result["is_anomaly"],
        )

        # Step 9: Mark bucket as processed
        self.processed_buckets[store_id].add(
            current_bucket
        )

        # Step 10: Return combined result
        return {
            "timestamp": timestamp,
            "bucket": current_bucket,
            **result,
            **severity_result,
        }