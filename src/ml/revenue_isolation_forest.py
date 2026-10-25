"""Revenue-only Isolation Forest detectors for hourly and daily sales totals."""

from __future__ import annotations

from collections import deque
from datetime import datetime, time, timedelta, timezone
import math
from statistics import median
from zoneinfo import ZoneInfo

import numpy as np
from sklearn.ensemble import IsolationForest


MODEL_VERSION = "isolation_forest_v1"
BUSINESS_TIMEZONE = ZoneInfo("Europe/London")
SUPPORTED_TIME_SCALES = ("hourly", "daily")


def as_utc(value: datetime | str) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime):
        raise ValueError(f"Unsupported revenue bucket timestamp: {value!r}")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def bucket_start(value: datetime | str, time_scale: str) -> datetime:
    timestamp = as_utc(value)
    if time_scale == "hourly":
        return timestamp.replace(minute=0, second=0, microsecond=0)
    if time_scale == "daily":
        local_date = timestamp.astimezone(BUSINESS_TIMEZONE).date()
        local_midnight = datetime.combine(
            local_date,
            time.min,
            tzinfo=BUSINESS_TIMEZONE,
        )
        return local_midnight.astimezone(timezone.utc)
    raise ValueError(f"Unsupported time scale: {time_scale}")


def next_bucket_start(value: datetime, time_scale: str) -> datetime:
    bucket = as_utc(value)
    if time_scale == "hourly":
        return bucket + timedelta(hours=1)
    if time_scale == "daily":
        next_local_date = bucket.astimezone(BUSINESS_TIMEZONE).date() + timedelta(days=1)
        return datetime.combine(
            next_local_date,
            time.min,
            tzinfo=BUSINESS_TIMEZONE,
        ).astimezone(timezone.utc)
    raise ValueError(f"Unsupported time scale: {time_scale}")


def build_regular_series(rows: list[dict], time_scale: str) -> list[dict]:
    """Fill absent historical hours/days with zero revenue for consistent scoring."""
    if time_scale not in SUPPORTED_TIME_SCALES:
        raise ValueError(f"Unsupported time scale: {time_scale}")

    totals: dict[datetime, float] = {}
    for row in rows:
        raw_timestamp = row.get("timestamp", row.get("_id"))
        bucket = bucket_start(raw_timestamp, time_scale)
        totals[bucket] = totals.get(bucket, 0.0) + float(row.get("revenue", 0.0))

    if not totals:
        return []

    current = min(totals)
    last = max(totals)
    result = []
    while current <= last:
        result.append(
            {
                "timestamp": current,
                "revenue": max(0.0, float(totals.get(current, 0.0))),
            }
        )
        current = next_bucket_start(current, time_scale)
    return result


