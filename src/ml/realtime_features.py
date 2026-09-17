from pathlib import Path

import pandas as pd


class RealtimeFeatureBuilder:

    def __init__(
        self,
        data_path="data/processed/daily_product_demand.csv"
    ):
        self.data_path = Path(data_path)

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Demand data not found: {self.data_path}"
            )

        self.data = pd.read_csv(self.data_path)

        self.data["date"] = pd.to_datetime(
            self.data["date"]
        )

    def build_features(
        self,
        product_id,
        store_id,
        prediction_date,
        live_demand=None
    ):
        """
        Build ML features for a real-time demand prediction.

        Historical demand comes from the processed dataset.
        Optional live_demand can be added as the latest
        completed daily demand.
        """

        prediction_date = pd.to_datetime(
            prediction_date
        )

        # Historical data before prediction date
        history = self.data[
            (self.data["product_id"] == product_id)
            & (self.data["store_id"] == store_id)
            & (self.data["date"] < prediction_date)
        ].copy()

        history = history.sort_values("date")

        # Add the latest completed live day if supplied
        if live_demand is not None:

            live_date = prediction_date - pd.Timedelta(
                days=1
            )

            live_record = {
                "date": live_date,
                "product_id": product_id,
                "store_id": store_id,
                "category": (
                    history.iloc[-1]["category"]
                    if len(history) > 0
                    else None
                ),
                "region": (
                    history.iloc[-1]["region"]
                    if len(history) > 0
                    else None
                ),
                "demand": float(live_demand),
                "revenue": 0.0,
            }

            history = pd.concat(
                [
                    history,
                    pd.DataFrame([live_record])
                ],
                ignore_index=True
            )

            history = (
                history
                .drop_duplicates(
                    subset=["date"],
                    keep="last"
                )
                .sort_values("date")
            )

        if len(history) < 7:
            raise ValueError(
                f"Not enough historical data for "
                f"{product_id} at {store_id}. "
                f"At least 7 previous days are required."
            )

        # Most recent demand values
        lag_1 = history.iloc[-1]["demand"]
        lag_2 = history.iloc[-2]["demand"]
        lag_7 = history.iloc[-7]["demand"]

        # Previous 7-day average
        rolling_mean_7 = (
            history.iloc[-7:]["demand"].mean()
        )

        # Calendar features
        day_of_week = prediction_date.dayofweek
        day_of_month = prediction_date.day
        week_of_year = prediction_date.isocalendar().week
        is_weekend = int(day_of_week >= 5)

        # Product metadata
        latest_record = history.iloc[-1]

        features = {
            "product_id": product_id,
            "store_id": store_id,
            "category": latest_record["category"],
            "region": latest_record["region"],
            "day_of_week": day_of_week,
            "day_of_month": day_of_month,
            "week_of_year": int(week_of_year),
            "is_weekend": is_weekend,
            "lag_1": float(lag_1),
            "lag_2": float(lag_2),
            "lag_7": float(lag_7),
            "rolling_mean_7": float(
                rolling_mean_7
            ),
        }

        return features


if __name__ == "__main__":

    builder = RealtimeFeatureBuilder()

    features = builder.build_features(
        product_id="P1001",
        store_id="S001",
        prediction_date="2026-10-01"
    )

    print("=" * 60)
    print("REAL-TIME FEATURE BUILDER TEST")
    print("=" * 60)

    print("\nGenerated ML features:\n")

    for key, value in features.items():
        print(f"{key:20} : {value}")

    print("=" * 60)
    print(
        "REAL-TIME FEATURE BUILDER TEST COMPLETE"
    )
    print("=" * 60)