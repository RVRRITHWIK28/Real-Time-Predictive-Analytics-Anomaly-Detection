from datetime import datetime, timedelta

from src.processing.completed_bucket import (
    CompletedMinuteBucketProcessor,
)

from src.processing.daily_demand_tracker import (
    DailyDemandTracker,
)


class CompletedBucketDemandPipeline:

    def __init__(self):
        self.bucket_processor = CompletedMinuteBucketProcessor()
        self.demand_tracker = DailyDemandTracker()

    def add_transaction(self, transaction):
        """
        Add a transaction to its minute bucket.
        """

        return self.bucket_processor.add_transaction(
            transaction
        )

    def process_completed_buckets(self, current_time):
        """
        Process all completed minute buckets and
        update daily product-store demand.
        """

        completed_buckets = (
            self.bucket_processor.get_completed_buckets(
                current_time
            )
        )

        processed = []

        for bucket in completed_buckets:

            transactions = (
                self.bucket_processor.get_transactions(
                    bucket
                )
            )

            # Add completed transactions to daily demand
            self.demand_tracker.add_transactions(
                transactions
            )

            processed.append({
                "bucket": bucket,
                "transaction_count": len(transactions),
                "transactions": transactions,
            })

            # Mark bucket as processed
            self.bucket_processor.mark_processed(
                bucket
            )

        return processed

    def get_daily_demand(
        self,
        date,
        product_id,
        store_id
    ):
        """
        Get accumulated daily demand.
        """

        return self.demand_tracker.get_daily_demand(
            date=date,
            product_id=product_id,
            store_id=store_id
        )


if __name__ == "__main__":

    pipeline = CompletedBucketDemandPipeline()

    # Transactions belonging to two different minutes
    transactions = [
        {
            "event_id": "evt_001",
            "timestamp": "2026-10-01T10:01:15+00:00",
            "product_id": "P1001",
            "store_id": "S001",
            "quantity": 3,
        },
        {
            "event_id": "evt_002",
            "timestamp": "2026-10-01T10:01:40+00:00",
            "product_id": "P1001",
            "store_id": "S001",
            "quantity": 5,
        },
        {
            "event_id": "evt_003",
            "timestamp": "2026-10-01T10:02:20+00:00",
            "product_id": "P1001",
            "store_id": "S001",
            "quantity": 2,
        },
    ]

    for transaction in transactions:
        pipeline.add_transaction(transaction)

    # 10:01 bucket is complete at 10:02
    current_time = datetime.fromisoformat(
        "2026-10-01T10:02:30+00:00"
    )

    results = pipeline.process_completed_buckets(
        current_time
    )

    print("=" * 60)
    print("COMPLETED BUCKET → DAILY DEMAND TEST")
    print("=" * 60)

    print("\nCompleted buckets:")

    for result in results:
        print(
            f"Bucket: {result['bucket']} | "
            f"Transactions: {result['transaction_count']}"
        )

    demand = pipeline.get_daily_demand(
        date="2026-10-01",
        product_id="P1001",
        store_id="S001"
    )

    print("\nDaily demand after processing:")
    print(
        f"P1001 + S001 = {demand} units"
    )

    print("=" * 60)
    print("COMPLETED BUCKET → DAILY DEMAND TEST COMPLETE")
    print("=" * 60)