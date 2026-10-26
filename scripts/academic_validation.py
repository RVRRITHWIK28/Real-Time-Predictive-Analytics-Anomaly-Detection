"""Run a reproducible Online Retail II forecast backtest and anomaly validation.

Run from the repository root:
    python scripts/academic_validation.py --archive data/raw/online+retail+ii.zip

Natural anomaly review labels are deliberately left for a human reviewer.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ingestion.online_retail_ii import DEFAULT_ARCHIVE, iter_online_retail_sales, new_source_stats
from src.ml.revenue_isolation_forest import (
    BUSINESS_TIMEZONE, RevenueIsolationForestDetector, as_utc,
    bucket_start, build_regular_series,
)
from src.ml.weekly_demand_forecast import (
    MAX_FORECAST_WEEKS, MIN_HISTORY_WEEKS, forecast_weekly_units,
)

HORIZON = 13
FOLDS = 3
MIN_SERIES_WEEKS = 52 + HORIZON * FOLDS


def load_data(archive):
    weekly = defaultdict(lambda: defaultdict(float))
    hourly, daily = defaultdict(float), defaultdict(float)
    source = new_source_stats()
    for event in iter_online_retail_sales(archive, source):
        stamp = datetime.fromisoformat(event["timestamp"])
        day = date.fromisoformat(event["business_date"])
        monday = day - timedelta(days=day.weekday())
        weekly[(event["country"], event["product_id"])][monday] += float(event["quantity"])
        hourly[bucket_start(stamp, "hourly")] += float(event["revenue"])
        daily[bucket_start(stamp, "daily")] += float(event["revenue"])
    hourly = build_regular_series(
        [{"timestamp": k, "revenue": v} for k, v in hourly.items()], "hourly"
    )
    daily = build_regular_series(
        [{"timestamp": k, "revenue": v} for k, v in daily.items()], "daily"
    )
    return weekly, hourly, daily, source


def dense_series(observed):
    start, end = min(observed), max(observed)
    dates, values = [], []
    current = start
    while current <= end:
        dates.append(current)
        values.append(float(observed.get(current, 0)))
        current += timedelta(days=7)
    return dates, values


def calc_metrics(actual, predicted):
    actual, predicted = np.asarray(actual, dtype=float), np.asarray(predicted, dtype=float)
    errors = predicted - actual
    absolute = np.abs(errors)
    return {
        "n": int(len(actual)),
        "mae": float(absolute.mean()),
        "rmse": float(np.sqrt(np.square(errors).mean())),
        "wape_pct": float(absolute.sum() / actual.sum() * 100) if actual.sum() else math.nan,
    }


def result_path(path):
    """Prefer repository-relative result paths so reports are portable."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())

