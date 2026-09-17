from src.processing.completed_bucket import (
    CompletedMinuteBucketProcessor,
)

from src.processing.stream_processor import (
    StreamAnalytics,
)


class BucketAnalyticsProcessor:

    def __init__(self):

        self.bucket_processor = (
            CompletedMinuteBucketProcessor()
        )

        self.analytics = StreamAnalytics()

    def add_transaction(self, transaction):

        return self.bucket_processor.add_transaction(
            transaction
        )

    def process_completed_buckets(
        self,
        current_time,
    ):
        """
        Process all completed minute buckets.
        """

        completed_buckets = (
            self.bucket_processor.get_completed_buckets(
                current_time
            )
        )

        results = []

        for bucket in completed_buckets:

            transactions = (
                self.bucket_processor.get_transactions(
                    bucket
                )
            )

            # Send every transaction to analytics
            for transaction in transactions:

                self.analytics.process_transaction(
                    transaction
                )

            # Calculate bucket-level metrics
            total_quantity = sum(
                transaction["quantity"]
                for transaction in transactions
            )

            total_revenue = sum(
                transaction["revenue"]
                for transaction in transactions
            )

            results.append(
                {
                    "bucket": bucket,
                    "transactions": len(
                        transactions
                    ),
                    "quantity": total_quantity,
                    "revenue": round(
                        total_revenue,
                        2,
                    ),
                }
            )

            # Prevent duplicate processing
            self.bucket_processor.mark_processed(
                bucket
            )

        return results