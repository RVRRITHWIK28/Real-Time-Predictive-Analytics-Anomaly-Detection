import csv

import random
from datetime import datetime, timedelta, timezone

from src.ingestion.data_generator import (
    generate_transaction,
    get_time_demand_multiplier,
    get_day_demand_multiplier,
)

from src.ingestion.master_data import PRODUCTS


BASE_TRANSACTIONS_PER_HOUR = 50


def get_transaction_count(event_time, start_date) -> int:
    """
    Calculate how many transactions should occur
    during a particular hour.
    """

    time_multiplier = get_time_demand_multiplier(
        event_time.hour
    )

    day_multiplier = get_day_demand_multiplier(
        event_time
    )

    trend_multiplier = get_trend_multiplier(
        event_time,
        start_date,
    )

    expected_count = (
        BASE_TRANSACTIONS_PER_HOUR
        * time_multiplier
        * day_multiplier
        * trend_multiplier
    )

    variation = random.uniform(0.80, 1.20)

    transaction_count = int(
        expected_count * variation
    )

    return max(transaction_count, 1)

def get_product_demand_multiplier(product_id: str) -> float:
    """
    Return a demand multiplier based on product popularity.
    """

    for product in PRODUCTS:
        if product["product_id"] == product_id:
            return 0.5 + (product["demand_weight"] * 3)

    return 1.0

def generate_historical_data(
    start_date,
    number_of_days,
):
    """
    Generate realistic historical transaction data
    for a specified number of days.
    """

    transactions = []

    current_time = start_date

    end_time = start_date + timedelta(days=number_of_days)

    while current_time < end_time:

        transaction_count = get_transaction_count(
    current_time,
    start_date,
)

        for _ in range(transaction_count):

            minute_offset = random.randint(0, 59)
            second_offset = random.randint(0, 59)

            event_time = current_time + timedelta(
                minutes=minute_offset,
                seconds=second_offset,
            )

            event = generate_transaction(
                event_time=event_time
            )

            transactions.append(event)

        current_time += timedelta(hours=1)

    return transactions

def save_transactions_to_csv(transactions, file_path):
    """
    Save generated transactions to a CSV file.
    """

    if not transactions:
        return

    fieldnames = list(
        transactions[0].model_dump().keys()
    )

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for transaction in transactions:
            writer.writerow(
                transaction.model_dump()
            )

def get_store_demand_multiplier(store_id: str) -> float:
    """
    Return a demand multiplier based on store.
    """

    store_multipliers = {
        "S001": 1.15,
        "S002": 1.20,
        "S003": 1.05,
        "S004": 1.25,
        "S005": 1.20,
        "S006": 1.00,
        "S007": 0.95,
        "S008": 0.90,
    }

    return store_multipliers.get(store_id, 1.0)

def get_trend_multiplier(event_time, start_date) -> float:
    """
    Return a gradual demand trend based on
    how many days have passed since the start date.
    """

    days_since_start = (
        event_time.date() - start_date.date()
    ).days

    daily_growth_rate = 0.01

    return 1.0 + (days_since_start * daily_growth_rate)