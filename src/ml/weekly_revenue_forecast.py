"""Country and StockCode weekly gross-revenue forecasting in GBP."""

from __future__ import annotations

import math
from datetime import date, timedelta

from sklearn.ensemble import RandomForestRegressor

from src.ml.weekly_demand_forecast import (
    LAG_WEEKS,
    MAX_FORECAST_WEEKS,
    MIN_HISTORY_WEEKS,
    MIN_TRAINING_ROWS,
    InsufficientHistoryError,
)


def _features(values: list[float], target_week: date) -> list[float]:
    """Use prior weekly revenue and annual calendar seasonality."""
    iso_week = target_week.isocalendar().week
    return [
        *(values[-lag] for lag in LAG_WEEKS),
        sum(values[-4:]) / 4,
        sum(values[-8:]) / 8,
        math.sin(2 * math.pi * iso_week / 52.18),
        math.cos(2 * math.pi * iso_week / 52.18),
    ]


def forecast_weekly_revenue(
    history: list[dict], horizon_weeks: int, n_jobs: int = -1
) -> dict:
    """Fit a country–StockCode Random Forest and forecast gross revenue.

    Each history row contains a Monday week_start date and revenue_gbp value.
    Missing weeks between first and last sales are zero-filled. Forecasts are
    recursive, nonnegative GBP values rounded to pence.
    """
    if not 1 <= horizon_weeks <= MAX_FORECAST_WEEKS:
        raise ValueError(
            f"Forecast horizon must be between 1 and {MAX_FORECAST_WEEKS} weeks."
        )
    if not history:
        raise InsufficientHistoryError(
            "No positive-revenue sales were found for this selection."
        )

    revenue_by_week = {
        item["week_start"]: max(0.0, float(item["revenue_gbp"]))
        for item in history
    }
    first_week, last_week = min(revenue_by_week), max(revenue_by_week)
    weeks, values = [], []
    current_week = first_week
    while current_week <= last_week:
        weeks.append(current_week)
        values.append(revenue_by_week.get(current_week, 0.0))
        current_week += timedelta(days=7)

    features, targets = [], []
    for index in range(max(LAG_WEEKS), len(values)):
        features.append(_features(values[:index], weeks[index]))
        targets.append(values[index])
    if len(weeks) < MIN_HISTORY_WEEKS or len(features) < MIN_TRAINING_ROWS:
        raise InsufficientHistoryError(
            "There is not enough weekly revenue history for this Country and "
            f"StockCode. Found {len(weeks)} calendar weeks; at least "
            f"{MIN_HISTORY_WEEKS} weeks ({MIN_TRAINING_ROWS} training weeks) are required."
        )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=2,
        max_features=0.9,
        random_state=42,
        n_jobs=n_jobs,
    )
    model.fit(features, targets)

    future, future_values = [], values.copy()
    forecast_week = last_week + timedelta(days=7)
    for week_number in range(1, horizon_weeks + 1):
        estimate = max(
            0.0,
            float(model.predict([_features(future_values, forecast_week)])[0]),
        )
        future.append(
            {
                "week_number": week_number,
                "week_start": forecast_week.isoformat(),
                "week_end": (forecast_week + timedelta(days=6)).isoformat(),
                "predicted_revenue_gbp": round(estimate, 2),
            }
        )
        future_values.append(estimate)
        forecast_week += timedelta(days=7)

    return {
        "history_start_week": first_week.isoformat(),
        "last_observed_week": last_week.isoformat(),
        "history_weeks": len(weeks),
        "weeks_with_sales": len(revenue_by_week),
        "historical_revenue_gbp": round(sum(values), 2),
        "history": [
            {"week_start": week.isoformat(), "revenue_gbp": round(value, 2)}
            for week, value in zip(weeks, values)
        ],
        "forecast": future,
    }
