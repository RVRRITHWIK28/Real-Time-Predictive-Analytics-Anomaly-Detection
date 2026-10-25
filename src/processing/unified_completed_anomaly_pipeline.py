"""Hourly and daily revenue anomaly aggregation and scoring."""

from collections import defaultdict
from datetime import datetime
import os

from src.ml.revenue_isolation_forest import (
    MODEL_VERSION,
    RevenueIsolationForestDetector,
    as_utc,
    bucket_start,
    next_bucket_start,
)
from src.processing.completed_bucket import CompletedMinuteBucketProcessor
from src.processing.unified_anomaly_pipeline import UnifiedAnomalyPipeline


class UnifiedCompletedAnomalyPipeline:
    """Detect revenue anomalies at hourly and daily scales only."""

    def __init__(self, contamination: float | None = None):
        self.bucket_processor = CompletedMinuteBucketProcessor()
        contamination = (
            float(contamination)
            if contamination is not None
            else float(os.getenv("REVENUE_IF_CONTAMINATION", "0.01"))
        )
        self.detectors = {
            "hourly": RevenueIsolationForestDetector("hourly", contamination),
            "daily": RevenueIsolationForestDetector("daily", contamination),
        }
        self.pending_revenue = {
            "hourly": defaultdict(float),
            "daily": defaultdict(float),
        }
        self.unified_pipeline = UnifiedAnomalyPipeline()

    def add_transaction(self, transaction):
        return self.bucket_processor.add_transaction(transaction)

    def _event_from_detection(self, detection: dict):
        detection_result = {
            "is_anomaly": True,
            "reason": detection["reason"],
            "ratio": detection["ratio"],
            "current_revenue": detection["current_revenue"],
            "baseline_revenue": detection["baseline_revenue"],
            "anomaly_score": detection["anomaly_score"],
        }
        return self.unified_pipeline.create_event(
            timestamp=detection["timestamp"],
            bucket=detection["timestamp"],
            anomaly_type=detection["anomaly_type"],
            entity_id="GLOBAL",
            detection_result=detection_result,
            time_scale=detection["time_scale"],
            model_version=detection["model_version"],
            anomaly_score=detection["anomaly_score"],
        )

    def fit_historical(self, hourly_rows: list[dict], daily_rows: list[dict]):
        """Fit separate models and return historical anomaly events."""
        events = []
        for time_scale, rows in (
            ("hourly", hourly_rows),
            ("daily", daily_rows),
        ):
            detections = self.detectors[time_scale].detect_historical(rows)
            events.extend(
                self._event_from_detection(detection)
                for detection in detections
            )
        return events

    def process_bucket(self, bucket: datetime, transactions: list[dict]):
        """Accumulate one completed minute into its hourly and daily totals."""
        revenue = sum(
            max(0.0, float(transaction.get("revenue", 0.0)))
            for transaction in transactions
        )
        for time_scale in ("hourly", "daily"):
            interval = bucket_start(bucket, time_scale)
            self.pending_revenue[time_scale][interval] += revenue
        return []

    def process_completed_buckets(self, current_time: datetime | str):
        current_time = as_utc(current_time)
        completed_minutes = self.bucket_processor.get_completed_buckets(
            current_time
        )

        for minute in completed_minutes:
            transactions = self.bucket_processor.get_transactions(minute)
            self.process_bucket(minute, transactions)
            self.bucket_processor.mark_processed(minute)
            self.bucket_processor.buckets.pop(minute, None)

        events = []
        for time_scale, pending in self.pending_revenue.items():
            detector = self.detectors[time_scale]
            completed_intervals = [
                interval
                for interval in sorted(pending)
                if next_bucket_start(interval, time_scale) <= current_time
            ]
            for interval in completed_intervals:
                detection = detector.detect_live(
                    interval,
                    pending.pop(interval),
                )
                if detection is not None:
                    events.append(self._event_from_detection(detection))
        return events
