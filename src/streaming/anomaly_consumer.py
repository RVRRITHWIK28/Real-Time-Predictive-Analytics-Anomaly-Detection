"""Backfill hourly/daily revenue outliers, then score future completed buckets."""

from __future__ import annotations

from datetime import timedelta
import os
import time

from pymongo import UpdateOne

from src.database.mongodb import (
    create_mongo_client,
    get_anomalies_collection,
    get_database,
    get_transactions_collection,
)
from src.ml.revenue_isolation_forest import (
    BUSINESS_TIMEZONE,
    MODEL_VERSION,
    build_regular_series,
    as_utc,
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
IDLE_FLUSH_SECONDS = float(os.getenv("ANOMALY_IDLE_FLUSH_SECONDS", "30"))


def _minute_bucket(timestamp):
    return as_utc(timestamp).replace(second=0, microsecond=0)


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
        print(f"Stored {inserted:,} Isolation Forest revenue alert(s).")
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
    collection.create_index(
        [
            ("model_version", 1),
            ("is_anomaly", 1),
            ("time_scale", 1),
        ],
        name="anomaly_model_scale_lookup",
    )


def backfill_from_mongodb(
    transactions_collection,
    anomalies_collection,
    pipeline,
):
    """Aggregate full transaction history into London-time hours and days."""
    total_transactions = transactions_collection.count_documents({})
    print(
        "Starting hourly/daily revenue backfill from MongoDB "
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
                "$expr": {
                    "$and": [
                        {"$isNumber": "$revenue"},
                        {"$gt": ["$revenue", 0]},
                    ]
                },
            }
        },
        {
            "$facet": {
                "hourly": [
                    {
                        "$group": {
                            "_id": {
                                "$dateTrunc": {
                                    "date": "$_anomaly_time",
                                    "unit": "hour",
                                    "timezone": "Europe/London",
                                }
                            },
                            "revenue": {"$sum": "$revenue"},
                        }
                    },
                    {"$sort": {"_id": 1}},
                ],
                "daily": [
                    {
                        "$group": {
                            "_id": {
                                "$dateTrunc": {
                                    "date": "$_anomaly_time",
                                    "unit": "day",
                                    "timezone": "Europe/London",
                                }
                            },
                            "revenue": {"$sum": "$revenue"},
                        }
                    },
                    {"$sort": {"_id": 1}},
                ],
                "range": [
                    {
                        "$group": {
                            "_id": None,
                            "first": {"$min": "$_anomaly_time"},
                            "last": {"$max": "$_anomaly_time"},
                        }
                    }
                ],
            }
        },
    ]

    cursor = transactions_collection.aggregate(
        aggregation,
        allowDiskUse=True,
        batchSize=5_000,
    )
    try:
        aggregate_result = next(cursor, {})
    finally:
        cursor.close()

    hourly_rows = build_regular_series(
        aggregate_result.get("hourly", []),
        "hourly",
    )
    daily_rows = build_regular_series(
        aggregate_result.get("daily", []),
        "daily",
    )
    events = pipeline.fit_historical(hourly_rows, daily_rows)
    inserted = _persist_events(anomalies_collection, events)

    bounds = aggregate_result.get("range", [])
    latest_event_time = (
        as_utc(bounds[0]["last"])
        if bounds and bounds[0].get("last") is not None
        else None
    )
    latest_bucket = (
        _minute_bucket(latest_event_time)
        if latest_event_time is not None
        else None
    )

    print(
        "Hourly/daily model backfill complete | "
        f"Transactions stored: {total_transactions:,} | "
        f"Hourly buckets: {len(hourly_rows):,} | "
        f"Daily buckets: {len(daily_rows):,} | "
        f"New Isolation Forest alerts: {inserted:,} | "
        f"Model: {MODEL_VERSION}"
    )
    return {
        "latest_event_time": latest_event_time,
        "latest_bucket": latest_bucket,
        "processed_transactions": total_transactions,
        "processed_buckets": len(hourly_rows) + len(daily_rows),
        "inserted_anomalies": inserted,
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
        event_time = as_utc(transaction.get("timestamp"))
        minute = _minute_bucket(event_time)
    except (TypeError, ValueError):
        print(
            "Skipping transaction with invalid timestamp: "
            f"{transaction.get('event_id', 'unknown')}"
        )
        return latest_finalized_bucket, max_event_time

    if backfill_cutoff_bucket is not None and minute <= backfill_cutoff_bucket:
        return latest_finalized_bucket, max_event_time
    if latest_finalized_bucket is not None and minute <= latest_finalized_bucket:
        return latest_finalized_bucket, max_event_time
    if "revenue" not in transaction:
        return latest_finalized_bucket, max_event_time

    try:
        transaction["revenue"] = float(transaction["revenue"])
    except (TypeError, ValueError):
        print(
            "Skipping transaction with invalid revenue: "
            f"{transaction.get('event_id', 'unknown')}"
        )
        return latest_finalized_bucket, max_event_time
    if transaction["revenue"] <= 0:
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
            "Hourly/daily Isolation Forest consumer started | "
            f"Kafka group: {ANOMALY_CONSUMER_GROUP} | "
            f"Business timezone: {BUSINESS_TIMEZONE.key} | "
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
                latest_finalized_bucket, max_event_time = _process_live_transaction(
                    transaction,
                    detector_pipeline,
                    anomalies,
                    backfill_cutoff_bucket,
                    latest_finalized_bucket,
                    max_event_time,
                )
                processed_live += 1
                last_message_at = time.monotonic()

                if processed_live % 10_000 == 0:
                    print(f"Consumed {processed_live:,} Kafka transactions.")

            if messages:
                consumer.commit()
            elif (
                max_event_time is not None
                and time.monotonic() - last_message_at >= IDLE_FLUSH_SECONDS
            ):
                # Close final open hour/day after the historical replay goes quiet.
                flush_time = max_event_time + timedelta(days=1)
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
