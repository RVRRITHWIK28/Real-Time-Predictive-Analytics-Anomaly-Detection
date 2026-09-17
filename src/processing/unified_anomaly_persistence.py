from src.processing.unified_completed_anomaly_pipeline import (
    UnifiedCompletedAnomalyPipeline,
)

from src.database.anomaly_repository import (
    save_anomaly_event,
)


class UnifiedAnomalyPersistencePipeline:

    def __init__(self):

        print(
            "Creating UnifiedAnomalyPersistencePipeline"
        )

        self.pipeline = UnifiedCompletedAnomalyPipeline()

    def add_transaction(self, transaction):

        return self.pipeline.add_transaction(
            transaction
        )

    def process_completed_buckets(
        self,
        current_time,
    ):

        print(
            "\nPersistence pipeline started"
        )

        print(
            "Current time:",
            current_time
        )

        # ------------------------------------------
        # DEBUG: inspect completed buckets
        # ------------------------------------------

        completed_buckets = (
            self.pipeline
            .bucket_processor
            .get_completed_buckets(
                current_time
            )
        )

        print(
            "Completed buckets:",
            completed_buckets
        )

        for bucket in completed_buckets:

            transactions = (
                self.pipeline
                .bucket_processor
                .get_transactions(
                    bucket
                )
            )

            print(
                f"\nBucket {bucket} transactions:"
            )

            for transaction in transactions:

                print(transaction)

        # ------------------------------------------
        # Run anomaly pipeline
        # ------------------------------------------

        events = (
            self.pipeline
            .process_completed_buckets(
                current_time
            )
        )

        print(
            "\nEvents returned:",
            len(events)
        )

        # ------------------------------------------
        # DEBUG: detector state
        # ------------------------------------------

        print(
            "\nRevenue detector history:"
        )

        print(
            list(
                self.pipeline
                .revenue_detector
                .history
            )
        )

        print(
            "\nQuantity detector history:"
        )

        print(
            list(
                self.pipeline
                .quantity_detector
                .history
            )
        )

        print(
            "\nProduct detector history:"
        )

        print(
            {
                product_id: list(history)
                for product_id, history
                in self.pipeline
                .product_detector
                .product_history
                .items()
            }
        )

        print(
            "\nStore detector history:"
        )

        print(
            {
                store_id: list(history)
                for store_id, history
                in self.pipeline
                .store_detector
                .store_history
                .items()
            }
        )

        # ------------------------------------------
        # Save anomaly events
        # ------------------------------------------

        saved_events = []

        for event in events:

            print(
                "\nSaving:",
                event.anomaly_type,
                event.entity_id
            )

            inserted_id = save_anomaly_event(
                event
            )

            saved_events.append(
                {
                    "event": event,
                    "inserted_id": inserted_id,
                }
            )

            print(
                "MongoDB ID:",
                inserted_id
            )

        print(
            "\nPersistence pipeline finished"
        )

        return saved_events