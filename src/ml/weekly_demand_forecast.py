"""Country and StockCode level weekly demand forecasting."""

from __future__ import annotations

import math
from datetime import date, timedelta

from sklearn.ensemble import RandomForestRegressor


LAG_WEEKS = (1, 2, 4, 8)
MIN_HISTORY_WEEKS = 20
MIN_TRAINING_ROWS = 12
MAX_FORECAST_WEEKS = 13


class InsufficientHistoryError(ValueError):
    """Raised when a selected country and StockCode lack model history."""


def _features(values: list[float], target_week: date) -> list[float]:
    """Build predictors using data strictly before ``target_week``."""
    iso_week = target_week.isocalendar().week
    return [
        *(values[-lag] for lag in LAG_WEEKS),
        sum(values[-4:]) / 4,
        sum(values[-8:]) / 8,
        math.sin(2 * math.pi * iso_week / 52.18),
        math.cos(2 * math.pi * iso_week / 52.18),
    ]


def forecast_weekly_units(history: list[dict], horizon_weeks: int) -> dict:
    """Fit a Random Forest on one product-country weekly series and forecast.

    ``history`` contains ``week_start`` (a Monday ``date``) and ``units``.
    Missing weeks between the first and last observed sales weeks are zero-filled.
    Predictions are recursive and rounded to whole, nonnegative units.
    """
    if not 1 <= horizon_weeks <= MAX_FORECAST_WEEKS:
        raise ValueError(
            f"Forecast horizon must be between 1 and {MAX_FORECAST_WEEKS} weeks."
        )
    if not history:
        raise InsufficientHistoryError(
            "No historical sales were found for this selection."
        )

    units_by_week = {
        item["week_start"]: float(item["units"])
        for item in history
    }
    first_week = min(units_by_week)
    last_week = max(units_by_week)

    weeks: list[date] = []
    values: list[float] = []
    current_week = first_week
    while current_week <= last_week:
        weeks.append(current_week)
        values.append(units_by_week.get(current_week, 0.0))
        current_week += timedelta(days=7)

    training_features = []
    training_targets = []
    for index in range(max(LAG_WEEKS), len(values)):
        training_features.append(_features(values[:index], weeks[index]))
        training_targets.append(values[index])

    if len(weeks) < MIN_HISTORY_WEEKS or len(training_features) < MIN_TRAINING_ROWS:
        raise InsufficientHistoryError(
            "There is not enough weekly history for a reliable forecast for this "
            f"Country and StockCode. Found {len(weeks)} calendar weeks; at least "
            f"{MIN_HISTORY_WEEKS} weeks ({MIN_TRAINING_ROWS} training weeks) are required."
        )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=2,
        max_features=0.9,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(training_features, training_targets)

    future = []
    future_values = values.copy()
    forecast_week = last_week + timedelta(days=7)
    for week_number in range(1, horizon_weeks + 1):
        estimate = float(model.predict([_features(future_values, forecast_week)])[0])
        predicted_units = max(0, int(round(estimate)))
        future.append(
            {
                "week_number": week_number,
                "week_start": forecast_week.isoformat(),
                "week_end": (forecast_week + timedelta(days=6)).isoformat(),
                "predicted_units": predicted_units,
            }
        )
        future_values.append(max(0.0, estimate))
        forecast_week += timedelta(days=7)

    return {
        "history_start_week": first_week.isoformat(),
        "last_observed_week": last_week.isoformat(),
        "history_weeks": len(weeks),
        "weeks_with_sales": len(units_by_week),
        "historical_units": int(round(sum(values))),
        "history": [
            {"week_start": week.isoformat(), "units": int(round(units))}
            for week, units in zip(weeks, values)
        ],
        "forecast": future,
    }
