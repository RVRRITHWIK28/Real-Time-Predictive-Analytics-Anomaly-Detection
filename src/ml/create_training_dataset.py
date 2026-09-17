import pandas as pd


INPUT_FILE = "data/raw/historical_transactions.csv"

OUTPUT_FILE = (
    "data/processed/daily_product_demand.csv"
)


def create_training_dataset():

    # Load transaction data
    df = pd.read_csv(INPUT_FILE)

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    # Extract date
    df["date"] = df["timestamp"].dt.date

    # Aggregate transactions
    training_df = (
        df.groupby(
            [
                "date",
                "product_id",
                "store_id",
                "category",
                "region",
            ],
            as_index=False,
        )
        .agg(
            demand=("quantity", "sum"),
            revenue=("revenue", "sum"),
        )
    )

    # Sort the dataset
    training_df = training_df.sort_values(
        [
            "date",
            "product_id",
            "store_id",
        ]
    )

    # Save dataset
    training_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    return training_df


if __name__ == "__main__":

    training_df = create_training_dataset()

    print("=" * 60)
    print("ML TRAINING DATASET CREATED")
    print("=" * 60)

    print("\nDataset shape:")
    print(training_df.shape)

    print("\nColumns:")
    print(training_df.columns.tolist())

    print("\nFirst 10 rows:")
    print(training_df.head(10))

    print("\nDate range:")
    print(
        training_df["date"].min(),
        "to",
        training_df["date"].max(),
    )

    print("\nTotal demand:")
    print(training_df["demand"].sum())

    print("\nTotal revenue:")
    print(
        round(
            training_df["revenue"].sum(),
            2,
        )
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print("\n" + "=" * 60)
    print("TRAINING DATASET CREATION COMPLETE")
    print("=" * 60)