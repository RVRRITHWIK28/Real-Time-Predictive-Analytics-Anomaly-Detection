import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)
from sklearn.preprocessing import OneHotEncoder


TRAIN_FILE = (
    "data/processed/train_data.csv"
)

TEST_FILE = (
    "data/processed/test_data.csv"
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


def train_model():

    # -----------------------------------------
    # Load datasets
    # -----------------------------------------

    train_df = pd.read_csv(
        TRAIN_FILE
    )

    test_df = pd.read_csv(
        TEST_FILE
    )


    # -----------------------------------------
    # Separate features and target
    # -----------------------------------------

    X_train = train_df[FEATURES]

    y_train = train_df[TARGET]

    X_test = test_df[FEATURES]

    y_test = test_df[TARGET]


    # -----------------------------------------
    # Categorical features
    # -----------------------------------------

    categorical_features = [
        "product_id",
        "store_id",
        "category",
        "region",
    ]


    # -----------------------------------------
    # Numerical features
    # -----------------------------------------

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


    # -----------------------------------------
    # Preprocessing
    # -----------------------------------------

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


    # -----------------------------------------
    # Random Forest model
    # -----------------------------------------

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        n_jobs=-1,
    )


    # -----------------------------------------
    # Complete ML pipeline
    # -----------------------------------------

    from sklearn.pipeline import Pipeline

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


    # -----------------------------------------
    # Train
    # -----------------------------------------

    pipeline.fit(
        X_train,
        y_train,
    )


    # -----------------------------------------
    # Predict
    # -----------------------------------------

    predictions = pipeline.predict(
        X_test
    )


    # -----------------------------------------
    # Evaluation
    # -----------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = mean_squared_error(
        y_test,
        predictions,
    ) ** 0.5


    non_zero_actual = (
        y_test != 0
    )

    mape = (
        (
            (
                y_test[
                    non_zero_actual
                ]
                - predictions[
                    non_zero_actual
                ]
            ).abs()
            / y_test[
                non_zero_actual
            ]
        ).mean()
        * 100
    )


    return (
        pipeline,
        mae,
        rmse,
        mape,
    )


if __name__ == "__main__":

    (
        pipeline,
        mae,
        rmse,
        mape,
    ) = train_model()


    print(
        "=" * 60
    )

    print(
        "RANDOM FOREST DEMAND MODEL"
    )

    print(
        "=" * 60
    )


    print(
        "\nModel:"
    )

    print(
        "RandomForestRegressor"
    )


    print(
        "\nEvaluation metrics:"
    )


    print(
        f"MAE  : {mae:.2f}"
    )

    print(
        f"RMSE : {rmse:.2f}"
    )

    print(
        f"MAPE : {mape:.2f}%"
    )


    print(
        "\nBaseline comparison:"
    )

    print(
        "Baseline MAE  : 9.56"
    )

    print(
        "Baseline RMSE : 12.74"
    )

    print(
        "Baseline MAPE : 74.55%"
    )


    print(
        "\n" + "=" * 60
    )

    print(
        "MODEL TRAINING COMPLETE"
    )

    print(
        "=" * 60
    )