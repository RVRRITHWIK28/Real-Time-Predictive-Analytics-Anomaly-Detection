from collections import defaultdict

from src.processing.completed_bucket import (
    CompletedMinuteBucketProcessor,
)

from src.ml.product_anomaly_detector import (
    ProductQuantityAnomalyDetector,
)

from src.ml.store_anomaly_detector import (
    StoreQuantityAnomalyDetector,
)

from src.processing.unified_anomaly_pipeline import (
    UnifiedAnomalyPipeline,
)


class CompletedProductStoreAnomalyPipeline:

    def __init__(self):

        self.bucket_processor = (
            CompletedMinuteBucketProcessor()
        )

        self.product_detector = (
            ProductQuantityAnomalyDetector(
                upper_threshold=2.0,
                lower_threshold=0.5,
                history_size=5,
            )
        )

        self.store_detector = (
            StoreQuantityAnomalyDetector(
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

    def process_completed_buckets(self, current_time):

        completed_buckets = (
            self.bucket_processor
            .get_completed_buckets(current_time)
        )

        results = []

        for bucket in completed_buckets:

            transactions = (
                self.bucket_processor
                .get_transactions(bucket)
            )

            # ------------------------------------------
            # Product quantities
            # ------------------------------------------

            product_quantities = defaultdict(int)

            for transaction in transactions:

                product_id = transaction["product_id"]

                product_quantities[product_id] += (
                    transaction["quantity"]
                )

            # ------------------------------------------
            # Store quantities
            # ------------------------------------------

            store_quantities = defaultdict(int)

            for transaction in transactions:

                store_id = transaction["store_id"]

                store_quantities[store_id] += (
                    transaction["quantity"]
                )

            # ------------------------------------------
            # Product anomaly detection
            # ------------------------------------------

            for product_id, quantity in (
                product_quantities.items()
            ):

                detection = (
                    self.product_detector.detect(
                        product_id,
                        quantity,
                    )
                )

                if detection["is_anomaly"]:

                    anomaly_type = (
                        "product_quantity_spike"
                        if detection["reason"]
                        == "Product quantity spike"
                        else "product_quantity_drop"
                    )

                    event = (
                        self.unified_pipeline
                        .create_event(
                            timestamp=bucket,
                            bucket=bucket,
                            anomaly_type=anomaly_type,
                            entity_id=product_id,
                            detection_result=detection,
                        )
                    )

                    results.append(event)

            # ------------------------------------------
            # Store anomaly detection
            # ------------------------------------------

            for store_id, quantity in (
                store_quantities.items()
            ):

                detection = (
                    self.store_detector.detect(
                        store_id,
                        quantity,
                    )
                )

                if detection["is_anomaly"]:

                    anomaly_type = (
                        "store_quantity_spike"
                        if detection["reason"]
                        == "Store quantity spike"
                        else "store_quantity_drop"
                    )

                    event = (
                        self.unified_pipeline
                        .create_event(
                            timestamp=bucket,
                            bucket=bucket,
                            anomaly_type=anomaly_type,
                            entity_id=store_id,
                            detection_result=detection,
                        )
                    )

                    results.append(event)

            self.bucket_processor.mark_processed(
                bucket
            )

        return results