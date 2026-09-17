import pandas as pd


INPUT_FILE = (
    "data/processed/daily_product_demand.csv"
)

OUTPUT_FILE = (
    "data/processed/ml_features.csv"
)


def create_features():

    # -----------------------------------------
    # Load dataset
    # -----------------------------------------

    df = pd.read_csv(INPUT_FILE)

    df["date"] = pd.to_datetime(
        df["date"]
    )


    # -----------------------------------------
    # Create complete date range
    # -----------------------------------------

    dates = pd.date_range(
        start=df["date"].min(),
        end=df["date"].max(),
        freq="D",
    )


    # -----------------------------------------
    # Get unique products and stores
    # -----------------------------------------

    products = df["product_id"].unique()

    stores = df["store_id"].unique()


    # -----------------------------------------
    # Create complete product-store-date grid
    # -----------------------------------------

    complete_grid = pd.MultiIndex.from_product(
        [
            dates,
            products,
            stores,
        ],
        names=[
            "date",
            "product_id",
            "store_id",
        ],
    ).to_frame(index=False)


    # -----------------------------------------
    # Add category and region information
    # -----------------------------------------

    product_info = (
        df[
            [
                "product_id",
                "category",
            ]
        ]
        .drop_duplicates()
    )

    store_info = (
        df[
            [
                "store_id",
                "region",
            ]
        ]
        .drop_duplicates()
    )


    complete_grid = complete_grid.merge(
        product_info,
        on="product_id",
        how="left",
    )

    complete_grid = complete_grid.merge(
        store_info,
        on="store_id",
        how="left",
    )


    # -----------------------------------------
    # Merge actual demand and revenue
    # -----------------------------------------

    complete_grid = complete_grid.merge(
        df[
            [
                "date",
                "product_id",
                "store_id",
                "demand",
                "revenue",
            ]
        ],
        on=[
            "date",
            "product_id",
            "store_id",
        ],
        how="left",
    )


    # -----------------------------------------
    # Fill missing sales with zero
    # -----------------------------------------

    complete_grid["demand"] = (
        complete_grid["demand"]
        .fillna(0)
    )

    complete_grid["revenue"] = (
        complete_grid["revenue"]
        .fillna(0)
    )


    # -----------------------------------------
    # Sort before creating lag features
    # -----------------------------------------

    complete_grid = complete_grid.sort_values(
        [
            "product_id",
            "store_id",
            "date",
        ]
    )


    # -----------------------------------------
    # Calendar features
    # -----------------------------------------

    complete_grid["day_of_week"] = (
        complete_grid["date"].dt.dayofweek
    )

    complete_grid["day_of_month"] = (
        complete_grid["date"].dt.day
    )

    complete_grid["week_of_year"] = (
        complete_grid["date"].dt.isocalendar().week
        .astype(int)
    )

    complete_grid["is_weekend"] = (
        complete_grid["day_of_week"] >= 5
    ).astype(int)


    # -----------------------------------------
    # Lag features
    # -----------------------------------------

    grouped = complete_grid.groupby(
        [
            "product_id",
            "store_id",
        ]
    )["demand"]

    complete_grid["lag_1"] = (
        grouped.shift(1)
    )

    complete_grid["lag_2"] = (
        grouped.shift(2)
    )

    complete_grid["lag_7"] = (
        grouped.shift(7)
    )


    # -----------------------------------------
    # Rolling demand
    # -----------------------------------------

    complete_grid["rolling_mean_7"] = (
        complete_grid.groupby(
            [
                "product_id",
                "store_id",
            ]
        )["demand"]
        .transform(
            lambda x: x.shift(1).rolling(7).mean()
        )
    )

    # -----------------------------------------
    # Remove rows without enough history
    # -----------------------------------------

    complete_grid = complete_grid.dropna(
        subset=[
            "lag_1",
            "lag_2",
            "lag_7",
            "rolling_mean_7",
        ]
    )


    # -----------------------------------------
    # Save feature dataset
    # -----------------------------------------

    complete_grid.to_csv(
        OUTPUT_FILE,
        index=False,
    )


    return complete_grid


if __name__ == "__main__":

    features = create_features()


    print("=" * 60)
    print("ML FEATURE ENGINEERING COMPLETE")
    print("=" * 60)


    print("\nDataset shape:")
    print(features.shape)


    print("\nColumns:")
    print(features.columns.tolist())


    print("\nFirst 10 rows:")
    print(features.head(10))


    print("\nMissing values:")
    print(features.isnull().sum())


    print("\nDate range:")
    print(
        features["date"].min(),
        "to",
        features["date"].max(),
    )


    print("\nSaved to:")
    print(OUTPUT_FILE)


    print("\n" + "=" * 60)