def backtest(weekly, minimum_weeks, output):
    results = []
    eligible_series = [
        (key, observed)
        for key, observed in weekly.items()
        if len(observed) >= minimum_weeks
        and (max(observed) - min(observed)).days // 7 + 1 >= minimum_weeks
    ]
    eligible_series.sort(key=lambda item: item[0])
    for series_number, ((country, stock_code), observed) in enumerate(eligible_series, start=1):
        if series_number % 100 == 0:
            print(f"Backtest progress: {series_number:,}/{len(eligible_series):,} eligible product-country series", flush=True)
        dates, values = dense_series(observed)
        count = len(dates)
        # Three non-overlapping 13-week windows. Earliest test begins at week 53,
        # so 52-week seasonal-naive values exist at all forecast horizons.
        origins = [count - HORIZON * k for k in range(FOLDS, 0, -1)]
        for fold, origin in enumerate(origins, 1):
            history = [
                {"week_start": dates[i], "units": values[i]}
                for i in range(origin)
            ]
            forecast = forecast_weekly_units(history, HORIZON)["forecast"]
            for offset in range(HORIZON):
                target = origin + offset
                actual = values[target]
                predictions = (
                    ("Random Forest", float(forecast[offset]["predicted_units"])),
                    ("Naive (last week)", values[origin - 1]),
                    ("Seasonal naive (52 weeks)", values[target - 52]),
                )
                for model, predicted in predictions:
                    results.append({
                        "country": country, "stock_code": stock_code,
                        "series_history_weeks": count, "fold": fold,
                        "horizon_week": offset + 1,
                        "target_week": dates[target].isoformat(),
                        "model": model, "actual_units": actual,
                        "predicted_units": predicted,
                        "absolute_error": abs(actual - predicted),
                    })

    if not results:
        raise RuntimeError("No series qualified for the forecast backtest.")

    predictions_file = output / "forecast_backtest_predictions.csv"
    with predictions_file.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    summary = []
    scopes = [("overall", None)] + [("horizon_week", h) for h in range(1, 14)]
    for scope, horizon in scopes:
        group = results if scope == "overall" else [
            row for row in results if row["horizon_week"] == horizon
        ]
        grouped = defaultdict(list)
        for row in group:
            grouped[row["model"]].append(row)
        metrics = {
            model: calc_metrics(
                [row["actual_units"] for row in rows],
                [row["predicted_units"] for row in rows],
            )
            for model, rows in grouped.items()
        }
        rf_mae = metrics["Random Forest"]["mae"]
        naive_mae = metrics["Naive (last week)"]["mae"]
        seasonal_mae = metrics["Seasonal naive (52 weeks)"]["mae"]
        for model, values_by_metric in metrics.items():
            summary.append({
                "scope": scope, "horizon_week": horizon if horizon else "all",
                "model": model, **values_by_metric,
                "mae_skill_vs_naive_pct": (
                    (1 - rf_mae / naive_mae) * 100 if naive_mae else math.nan
                ),
                "mae_skill_vs_seasonal_naive_pct": (
                    (1 - rf_mae / seasonal_mae) * 100 if seasonal_mae else math.nan
                ),
            })
    metrics_file = output / "forecast_metrics_by_horizon.csv"
    with metrics_file.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    return {
        "eligible_series": len(eligible_series), "excluded_series": len(weekly) - len(eligible_series),
        "minimum_calendar_weeks": minimum_weeks, "minimum_weeks_with_sales": minimum_weeks,
        "rolling_origins_per_series": FOLDS,
        "forecast_horizon_weeks": HORIZON,
        "observations_per_model": len(results) // 3,
        "metrics_file": result_path(metrics_file), "predictions_file": result_path(predictions_file),
    }


def _is_flagged(detector, timestamp, revenue):
    feature = detector._features([{
        "timestamp": timestamp, "revenue": max(0.0, float(revenue))
    }])
    return bool(detector.model.predict(feature)[0] == -1)


def revenue_evidence_screen(ratio):
    """Describe deviation from the historical median; this is not a truth label."""
    if ratio is None:
        return "unavailable"
    ratio = float(ratio)
    if ratio >= 2.0 or ratio <= 0.5:
        return "strong deviation: >=2x or <=0.5x median"
    if ratio >= 1.5 or ratio <= (1.0 / 1.5):
        return "moderate deviation: >=1.5x or <=0.67x median"
    if ratio >= 1.25 or ratio <= 0.8:
        return "mild deviation: >=1.25x or <=0.8x median"
    return "near median: within 0.8x-1.25x"


