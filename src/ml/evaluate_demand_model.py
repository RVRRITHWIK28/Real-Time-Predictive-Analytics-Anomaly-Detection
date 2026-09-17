import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


TRAIN_FILE = (
    "data/processed/train_data.csv"
)

TEST_FILE = (
    "data/processed/test_data.csv"
)

PREDICTIONS_FILE = (
    "data/processed/demand_predictions.csv"
)


FEATURES = [
    "day_of_week",
    "day_of_month",
    "week_of_year",
    "is_weekend",
    "lag_1",
    "lag_2",
    "lag_7",
    "rolling_mean_7",
    "product_id",
    "store_id",
    "category",
    "region",
]

TARGET = "demand"


def build_model():

    categorical_features = [
        "product_id",
        "store_id",
        "category",
        "region",
    ]

    numerical_features = [
        "day_of_week",
        "day_of_month",
        "week_of_year",
        "is_weekend",
        "lag_1",
        "lag_2",
        "lag_7",
        "rolling_mean_7",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
            (
                "numerical",
                "passthrough",
                numerical_features,
            ),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "model",
                model,
            ),
        ]
    )

    return pipeline


def evaluate_model():

    # -----------------------------------------
    # Load data
    # -----------------------------------------

    train_df = pd.read_csv(
        TRAIN_FILE
    )

    test_df = pd.read_csv(
        TEST_FILE
    )


    # -----------------------------------------
    # Prepare data
    # -----------------------------------------

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]


    # -----------------------------------------
    # Build and train model
    # -----------------------------------------

    pipeline = build_model()

    pipeline.fit(
        X_train,
        y_train,
    )


    # -----------------------------------------
    # Generate predictions
    # -----------------------------------------

    predictions = pipeline.predict(
        X_test
    )


    # -----------------------------------------
    # Create prediction report
    # -----------------------------------------

    prediction_df = test_df[
        [
            "date",
            "product_id",
            "store_id",
            "category",
            "region",
            "demand",
        ]
    ].copy()

    prediction_df[
        "predicted_demand"
    ] = predictions

    prediction_df[
        "absolute_error"
    ] = (
        prediction_df["demand"]
        - prediction_df["predicted_demand"]
    ).abs()


    # -----------------------------------------
    # Calculate percentage error
    # -----------------------------------------

    prediction_df[
        "percentage_error"
    ] = 0.0

    non_zero = (
        prediction_df["demand"] != 0
    )

    prediction_df.loc[
        non_zero,
        "percentage_error",
    ] = (
        prediction_df.loc[
            non_zero,
            "absolute_error",
        ]
        / prediction_df.loc[
            non_zero,
            "demand",
        ]
        * 100
    )


    # -----------------------------------------
    # Save predictions
    # -----------------------------------------

    prediction_df.to_csv(
        PREDICTIONS_FILE,
        index=False,
    )


    # -----------------------------------------
    # Metrics
    # -----------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5


    # -----------------------------------------
    # Feature importance
    # -----------------------------------------

    preprocessor = (
        pipeline.named_steps[
            "preprocessor"
        ]
    )

    model = (
        pipeline.named_steps[
            "model"
        ]
    )

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    importance_df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": model.feature_importances_,
        }
    )

    importance_df = (
        importance_df
        .sort_values(
            "importance",
            ascending=False,
        )
        .reset_index(drop=True)
    )


    return (
        prediction_df,
        mae,
        rmse,
        importance_df,
    )


if __name__ == "__main__":

    (
        predictions,
        mae,
        rmse,
        importance_df,
    ) = evaluate_model()


    print("=" * 60)
    print("DEMAND MODEL DETAILED EVALUATION")
    print("=" * 60)


    print("\nMAE:")
    print(
        round(mae, 2)
    )


    print("\nRMSE:")
    print(
        round(rmse, 2)
    )


    print("\nFirst 10 predictions:")

    print(
        predictions[
            [
                "date",
                "product_id",
                "store_id",
                "demand",
                "predicted_demand",
                "absolute_error",
            ]
        ].head(10)
    )


    print(
        "\nLargest prediction errors:"
    )

    print(
        predictions[
            [
                "date",
                "product_id",
                "store_id",
                "demand",
                "predicted_demand",
                "absolute_error",
            ]
        ]
        .sort_values(
            "absolute_error",
            ascending=False,
        )
        .head(10)
    )


    print(
        "\nTop 15 important features:"
    )

    print(
        importance_df.head(15)
    )


    print(
        "\nPredictions saved to:"
    )

    print(
        PREDICTIONS_FILE
    )


    print(
        "\n" + "=" * 60
    )

    print(
        "DETAILED EVALUATION COMPLETE"
    )

    print(
        "=" * 60
    )