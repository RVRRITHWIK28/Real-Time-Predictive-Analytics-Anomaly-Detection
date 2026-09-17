from collections import defaultdict
from datetime import datetime, timedelta


class CompletedMinuteBucketProcessor:

    def __init__(self):
        self.buckets = defaultdict(list)
        self.processed_buckets = set()

    def add_transaction(self, transaction):
        """
        Add a transaction to its minute bucket.
        """

        timestamp = transaction["timestamp"]

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )

        bucket = timestamp.replace(
            second=0,
            microsecond=0,
        )

        self.buckets[bucket].append(transaction)

        return bucket

    def get_completed_buckets(self, current_time):
        """
        Return buckets that are complete based on current time.
        """

        if isinstance(current_time, str):
            current_time = datetime.fromisoformat(
                current_time.replace("Z", "+00:00")
            )

        completed = []

        for bucket in sorted(self.buckets.keys()):

            if bucket in self.processed_buckets:
                continue

            bucket_end = bucket + timedelta(
                minutes=1
            )

            if current_time >= bucket_end:
                completed.append(bucket)

        return completed

    def get_transactions(self, bucket):
        """
        Return all transactions belonging
        to a specific minute bucket.
        """

        return self.buckets.get(bucket, [])

    def mark_processed(self, bucket):
        """
        Mark a bucket as processed.
        """

        self.processed_buckets.add(bucket)