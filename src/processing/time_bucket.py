from collections import defaultdict
from datetime import datetime


def get_minute_bucket(timestamp):
    """
    Convert a transaction timestamp
    into its corresponding minute bucket.
    """

    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

    return timestamp.replace(
        second=0,
        microsecond=0,
    )


class MinuteBucketCounter:

    def __init__(self):
        self.buckets = defaultdict(int)

    def add_transaction(self, timestamp):

        bucket = get_minute_bucket(timestamp)

        self.buckets[bucket] += 1

        return bucket

    def get_count(self, bucket):

        return self.buckets.get(
            bucket,
            0,
        )

    def get_all_buckets(self):

        return dict(self.buckets)