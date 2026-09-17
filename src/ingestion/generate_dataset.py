from datetime import datetime, timezone

from src.ingestion.historical_generator import (
    generate_historical_data,
    save_transactions_to_csv,
)


START_DATE = datetime(
    2026,
    9,
    1,
    0,
    0,
    tzinfo=timezone.utc,
)

NUMBER_OF_DAYS = 30

OUTPUT_FILE = "data/raw/historical_transactions.csv"


def main():
    print("=" * 60)
    print("HISTORICAL DATASET GENERATION")
    print("=" * 60)

    print(f"Start date     : {START_DATE}")
    print(f"Number of days : {NUMBER_OF_DAYS}")
    print()

    transactions = generate_historical_data(
        start_date=START_DATE,
        number_of_days=NUMBER_OF_DAYS,
    )

    print(f"Transactions generated: {len(transactions)}")

    save_transactions_to_csv(
        transactions,
        OUTPUT_FILE,
    )

    print()
    print("Dataset saved successfully!")
    print(f"Location: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()