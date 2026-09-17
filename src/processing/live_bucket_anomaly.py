from collections import defaultdict

from src.streaming.consumer import (
    create_consumer,
    consume_transactions,
)

from src.processing.time_bucket import (
    get_minute_bucket,
)

from src.ml.bucket_anomaly_detector import (
    BucketVolumeDetector,
)

from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_anomalies_collection,
    insert_anomaly,
)


def run_live_bucket_anomaly():

    consumer = create_consumer()

    mongo_client = create_mongo_client()

    database = get_database(
        mongo_client
    )

    anomalies_collection = (
        get_anomalies_collection(database)
    )

    detector = BucketVolumeDetector(
        threshold=2.0,
        history_size=5,
    )

    buckets = defaultdict(int)

    processed_buckets = set()

    latest_bucket = None

    print(
        "Live bucket anomaly detection started."
    )

    print(
        "Kafka → Event Time Buckets → "
        "Detector → MongoDB"
    )

    print(
        "Waiting for transactions...\n"
    )

    try:

        for transaction in consume_transactions(
            consumer
        ):

            timestamp = transaction["timestamp"]

            bucket = get_minute_bucket(
                timestamp
            )

            # Ignore buckets that were already
            # completely processed.
            if bucket in processed_buckets:
                continue

            # Store transaction in its
            # event-time bucket.
            buckets[bucket] += 1

            # Keep track of the newest
            # event-time bucket seen.
            if (
                latest_bucket is None
                or bucket > latest_bucket
            ):
                latest_bucket = bucket

            # We need one newer bucket before
            # considering the previous bucket
            # complete.
            completed_candidates = [
                existing_bucket
                for existing_bucket in buckets
                if (
                    existing_bucket < latest_bucket
                    and existing_bucket
                    not in processed_buckets
                )
            ]

            # Process candidates in chronological order.
            for completed_bucket in sorted(
                completed_candidates
            ):

                current_count = buckets[
                    completed_bucket
                ]

                result = detector.detect(
                    current_count
                )

                print(
                    "\nCompleted bucket:"
                )

                print(
                    f"Bucket       : "
                    f"{completed_bucket}"
                )

                print(
                    f"Transactions : "
                    f"{current_count}"
                )

                print(
                    f"Baseline     : "
                    f"{result['baseline_count']}"
                )

                print(
                    f"Ratio        : "
                    f"{result['ratio']}"
                )

                print(
                    f"Anomaly      : "
                    f"{result['is_anomaly']}"
                )

                print(
                    f"Reason       : "
                    f"{result['reason']}"
                )

                # Store anomaly in MongoDB.
                if result["is_anomaly"]:

                    anomaly = {
                        "bucket": (
                            completed_bucket
                            .isoformat()
                        ),

                        "anomaly_type": (
                            "transaction_volume_spike"
                        ),

                        "current_count": (
                            result[
                                "current_count"
                            ]
                        ),

                        "baseline_count": (
                            result[
                                "baseline_count"
                            ]
                        ),

                        "ratio": result["ratio"],

                        "is_anomaly": True,
                    }

                    document_id = (
                        insert_anomaly(
                            anomalies_collection,
                            anomaly,
                        )
                    )

                    print(
                        "🚨 Anomaly stored "
                        "in MongoDB!"
                    )

                    print(
                        f"Document ID: "
                        f"{document_id}"
                    )

                processed_buckets.add(
                    completed_bucket
                )

                del buckets[
                    completed_bucket
                ]

    except KeyboardInterrupt:

        print(
            "\nLive bucket anomaly "
            "detection stopped."
        )

    finally:

        consumer.close()

        mongo_client.close()


if __name__ == "__main__":
    run_live_bucket_anomaly()