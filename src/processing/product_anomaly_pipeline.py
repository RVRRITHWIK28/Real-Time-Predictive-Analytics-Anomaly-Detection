from src.processing.stream_processor import StreamAnalytics
from src.ml.product_anomaly_detector import ProductQuantityAnomalyDetector
from src.ml.anomaly_severity import calculate_severity


class ProductAnomalyPipeline:

    def __init__(self):
        self.analytics = StreamAnalytics()

        self.detector = ProductQuantityAnomalyDetector(
            upper_threshold=2.0,
            lower_threshold=0.5,
            history_size=5,
        )

        self.processed_buckets = {}

    def process_transaction(self, transaction):

        # Step 1: Process transaction
        self.analytics.process_transaction(transaction)

        # Step 2: Identify product
        product_id = transaction["product_id"]
        timestamp = transaction["timestamp"]

        # Step 3: Get product-level minute quantity
        product_data = (
            self.analytics.get_product_minute_quantity()
        )

        product_buckets = product_data.get(
            product_id,
            {},
        )

        if not product_buckets:
            return None

        # Step 4: Get current minute bucket
        current_bucket = max(
            product_buckets.keys()
        )

        # Step 5: Prevent duplicate processing
        if product_id not in self.processed_buckets:
            self.processed_buckets[product_id] = set()

        if current_bucket in self.processed_buckets[product_id]:
            return None

        # Step 6: Get current quantity
        current_quantity = product_buckets[
            current_bucket
        ]

        # Step 7: Run product anomaly detector
        result = self.detector.detect(
            product_id,
            current_quantity,
        )

        # Step 8: Calculate severity
        severity_result = calculate_severity(
            ratio=result["ratio"],
            is_anomaly=result["is_anomaly"],
        )

        # Step 9: Mark bucket as processed
        self.processed_buckets[
            product_id
        ].add(current_bucket)

        # Step 10: Return combined result
        return {
            "timestamp": timestamp,
            "bucket": current_bucket,
            **result,
            **severity_result,
        }