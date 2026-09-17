from src.processing.time_bucket import (
    get_minute_bucket,
    MinuteBucketCounter,
)


print("Testing minute bucket conversion...")

timestamp_1 = "2026-09-16T10:00:15+00:00"
timestamp_2 = "2026-09-16T10:00:42+00:00"
timestamp_3 = "2026-09-16T10:01:05+00:00"


bucket_1 = get_minute_bucket(timestamp_1)
bucket_2 = get_minute_bucket(timestamp_2)
bucket_3 = get_minute_bucket(timestamp_3)


print(
    f"{timestamp_1} → {bucket_1}"
)

print(
    f"{timestamp_2} → {bucket_2}"
)

print(
    f"{timestamp_3} → {bucket_3}"
)


print("\nTesting transaction counting...")

counter = MinuteBucketCounter()


counter.add_transaction(timestamp_1)
counter.add_transaction(timestamp_2)
counter.add_transaction(timestamp_3)


all_buckets = counter.get_all_buckets()


for bucket, count in all_buckets.items():

    print(
        f"Bucket: {bucket} | "
        f"Transactions: {count}"
    )


print("\nTime bucket test completed!")