def validate_anomalies(hourly, daily, archive, output):
    alerts, injections, holdout_summary = [], [], {}
    for scale, rows in (("hourly", hourly), ("daily", daily)):
        split = int(len(rows) * 0.70)
        training, holdout = rows[:split], rows[split:]
        detector = RevenueIsolationForestDetector(scale, contamination=0.01)
        detector.fit_history(training)
        if detector.model is None:
            raise RuntimeError(f"Insufficient {scale} history to fit detector.")
        holdout_predictions = [
            _is_flagged(detector, row["timestamp"], row["revenue"])
            for row in holdout
        ]
        holdout_summary[scale] = {
            "holdout_buckets": len(holdout),
            "untouched_holdout_flag_rate_pct": (
                sum(holdout_predictions) / len(holdout_predictions) * 100
            ),
            "interpretation": "unlabeled holdout flag rate, not a false-positive rate",
        }
        positive = [i for i, row in enumerate(holdout) if row["revenue"] > 0]
        if positive:
            selected = [
                positive[i] for i in np.linspace(
                    0, len(positive) - 1, min(300, len(positive)), dtype=int
                )
            ]
            injected_spikes, injected_drops = [], []
            for index in selected:
                row = holdout[index]
                revenue = float(row["revenue"])
                injected_spikes.append(
                    _is_flagged(detector, row["timestamp"], revenue * 5)
                )
                injected_drops.append(
                    _is_flagged(detector, row["timestamp"], revenue * 0.1)
                )
            for label, flags in (
                ("5x spike", injected_spikes), ("90% drop", injected_drops)
            ):
                injections.append({
                    "time_scale": scale, "perturbation": label,
                    "known_injected_cases": len(flags),
                    "detected_cases": int(sum(flags)),
                    "detection_rate_pct": sum(flags) / len(flags) * 100,
                    "note": "controlled synthetic perturbations on real holdout buckets; not natural-anomaly recall",
                })
        alerts.extend(
            RevenueIsolationForestDetector(scale, contamination=0.01)
            .detect_historical(rows)
        )

    injection_file = output / "anomaly_injection_validation.csv"
    with injection_file.open("w", newline="", encoding="utf-8") as stream:
        fields = list(injections[0]) if injections else [
            "time_scale", "perturbation", "known_injected_cases",
            "detected_cases", "detection_rate_pct", "note",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(injections)

    # Build a reproducible audit sample stratified by interval and anomaly type.
    groups = defaultdict(list)
    for alert in alerts:
        direction = alert["anomaly_type"].split("_")[-1]
        groups[f'{alert["time_scale"]}|{direction}'].append(alert)
    rng, sample = random.Random(42), []
    for group in sorted(groups):
        options = sorted(groups[group], key=lambda row: row["timestamp"])
        sample.extend(rng.sample(options, min(15, len(options))))
    sample.sort(key=lambda row: (row["time_scale"], row["timestamp"]))

    selected_buckets, review = set(), []
    for alert in sample:
        stamp = as_utc(alert["timestamp"])
        key = bucket_start(stamp, alert["time_scale"])
        selected_buckets.add((alert["time_scale"], key))
        review.append({
            "time_scale": alert["time_scale"],
            "timestamp_utc": stamp.isoformat(),
            "local_business_time": stamp.astimezone(BUSINESS_TIMEZONE).isoformat(),
            "anomaly_type": alert["anomaly_type"],
            "observed_revenue_gbp": alert["current_revenue"],
            "historical_median_baseline_gbp": alert["baseline_revenue"],
            "observed_to_baseline_ratio": alert["ratio"],
            "isolation_forest_score": alert["anomaly_score"],
            "ratio_evidence_screen": revenue_evidence_screen(alert["ratio"]),
            "contributing_sale_lines": "", "distinct_invoices": "",
            "largest_invoice_revenue_share_pct": "",
            "review_label": "", "review_notes": "",
        })

    # Expose invoice count and concentration as review context, without
    # automatically treating a model alert as a true business incident.
    invoice_totals, line_counts = defaultdict(float), Counter()
    if selected_buckets:
        source = new_source_stats()
        for event in iter_online_retail_sales(archive, source):
            stamp = datetime.fromisoformat(event["timestamp"])
            for scale in ("hourly", "daily"):
                key = (scale, bucket_start(stamp, scale))
                if key in selected_buckets:
                    invoice_totals[(scale, key[1], event["invoice_id"])] += float(event["revenue"])
                    line_counts[key] += 1
    for row in review:
        stamp = datetime.fromisoformat(row["timestamp_utc"])
        key = (row["time_scale"], bucket_start(stamp, row["time_scale"]))
        values = [
            value for (scale, bucket, _invoice), value in invoice_totals.items()
            if (scale, bucket) == key
        ]
        total = sum(values)
        row["contributing_sale_lines"] = line_counts[key]
        row["distinct_invoices"] = len(values)
        row["largest_invoice_revenue_share_pct"] = (
            round(max(values) / total * 100, 2) if total else ""
        )

    review_file = output / "anomaly_review_sample.csv"
    fields = list(review[0]) if review else [
        "time_scale", "timestamp_utc", "local_business_time", "anomaly_type",
        "observed_revenue_gbp", "historical_median_baseline_gbp",
        "observed_to_baseline_ratio", "isolation_forest_score",
        "ratio_evidence_screen", "contributing_sale_lines", "distinct_invoices",
        "largest_invoice_revenue_share_pct", "review_label", "review_notes",
    ]
    with review_file.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(review)

    return {
        "method": "chronological historical replay; score against past history; periodic refits",
        "contamination": 0.01,
        "hourly_bucket_count": len(hourly),
        "daily_bucket_count": len(daily),
        "hourly_flag_count": sum(a["time_scale"] == "hourly" for a in alerts),
        "daily_flag_count": sum(a["time_scale"] == "daily" for a in alerts),
        "total_flag_count": len(alerts),
        "hourly_flag_rate_pct": (
            sum(a["time_scale"] == "hourly" for a in alerts) / len(hourly) * 100
            if hourly else 0.0
        ),
        "daily_flag_rate_pct": (
            sum(a["time_scale"] == "daily" for a in alerts) / len(daily) * 100
            if daily else 0.0
        ),
        "unlabeled_holdout": holdout_summary,
        "review_sample_rows": len(review),
        "review_sample_screen_counts": dict(Counter(
            row["ratio_evidence_screen"] for row in review
        )),
        "review_sample_file": result_path(review_file),
        "review_note": "Review labels are blank; inspect source context before assigning them.",
        "injection_file": result_path(injection_file),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--output-dir", type=Path, default=Path("reports/academic_validation"))
    parser.add_argument("--min-series-weeks", type=int, default=MIN_SERIES_WEEKS)
    args = parser.parse_args()
    if HORIZON > MAX_FORECAST_WEEKS:
        raise RuntimeError("Backtest horizon exceeds the model-supported horizon.")
    if args.min_series_weeks < MIN_HISTORY_WEEKS + 2 * HORIZON:
        raise ValueError("Minimum history is too short for all rolling folds.")

    archive, output = args.archive.resolve(), args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    print(f"Reading dataset: {archive}", flush=True)
    weekly, hourly, daily, source = load_data(archive)
    print(
        f"Loaded {source['sale_events']:,} positive sale lines; {len(weekly):,} "
        f"country/StockCode series; {len(hourly):,} hourly and {len(daily):,} daily buckets.",
        flush=True,
    )
    print("Running rolling 13-week forecast comparison...", flush=True)
    forecast = backtest(weekly, args.min_series_weeks, output)
    print("Running chronological anomaly replay and controlled perturbations...", flush=True)
    anomaly = validate_anomalies(hourly, daily, archive, output)
    summary = {
        "dataset": "Online Retail II",
        "dataset_period": "2009-12-01 through 2011-12-09",
        "dataset_citation": "Chen, D. (2012). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D",
        "source_row_counts": source,
        "forecast_evaluation": forecast,
        "anomaly_evaluation": anomaly,
        "limitations": [
            "Positive sale lines only; cancellations and returns/adjustments are excluded.",
            "Weekly zero-fill between first and last sale assumes product availability; inventory status is not observed.",
            "Forecast results cover longer-history country/StockCode series, not short-history items.",
            "The dataset ends in 2011; forecast dates are historical projections from the final observed week.",
            "No labeled natural-anomaly ground truth exists; Isolation Forest totals are flags, not confirmed incidents.",
            "Controlled shifts measure sensitivity to those perturbations, not precision on natural events.",
            "StockCodes may include service/manual entries because the dataset has no clean merchandise category field.",
        ],
    }
    path = output / "academic_validation_summary.json"
    path.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Saved outputs to {output}", flush=True)
    print(json.dumps(summary, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
