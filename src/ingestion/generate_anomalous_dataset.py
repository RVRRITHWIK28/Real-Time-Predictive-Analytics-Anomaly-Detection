import pandas as pd

from src.ingestion.anomaly_injector import (
    inject_quantity_anomaly,
    inject_transaction_drop,
    inject_transaction_spike,
)


INPUT_FILE = "data/raw/normal_transactions.csv"

OUTPUT_FILE = "data/raw/anomalous_transactions.csv"


def main():
    print("=" * 60)
    print("ANOMALOUS DATASET GENERATION")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    print(f"Normal transactions: {len(df)}")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    # --------------------------------------------------
    # Inject transaction-volume spike
    # --------------------------------------------------

    spike_date = pd.Timestamp(
        "2026-09-20"
    ).date()

    spike_hour = 19

    before_spike = (
        (df["timestamp"].dt.date == spike_date)
        & (df["timestamp"].dt.hour == spike_hour)
    )

    print(
        f"Spike target before: "
        f"{before_spike.sum()}"
    )

    df = inject_transaction_spike(
        df,
        target_date=spike_date,
        target_hour=spike_hour,
        multiplier=2.5,
    )

    # --------------------------------------------------
    # Inject transaction-volume drop
    # --------------------------------------------------

    drop_date = pd.Timestamp(
        "2026-09-21"
    ).date()

    drop_hour = 19

    before_drop = (
        (df["timestamp"].dt.date == drop_date)
        & (df["timestamp"].dt.hour == drop_hour)
    )

    print(
        f"Drop target before: "
        f"{before_drop.sum()}"
    )

    df = inject_transaction_drop(
        df,
        target_date=drop_date,
        target_hour=drop_hour,
        remaining_fraction=0.30,
    )

    # Inject quantity anomaly
    quantity_anomaly_date = pd.Timestamp(
        "2026-09-22"
    ).date()

    quantity_anomaly_hour = 19

    before_quantity_anomaly = (
        (df["timestamp"].dt.date == quantity_anomaly_date)
        & (df["timestamp"].dt.hour == quantity_anomaly_hour)
    )

    print(
        f"Quantity anomaly target before: "
        f"{before_quantity_anomaly.sum()}"
    )

    df = inject_quantity_anomaly(
        df,
        target_date=quantity_anomaly_date,
        target_hour=quantity_anomaly_hour,
        quantity_multiplier=5,
    )

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print(
        f"Anomalous transactions: {len(df)}"
    )

    print(
        f"Dataset saved to: {OUTPUT_FILE}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()