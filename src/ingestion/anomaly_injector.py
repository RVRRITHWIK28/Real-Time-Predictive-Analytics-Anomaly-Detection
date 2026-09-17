import uuid

import pandas as pd


def inject_transaction_spike(
    df,
    target_date,
    target_hour,
    multiplier=2.5,
):
    """
    Inject a transaction-volume spike into a specific
    date and hour using new event IDs.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    target_mask = (
        (df["timestamp"].dt.date == target_date)
        & (df["timestamp"].dt.hour == target_hour)
    )

    target_transactions = df[target_mask].copy()

    if target_transactions.empty:
        raise ValueError(
            "No transactions found for the target date and hour."
        )

    additional_count = int(
        len(target_transactions) * (multiplier - 1)
    )

    additional_transactions = target_transactions.sample(
        n=additional_count,
        replace=True,
        random_state=42,
    ).copy()

    additional_transactions["event_id"] = [
        f"evt_anomaly_{uuid.uuid4().hex[:12]}"
        for _ in range(len(additional_transactions))
    ]

    df = pd.concat(
        [df, additional_transactions],
        ignore_index=True,
    )

    return df

def inject_transaction_drop(
    df,
    target_date,
    target_hour,
    remaining_fraction=0.30,
):
    """
    Inject a transaction-volume drop into a specific
    date and hour.

    remaining_fraction determines how much of the
    original volume remains.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    target_mask = (
        (df["timestamp"].dt.date == target_date)
        & (df["timestamp"].dt.hour == target_hour)
    )

    target_transactions = df[target_mask].copy()

    if target_transactions.empty:
        raise ValueError(
            "No transactions found for the target date and hour."
        )

    keep_count = int(
        len(target_transactions) * remaining_fraction
    )

    keep_count = max(keep_count, 1)

    target_to_keep = target_transactions.sample(
        n=keep_count,
        random_state=42,
    )

    non_target_transactions = df[~target_mask]

    df = pd.concat(
        [
            non_target_transactions,
            target_to_keep,
        ],
        ignore_index=True,
    )

    return df

def inject_quantity_anomaly(
    df,
    target_date,
    target_hour,
    quantity_multiplier=5,
):
    """
    Inject unusually high transaction quantities
    into a specific date and hour.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    target_mask = (
        (df["timestamp"].dt.date == target_date)
        & (df["timestamp"].dt.hour == target_hour)
    )

    target_transactions = df[target_mask].copy()

    if target_transactions.empty:
        raise ValueError(
            "No transactions found for the target date and hour."
        )

    # Select a small portion of transactions
    anomaly_count = max(
        int(len(target_transactions) * 0.05),
        1,
    )

    anomaly_transactions = target_transactions.sample(
        n=anomaly_count,
        random_state=42,
    ).copy()

    # Generate new event IDs
    anomaly_transactions["event_id"] = [
        f"evt_quantity_anomaly_{uuid.uuid4().hex[:12]}"
        for _ in range(len(anomaly_transactions))
    ]

    # Increase quantity
    anomaly_transactions["quantity"] = (
        anomaly_transactions["quantity"]
        * quantity_multiplier
    )

    # Recalculate revenue
    anomaly_transactions["revenue"] = (
        anomaly_transactions["quantity"]
        * anomaly_transactions["unit_price"]
        * (1 - anomaly_transactions["discount"])
    ).round(2)

    df = pd.concat(
        [df, anomaly_transactions],
        ignore_index=True,
    )

    return df