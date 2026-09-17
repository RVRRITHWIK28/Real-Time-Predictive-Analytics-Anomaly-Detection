import pandas as pd


INPUT_FILE = (
    "data/processed/ml_features.csv"
)


TRAIN_FILE = (
    "data/processed/train_data.csv"
)


TEST_FILE = (
    "data/processed/test_data.csv"
)


def create_train_test_data():

    # -----------------------------------------
    # Load feature dataset
    # -----------------------------------------

    df = pd.read_csv(INPUT_FILE)

    df["date"] = pd.to_datetime(
        df["date"]
    )


    # -----------------------------------------
    # Sort chronologically
    # -----------------------------------------

    df = df.sort_values(
        [
            "date",
            "product_id",
            "store_id",
        ]
    ).reset_index(drop=True)


    # -----------------------------------------
    # Determine split date
    # -----------------------------------------

    unique_dates = sorted(
        df["date"].unique()
    )

    split_index = int(
        len(unique_dates) * 0.70
    )

    split_date = unique_dates[
        split_index
    ]


    # -----------------------------------------
    # Time-based split
    # -----------------------------------------

    train_df = df[
        df["date"] < split_date
    ].copy()

    test_df = df[
        df["date"] >= split_date
    ].copy()


    # -----------------------------------------
    # Save datasets
    # -----------------------------------------

    train_df.to_csv(
        TRAIN_FILE,
        index=False,
    )

    test_df.to_csv(
        TEST_FILE,
        index=False,
    )


    return (
        train_df,
        test_df,
        split_date,
    )


if __name__ == "__main__":

    train_df, test_df, split_date = (
        create_train_test_data()
    )


    print("=" * 60)
    print("TRAIN / TEST SPLIT COMPLETE")
    print("=" * 60)


    print("\nSplit date:")
    print(split_date)


    print("\nTraining data:")
    print(
        "Rows:",
        len(train_df)
    )

    print(
        "Date range:",
        train_df["date"].min(),
        "to",
        train_df["date"].max(),
    )


    print("\nTesting data:")
    print(
        "Rows:",
        len(test_df)
    )

    print(
        "Date range:",
        test_df["date"].min(),
        "to",
        test_df["date"].max(),
    )


    print("\nTraining percentage:")
    print(
        round(
            len(train_df)
            / (len(train_df)
             + len(test_df))
            * 100,
            2,
        )
    )

    print("\nTesting percentage:")
    print(
        round(
            len(test_df)
            / (len(train_df)
             + len(test_df))
            * 100,
            2,
        )
    )



    print("\nSaved files:")
    print(TRAIN_FILE)
    print(TEST_FILE)


    print("\n" + "=" * 60)