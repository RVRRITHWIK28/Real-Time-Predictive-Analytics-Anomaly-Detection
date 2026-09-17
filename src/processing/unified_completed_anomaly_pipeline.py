from collections import defaultdict

from src.processing.completed_bucket import (
    CompletedMinuteBucketProcessor,
)

from src.ml.revenue_anomaly_detector import (
    RevenueAnomalyDetector,
)

from src.ml.quantity_anomaly_detector import (
    QuantityAnomalyDetector,
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


class UnifiedCompletedAnomalyPipeline:

    def __init__(self):

        self.bucket_processor = (
            CompletedMinuteBucketProcessor()
        )

        # Global detectors
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

        # Product detector
        self.product_detector = (
            ProductQuantityAnomalyDetector(
                upper_threshold=2.0,
                lower_threshold=0.5,
                history_size=5,
            )
        )

        # Store detector
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

    def process_completed_buckets(
        self,
        current_time,
    ):

        completed_buckets = (
            self.bucket_processor
            .get_completed_buckets(
                current_time
            )
        )

        results = []

        for bucket in completed_buckets:

            transactions = (
                self.bucket_processor
                .get_transactions(bucket)
            )

            # ==================================================
            # GLOBAL ANALYTICS
            # ==================================================

            current_revenue = sum(
                transaction["revenue"]
                for transaction in transactions
            )

            current_quantity = sum(
                transaction["quantity"]
                for transaction in transactions
            )

            # ==================================================
            # REVENUE ANOMALY
            # ==================================================

            revenue_detection = (
                self.revenue_detector.detect(
                    current_revenue
                )
            )

            if revenue_detection["is_anomaly"]:

                anomaly_type = (
                    "revenue_spike"
                    if revenue_detection["reason"]
                    == "Revenue spike"
                    else "revenue_drop"
                )

                event = (
                    self.unified_pipeline
                    .create_event(
                        timestamp=bucket,
                        bucket=bucket,
                        anomaly_type=anomaly_type,
                        entity_id="GLOBAL",
                        detection_result=(
                            revenue_detection
                        ),
                    )
                )

                results.append(event)

            # ==================================================
            # GLOBAL QUANTITY ANOMALY
            # ==================================================

            quantity_detection = (
                self.quantity_detector.detect(
                    current_quantity
                )
            )

            if quantity_detection["is_anomaly"]:

                anomaly_type = (
                    "quantity_spike"
                    if quantity_detection["reason"]
                    == "Quantity spike"
                    else "quantity_drop"
                )

                event = (
                    self.unified_pipeline
                    .create_event(
                        timestamp=bucket,
                        bucket=bucket,
                        anomaly_type=anomaly_type,
                        entity_id="GLOBAL",
                        detection_result=(
                            quantity_detection
                        ),
                    )
                )

                results.append(event)

            # ==================================================
            # PRODUCT AGGREGATION
            # ==================================================

            product_quantities = defaultdict(int)

            for transaction in transactions:

                product_id = transaction["product_id"]

                product_quantities[product_id] += (
                    transaction["quantity"]
                )

            # ==================================================
            # PRODUCT ANOMALIES
            # ==================================================

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

            # ==================================================
            # STORE AGGREGATION
            # ==================================================

            store_quantities = defaultdict(int)

            for transaction in transactions:

                store_id = transaction["store_id"]

                store_quantities[store_id] += (
                    transaction["quantity"]
                )

            # ==================================================
            # STORE ANOMALIES
            # ==================================================

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

            # Mark bucket processed
            self.bucket_processor.mark_processed(
                bucket
            )

        return results