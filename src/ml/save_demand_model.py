import json
from datetime import datetime, timezone

import joblib
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

MODEL_FILE = (
    "models/demand_model.joblib"
)

METADATA_FILE = (
    "models/demand_model_metadata.json"
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


def train_and_save():

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
    # Prepare features and target
    # -----------------------------------------

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]


    # -----------------------------------------
    # Build model
    # -----------------------------------------

    pipeline = build_model()


    # -----------------------------------------
    # Train model
    # -----------------------------------------

    pipeline.fit(
        X_train,
        y_train,
    )


    # -----------------------------------------
    # Test model
    # -----------------------------------------

    predictions = pipeline.predict(
        X_test
    )


    # -----------------------------------------
    # Calculate metrics
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


    # -----------------------------------------
    # Save model
    # -----------------------------------------

    joblib.dump(
        pipeline,
        MODEL_FILE,
    )


    # -----------------------------------------
    # Save metadata
    # -----------------------------------------

    metadata = {
        "model_type": (
            "RandomForestRegressor"
        ),
        "target": TARGET,
        "features": FEATURES,
        "n_estimators": 200,
        "max_depth": 12,
        "random_state": 42,
        "training_rows": len(train_df),
        "testing_rows": len(test_df),
        "training_start": (
            train_df["date"].min()
        ),
        "training_end": (
            train_df["date"].max()
        ),
        "testing_start": (
            test_df["date"].min()
        ),
        "testing_end": (
            test_df["date"].max()
        ),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape": round(mape, 4),
        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    }


    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )


    return (
        pipeline,
        metadata,
    )


def verify_saved_model():

    # -----------------------------------------
    # Load saved model
    # -----------------------------------------

    loaded_model = joblib.load(
        MODEL_FILE
    )


    # -----------------------------------------
    # Load test data
    # -----------------------------------------

    test_df = pd.read_csv(
        TEST_FILE
    )

    X_test = test_df[FEATURES]


    # -----------------------------------------
    # Generate predictions
    # -----------------------------------------

    predictions = (
        loaded_model.predict(
            X_test
        )
    )


    return predictions


if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "TRAINING AND SAVING DEMAND MODEL"
    )

    print(
        "=" * 60
    )


    # Train and save

    (
        model,
        metadata,
    ) = train_and_save()


    print(
        "\nModel training complete."
    )


    print(
        "\nModel metrics:"
    )

    print(
        f"MAE  : {metadata['mae']}"
    )

    print(
        f"RMSE : {metadata['rmse']}"
    )

    print(
        f"MAPE : {metadata['mape']}%"
    )


    print(
        "\nModel saved to:"
    )

    print(
        MODEL_FILE
    )


    print(
        "\nMetadata saved to:"
    )

    print(
        METADATA_FILE
    )


    # Verify model can be loaded

    predictions = verify_saved_model()


    print(
        "\nSaved model reload test:"
    )

    print(
        "Prediction count:",
        len(predictions),
    )


    print(
        "First 5 predictions:"
    )

    print(
        predictions[:5]
    )


    print(
        "\n" + "=" * 60
    )

    print(
        "MODEL SAVE AND RELOAD VERIFICATION COMPLETE"
    )

    print(
        "=" * 60
    )