"""Create lag and calendar features for observed product/country series."""

from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/daily_product_demand.csv")
OUTPUT_FILE = Path("data/processed/ml_features.csv")


def create_features():
    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
    required = {
        "date",
        "product_id",
        "store_id",
        "category",
        "region",
        "demand",
        "revenue",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Daily demand data is missing columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("Daily demand data is empty")

    keys = ["product_id", "store_id"]
    df = df.sort_values(keys + ["date"]).reset_index(drop=True)
    duplicates = df.duplicated(keys + ["date"])
    if duplicates.any():
        raise ValueError("Daily data has duplicate product/country/date rows")

    grouped = df.groupby(keys, sort=False)["demand"]
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    df["lag_1"] = grouped.shift(1)
    df["lag_2"] = grouped.shift(2)
    df["lag_7"] = grouped.shift(7)
    df["rolling_mean_7"] = grouped.transform(
        lambda values: values.shift(1).rolling(7, min_periods=7).mean()
    )
    df = df.dropna(
        subset=["lag_1", "lag_2", "lag_7", "rolling_mean_7"]
    ).copy()
    if df.empty:
        raise ValueError("No feature rows remain after the seven-day lag period")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Feature rows written: {len(df):,}")
    print(f"Feature file: {OUTPUT_FILE}")
    return df


if __name__ == "__main__":
    features = create_features()
    print("Date range:", features["date"].min(), "to", features["date"].max())
