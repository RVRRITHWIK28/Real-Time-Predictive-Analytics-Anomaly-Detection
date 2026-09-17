import pandas as pd

from src.ingestion.anomaly_injector import (
    inject_transaction_drop,
    inject_transaction_spike,
)


print("ANOMALY INJECTION TEST")
print("=" * 60)

df = pd.read_csv(
    "data/raw/normal_transactions.csv"
)

before_count = len(df)

print(f"Transactions before injection: {before_count}")

target_date = pd.Timestamp(
    "2026-09-20"
).date()

target_hour = 19

target_before = (
    (pd.to_datetime(df["timestamp"]).dt.date == target_date)
    & (pd.to_datetime(df["timestamp"]).dt.hour == target_hour)
)

print(
    f"Transactions in target hour before: "
    f"{target_before.sum()}"
)

df_anomalous = inject_transaction_spike(
    df,
    target_date=target_date,
    target_hour=target_hour,
    multiplier=2.5,
)

after_count = len(df_anomalous)

target_after = (
    (df_anomalous["timestamp"].dt.date == target_date)
    & (df_anomalous["timestamp"].dt.hour == target_hour)
)

print(
    f"Transactions in target hour after: "
    f"{target_after.sum()}"
)

print(
    f"Transactions after injection: "
    f"{after_count}"
)


duplicate_ids = (
    df_anomalous["event_id"]
    .duplicated()
    .sum()
)

print(
    f"Duplicate event IDs after injection: "
    f"{duplicate_ids}"
)

print("\nTRANSACTION DROP TEST")
print("=" * 60)

df_drop = inject_transaction_drop(
    df,
    target_date=pd.Timestamp(
        "2026-09-21"
    ).date(),
    target_hour=19,
    remaining_fraction=0.30,
)

target_drop_mask = (
    (df_drop["timestamp"].dt.date == pd.Timestamp("2026-09-21").date())
    & (df_drop["timestamp"].dt.hour == 19)
)

print(
    f"Transactions in target hour after drop: "
    f"{target_drop_mask.sum()}"
)

print(
    f"Total transactions after drop: "
    f"{len(df_drop)}"
)

print(
    f"Duplicate event IDs after drop: "
    f"{df_drop['event_id'].duplicated().sum()}"
)

print("\nAnomaly injection completed successfully!")