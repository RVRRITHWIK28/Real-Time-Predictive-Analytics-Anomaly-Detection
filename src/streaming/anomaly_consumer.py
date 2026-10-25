"""Backfill anomaly history from MongoDB, then detect future Kafka events."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import time

from pymongo import UpdateOne

from src.database.mongodb import (
    create_mongo_client,
    get_anomalies_collection,
    get_database,
    get_transactions_collection,
)
from src.processing.unified_completed_anomaly_pipeline import (
    UnifiedCompletedAnomalyPipeline,
)
from src.streaming.consumer import create_consumer


ANOMALY_CONSUMER_GROUP = os.getenv(
    "ANOMALY_CONSUMER_GROUP",
    "online-retail-anomaly-detection",
)
EVENT_TIME_LATENESS = timedelta(
    seconds=int(os.getenv("ANOMALY_EVENT_TIME_LATENESS_SECONDS", "120"))
)
IDLE_FLUSH_SECONDS = float(
    os.getenv("ANOMALY_IDLE_FLUSH_SECONDS", "30")
)
BACKFILL_LOG_EVERY = 50_000


def _as_utc(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime):
        raise ValueError(f"Unsupported transaction timestamp: {value!r}")
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _minute_bucket(timestamp):
    return timestamp.replace(second=0, microsecond=0)


def _persist_events(collection, events):
    if not events:
        return 0

    updates = []
    for event in events:
        document = event.model_dump(mode="json")
        key = {
            "timestamp": document["timestamp"],
            "bucket": document["bucket"],
            "anomaly_type": document["anomaly_type"],
            "entity_id": document["entity_id"],
        }
        updates.append(
            UpdateOne(
                key,
                {"$setOnInsert": document},
                upsert=True,
            )
        )

    result = collection.bulk_write(updates, ordered=False)
    return result.upserted_count


def _persist_and_report(collection, events):
    inserted = _persist_events(collection, events)
    if inserted:
        print(f"Stored {inserted:,} anomaly alert(s) in MongoDB.")
    return inserted


def _ensure_anomaly_index(collection):
    collection.create_index(
        [
            ("timestamp", 1),
            ("bucket", 1),
            ("anomaly_type", 1),
            ("entity_id", 1),
        ],
        unique=True,
        name="unique_anomaly_event",
    )


def backfill_from_mongodb(
    transactions_collection,
    anomalies_collection,
    pipeline,
):
    """Replay MongoDB transactions in event-time order to seed and persist alerts."""
    total_transactions = transactions_collection.count_documents({})
    print(
        "Starting historical anomaly backfill from MongoDB "
        f"({total_transactions:,} stored transactions)."
    )

    aggregation = [
        {
            "$addFields": {
                "_anomaly_time": {
                    "$convert": {
                        "input": "$timestamp",
                        "to": "date",
                        "onError": None,
                        "onNull": None,
                    }
                }
            }
        },
        {
            "$match": {
                "_anomaly_time": {"$ne": None},
                "product_id": {"$exists": True, "$ne": None},
                "store_id": {"$exists": True, "$ne": None},
                "$expr": {
                    "$and": [
                        {"$isNumber": "$quantity"},
                        {"$gt": ["$quantity", 0]},
                        {"$isNumber": "$revenue"},
                        {"$gt": ["$revenue", 0]},
                    ]
                },
            }
        },
        {"$sort": {"_anomaly_time": 1, "event_id": 1}},
        {
            "$project": {
                "_id": 0,
                "event_id": 1,
                "timestamp": "$_anomaly_time",
                "product_id": 1,
                "store_id": 1,
                "quantity": 1,
                "revenue": 1,
            }
        },
    ]

    cursor = transactions_collection.aggregate(
        aggregation,
        allowDiskUse=True,
        batchSize=5_000,
    )

    processed_transactions = 0
    processed_buckets = 0
    inserted_anomalies = 0
    current_bucket = None
    bucket_transactions = []
    latest_event_time = None

    def flush_bucket():
        nonlocal processed_buckets, inserted_anomalies
        if current_bucket is None:
            return
        events = pipeline.process_bucket(
            current_bucket,
            bucket_transactions,
        )
        inserted_anomalies += _persist_events(anomalies_collection, events)
        processed_buckets += 1

    try:
        for row in cursor:
            event_time = _as_utc(row["timestamp"])
            bucket = _minute_bucket(event_time)
            row["timestamp"] = event_time

            if current_bucket is not None and bucket != current_bucket:
                flush_bucket()
                bucket_transactions = []

            current_bucket = bucket
            bucket_transactions.append(row)
            latest_event_time = event_time
            processed_transactions += 1

            if processed_transactions % BACKFILL_LOG_EVERY == 0:
                print(
                    f"Backfilled {processed_transactions:,} transactions "
                    f"across {processed_buckets:,} completed minutes."
                )

        flush_bucket()
    finally:
        cursor.close()

    latest_bucket = (
        _minute_bucket(latest_event_time)
        if latest_event_time is not None
        else None
    )
    print(
        "Historical backfill complete | "
        f"Transactions analyzed: {processed_transactions:,} | "
        f"Minute buckets: {processed_buckets:,} | "
        f"New alerts stored: {inserted_anomalies:,}"
    )
    return {
        "latest_event_time": latest_event_time,
        "latest_bucket": latest_bucket,
        "processed_transactions": processed_transactions,
        "processed_buckets": processed_buckets,
        "inserted_anomalies": inserted_anomalies,
    }


def _latest_processed_bucket(pipeline, previous):
    processed = pipeline.bucket_processor.processed_buckets
    if not processed:
        return previous
    latest = max(processed)
    if previous is None or latest > previous:
        return latest
    return previous


def _process_live_transaction(
    transaction,
    pipeline,
    anomalies_collection,
    backfill_cutoff_bucket,
    latest_finalized_bucket,
    max_event_time,
):
    try:
        event_time = _as_utc(transaction.get("timestamp"))
        bucket = _minute_bucket(event_time)
    except (TypeError, ValueError):
        print(
            "Skipping transaction with invalid timestamp: "
            f"{transaction.get('event_id', 'unknown')}"
        )
        return latest_finalized_bucket, max_event_time

    # The MongoDB backfill already analyzed every bucket through this point.
    # Ignore Kafka's historical replay of those same records.
    if backfill_cutoff_bucket is not None and bucket <= backfill_cutoff_bucket:
        return latest_finalized_bucket, max_event_time

    # Ignore records arriving after their event-time bucket has been finalized.
    if latest_finalized_bucket is not None and bucket <= latest_finalized_bucket:
        return latest_finalized_bucket, max_event_time

    required_fields = ("product_id", "store_id", "quantity", "revenue")
    if any(field not in transaction for field in required_fields):
        print(
            "Skipping incomplete transaction: "
            f"{transaction.get('event_id', 'unknown')}"
        )
        return latest_finalized_bucket, max_event_time

    try:
        transaction["quantity"] = float(transaction["quantity"])
        transaction["revenue"] = float(transaction["revenue"])
    except (TypeError, ValueError):
        print(
            "Skipping transaction with invalid numeric values: "
            f"{transaction.get('event_id', 'unknown')}"
        )
        return latest_finalized_bucket, max_event_time

    if transaction["quantity"] <= 0 or transaction["revenue"] <= 0:
        return latest_finalized_bucket, max_event_time

    transaction["timestamp"] = event_time
    pipeline.add_transaction(transaction)

    if max_event_time is None or event_time > max_event_time:
        max_event_time = event_time

    watermark = max_event_time - EVENT_TIME_LATENESS
    events = pipeline.process_completed_buckets(watermark)
    _persist_and_report(anomalies_collection, events)

    latest_finalized_bucket = _latest_processed_bucket(
        pipeline,
        latest_finalized_bucket,
    )
    return latest_finalized_bucket, max_event_time


def run_anomaly_consumer():
    mongo_client = create_mongo_client()
    consumer = None

    try:
        database = get_database(mongo_client)
        transactions = get_transactions_collection(database)
        anomalies = get_anomalies_collection(database)
        _ensure_anomaly_index(anomalies)

        # Subscribe first so Kafka retains any events arriving during backfill.
        consumer = create_consumer(
            group_id=ANOMALY_CONSUMER_GROUP,
            auto_offset_reset="latest",
            enable_auto_commit=False,
            max_poll_interval_ms=3_600_000,
        )
        pending = consumer.poll(timeout_ms=1_000)
        pending_messages = [
            message
            for partition_messages in pending.values()
            for message in partition_messages
        ]

        detector_pipeline = UnifiedCompletedAnomalyPipeline()
        backfill = backfill_from_mongodb(
            transactions,
            anomalies,
            detector_pipeline,
        )
        backfill_cutoff_bucket = backfill["latest_bucket"]
        latest_finalized_bucket = backfill_cutoff_bucket
        max_event_time = backfill["latest_event_time"]

        print(
            "Anomaly consumer started | "
            f"Kafka group: {ANOMALY_CONSUMER_GROUP} | "
            f"Backfilled through: {backfill_cutoff_bucket or 'no data'}"
        )

        processed_live = 0
        last_message_at = time.monotonic()

        while True:
            polled = consumer.poll(timeout_ms=1_000)
            messages = pending_messages
            pending_messages = []
            messages.extend(
                message
                for partition_messages in polled.values()
                for message in partition_messages
            )

            for message in messages:
                transaction = message.value
                latest_finalized_bucket, max_event_time = (
                    _process_live_transaction(
                        transaction,
                        detector_pipeline,
                        anomalies,
                        backfill_cutoff_bucket,
                        latest_finalized_bucket,
                        max_event_time,
                    )
                )
                processed_live += 1
                last_message_at = time.monotonic()

                if processed_live % 10_000 == 0:
                    print(
                        f"Consumed {processed_live:,} Kafka transactions."
                    )

            if messages:
                consumer.commit()
            elif (
                max_event_time is not None
                and time.monotonic() - last_message_at >= IDLE_FLUSH_SECONDS
            ):
                # Close the final non-empty minute after a quiet period.
                flush_time = max_event_time + timedelta(minutes=1)
                events = detector_pipeline.process_completed_buckets(flush_time)
                _persist_and_report(anomalies, events)
                latest_finalized_bucket = _latest_processed_bucket(
                    detector_pipeline,
                    latest_finalized_bucket,
                )
                last_message_at = time.monotonic()

    except KeyboardInterrupt:
        print("Anomaly consumer stopped.")
    finally:
        if consumer is not None:
            consumer.close()
        mongo_client.close()

if __name__ == "__main__":
    run_anomaly_consumer()