class RevenueIsolationForestDetector:
    """A separate seasonality-aware Isolation Forest for one revenue time scale."""

    def __init__(self, time_scale: str, contamination: float = 0.01):
        if time_scale not in SUPPORTED_TIME_SCALES:
            raise ValueError(f"Unsupported time scale: {time_scale}")
        if not 0.0 < contamination <= 0.5:
            raise ValueError("contamination must be greater than 0 and at most 0.5")

        self.time_scale = time_scale
        self.contamination = contamination
        self.min_history = 24 * 14 if time_scale == "hourly" else 60
        self.max_history = 24 * 365 if time_scale == "hourly" else 365 * 3
        self.refit_interval = 24 * 30 if time_scale == "hourly" else 30
        self.history: deque[dict] = deque(maxlen=self.max_history)
        self.model: IsolationForest | None = None
        self._since_refit = 0

    def _features(self, rows: list[dict]) -> np.ndarray:
        matrix = []
        for row in rows:
            local = as_utc(row["timestamp"]).astimezone(BUSINESS_TIMEZONE)
            revenue = max(0.0, float(row["revenue"]))
            log_revenue = math.log1p(revenue)

            if self.time_scale == "hourly":
                hour_of_day = local.hour + local.minute / 60.0
                hour_of_week = local.weekday() * 24 + local.hour
                matrix.append(
                    [
                        log_revenue,
                        math.sin(2 * math.pi * hour_of_day / 24.0),
                        math.cos(2 * math.pi * hour_of_day / 24.0),
                        math.sin(2 * math.pi * hour_of_week / 168.0),
                        math.cos(2 * math.pi * hour_of_week / 168.0),
                    ]
                )
            else:
                day_of_year = local.timetuple().tm_yday - 1
                matrix.append(
                    [
                        log_revenue,
                        math.sin(2 * math.pi * local.weekday() / 7.0),
                        math.cos(2 * math.pi * local.weekday() / 7.0),
                        math.sin(2 * math.pi * day_of_year / 365.2425),
                        math.cos(2 * math.pi * day_of_year / 365.2425),
                    ]
                )

        return np.asarray(matrix, dtype=float)

    def _new_model(self, sample_count: int) -> IsolationForest:
        return IsolationForest(
            n_estimators=200,
            max_samples=min(256, sample_count),
            contamination=self.contamination,
            random_state=42,
            n_jobs=1,
        )

    def _fit(self, rows: list[dict]) -> None:
        if len(rows) < self.min_history:
            self.model = None
            return
        self.model = self._new_model(len(rows))
        self.model.fit(self._features(rows))

    def fit_history(self, rows: list[dict]) -> None:
        ordered = sorted(
            (
                {
                    "timestamp": as_utc(row["timestamp"]),
                    "revenue": max(0.0, float(row["revenue"])),
                }
                for row in rows
            ),
            key=lambda item: item["timestamp"],
        )
        self.history = deque(ordered[-self.max_history :], maxlen=self.max_history)
        self._fit(list(self.history))
        self._since_refit = 0

    def _baseline(self, timestamp: datetime) -> float:
        rows = list(self.history)
        if not rows:
            return 0.0

        local = as_utc(timestamp).astimezone(BUSINESS_TIMEZONE)
        local_rows = [
            (as_utc(row["timestamp"]).astimezone(BUSINESS_TIMEZONE), float(row["revenue"]))
            for row in rows
        ]
        if self.time_scale == "hourly":
            matching = [
                revenue
                for row_time, revenue in local_rows
                if row_time.weekday() == local.weekday() and row_time.hour == local.hour
            ]
        else:
            matching = [
                revenue
                for row_time, revenue in local_rows
                if row_time.weekday() == local.weekday() and row_time.month == local.month
            ]

        values = matching or [revenue for _, revenue in local_rows]
        baseline = float(median(values))
        if baseline <= 0:
            positive_values = [value for value in values if value > 0]
            baseline = float(median(positive_values)) if positive_values else 0.01
        return baseline

    def _result(self, timestamp: datetime, revenue: float, anomaly_score: float) -> dict:
        baseline = self._baseline(timestamp)
        ratio = revenue / baseline if baseline > 0 else None
        anomaly_type = f"{self.time_scale}_revenue_spike" if revenue >= baseline else f"{self.time_scale}_revenue_drop"
        direction = "spike" if anomaly_type.endswith("_revenue_spike") else "drop"
        return {
            "timestamp": as_utc(timestamp),
            "time_scale": self.time_scale,
            "anomaly_type": anomaly_type,
            "is_anomaly": True,
            "reason": (
                f"Isolation Forest detected an unusual {self.time_scale} "
                f"revenue {direction}."
            ),
            "current_revenue": round(float(revenue), 2),
            "baseline_revenue": round(float(baseline), 2),
            "ratio": round(float(ratio), 4) if ratio is not None else None,
            "anomaly_score": round(float(anomaly_score), 6),
            "model_version": MODEL_VERSION,
        }

    def detect_historical(self, rows: list[dict]) -> list[dict]:
        """Score each bucket against earlier history to avoid training leakage."""
        ordered = sorted(
            (
                {
                    "timestamp": as_utc(row["timestamp"]),
                    "revenue": max(0.0, float(row["revenue"])),
                }
                for row in rows
            ),
            key=lambda item: item["timestamp"],
        )
        self.history = deque(maxlen=self.max_history)
        self.model = None
        events = []
        since_refit = 0

        for row in ordered:
            history = list(self.history)
            if len(history) < self.min_history:
                self.history.append(row)
                continue

            if self.model is None or since_refit >= self.refit_interval:
                self._fit(history)
                since_refit = 0

            if self.model is not None:
                features = self._features([row])
                if self.model.predict(features)[0] == -1:
                    score = -float(self.model.decision_function(features)[0])
                    events.append(
                        self._result(
                            row["timestamp"],
                            row["revenue"],
                            score,
                        )
                    )

            self.history.append(row)
            since_refit += 1

        # Retain a current model for incoming Kafka events after the backfill.
        self._fit(list(self.history))
        self._since_refit = 0
        return events

    def detect_live(self, timestamp: datetime, revenue: float) -> dict | None:
        """Score a completed bucket against past data, then update its history."""
        row = {
            "timestamp": as_utc(timestamp),
            "revenue": max(0.0, float(revenue)),
        }
        result = None
        if self.model is not None:
            matrix = self._features([row])
            if self.model.predict(matrix)[0] == -1:
                score = -float(self.model.decision_function(matrix)[0])
                result = self._result(row["timestamp"], row["revenue"], score)

        self.history.append(row)
        self._since_refit += 1
        if self.model is None or self._since_refit >= self.refit_interval:
            self._fit(list(self.history))
            self._since_refit = 0
        return result
