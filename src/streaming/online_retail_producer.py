"""Replay positive sale lines from Online Retail II to Kafka."""

from __future__ import annotations

import argparse
from itertools import islice
import time
from pathlib import Path

from src.ingestion.online_retail_ii import (
    DEFAULT_ARCHIVE,
    iter_online_retail_sales,
    new_source_stats,
)
from src.ingestion.schemas import TransactionEvent
from src.streaming.kafka_config import TRANSACTION_TOPIC
from src.streaming.producer import create_producer


def run_producer(
    archive_path: str | Path = DEFAULT_ARCHIVE,
    limit: int | None = None,
    delay_seconds: float = 0.0,
    flush_every: int = 1000,
    log_every: int = 10000,
) -> dict[str, int]:
    if delay_seconds < 0:
        raise ValueError("delay_seconds cannot be negative")
    if flush_every < 1 or log_every < 1:
        raise ValueError("flush_every and log_every must be positive")
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive when provided")

    stats = new_source_stats()
    producer = create_producer()
    sent = 0
    try:
        events = iter_online_retail_sales(archive_path, stats)
        if limit is not None:
            events = islice(events, limit)
        for event in events:
            validated = TransactionEvent(**event)
            payload = validated.model_dump(mode="json")
            producer.send(TRANSACTION_TOPIC, value=payload)
            sent += 1

            if sent % flush_every == 0:
                producer.flush()
            if sent % log_every == 0:
                print(f"Sent {sent:,} Online Retail II sale lines to Kafka")
            if delay_seconds:
                time.sleep(delay_seconds)
    except KeyboardInterrupt:
        print("Historical replay stopped by user.")
    finally:
        producer.flush()
        producer.close()

    print(f"Kafka topic: {TRANSACTION_TOPIC}")
    print(f"Sale events sent: {sent:,}")
    print(f"Source rows read: {stats['source_rows']:,}")
    print(f"Cancellation rows skipped: {stats['cancellations_skipped']:,}")
    print(
        "Return/adjustment rows skipped: "
        f"{stats['returns_or_adjustments_skipped']:,}"
    )
    print(
        "Rows with nonpositive prices skipped: "
        f"{stats['nonpositive_prices_skipped']:,}"
    )
    print(f"Invalid rows skipped: {stats['invalid_rows_skipped']:,}")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replay Online Retail II sale lines into the transactions Kafka topic."
    )
    parser.add_argument(
        "--archive",
        default=str(DEFAULT_ARCHIVE),
        help="Path to the supplied online+retail+ii.zip archive.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional maximum number of sale lines to send (useful for a small first run).",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=0.0,
        help="Optional pause between events for a slower demonstration replay.",
    )
    parser.add_argument("--flush-every", type=int, default=1000)
    parser.add_argument("--log-every", type=int, default=10000)
    args = parser.parse_args()
    run_producer(
        archive_path=args.archive,
        limit=args.limit,
        delay_seconds=args.delay_seconds,
        flush_every=args.flush_every,
        log_every=args.log_every,
    )


if __name__ == "__main__":
    main()
