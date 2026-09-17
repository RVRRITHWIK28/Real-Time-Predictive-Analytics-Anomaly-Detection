import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)


TEST_FILE = (
    "data/processed/test_data.csv"
)


def evaluate_baseline():

    # -----------------------------------------
    # Load test data
    # -----------------------------------------

    df = pd.read_csv(TEST_FILE)


    # -----------------------------------------
    # Actual demand
    # -----------------------------------------

    actual = df["demand"]


    # -----------------------------------------
    # Baseline prediction
    # -----------------------------------------
    # Predict today's demand using
    # yesterday's demand.

    predicted = df["lag_1"]


    # -----------------------------------------
    # Calculate MAE
    # -----------------------------------------

    mae = mean_absolute_error(
        actual,
        predicted,
    )


    # -----------------------------------------
    # Calculate RMSE
    # -----------------------------------------

    rmse = mean_squared_error(
        actual,
        predicted,
    ) ** 0.5


    # -----------------------------------------
    # Calculate MAPE
    # -----------------------------------------

    non_zero_actual = actual != 0

    mape = (
        (
            (
                actual[non_zero_actual]
                - predicted[non_zero_actual]
            ).abs()
            / actual[non_zero_actual]
        ).mean()
        * 100
    )


    return {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2),
    }


if __name__ == "__main__":

    results = evaluate_baseline()


    print("=" * 60)
    print("BASELINE MODEL EVALUATION")
    print("=" * 60)


    print(
        "\nPrediction strategy:"
    )

    print(
        "Today's demand = yesterday's demand"
    )


    print("\nEvaluation metrics:")


    print(
        f"MAE  : {results['MAE']}"
    )

    print(
        f"RMSE : {results['RMSE']}"
    )

    print(
        f"MAPE : {results['MAPE']}%"
    )


    print("\n" + "=" * 60)
    print(
        "BASELINE EVALUATION COMPLETE"
    )
    print("=" * 60)