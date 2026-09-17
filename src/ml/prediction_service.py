from pathlib import Path

import joblib
import pandas as pd


class DemandPredictionService:

    def __init__(self, model_path="models/demand_model.joblib"):
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.model = joblib.load(self.model_path)

    def predict(self, input_data):
        """
        Predict product demand using the saved ML model.
        """

        # Convert dictionary to DataFrame
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])

        # Convert list of dictionaries to DataFrame
        elif isinstance(input_data, list):
            input_data = pd.DataFrame(input_data)

        # Make sure input is a DataFrame
        elif not isinstance(input_data, pd.DataFrame):
            raise TypeError(
                "input_data must be a dictionary, list of dictionaries, "
                "or pandas DataFrame."
            )

        # Required features
        required_features = [
            "product_id",
            "store_id",
            "category",
            "region",
            "day_of_week",
            "day_of_month",
            "week_of_year",
            "is_weekend",
            "lag_1",
            "lag_2",
            "lag_7",
            "rolling_mean_7",
        ]

        # Check for missing features
        missing_features = [
            feature
            for feature in required_features
            if feature not in input_data.columns
        ]

        if missing_features:
            raise ValueError(
                f"Missing required features: {missing_features}"
            )

        # Generate prediction
        predictions = self.model.predict(input_data)

        # Return structured response
        results = []

        for index, prediction in enumerate(predictions):
            results.append({
                "product_id": input_data.iloc[index]["product_id"],
                "store_id": input_data.iloc[index]["store_id"],
                "predicted_demand": round(float(prediction), 2)
            })

        return results


if __name__ == "__main__":

    service = DemandPredictionService()

    sample_input = {
        "product_id": "P1001",
        "store_id": "S001",
        "category": "Electronics",
        "region": "South",
        "day_of_week": 2,
        "day_of_month": 1,
        "week_of_year": 40,
        "is_weekend": 0,
        "lag_1": 65,
        "lag_2": 62,
        "lag_7": 58,
        "rolling_mean_7": 61.5,
    }

    result = service.predict(sample_input)

    print("=" * 60)
    print("STRUCTURED DEMAND PREDICTION SERVICE TEST")
    print("=" * 60)

    print(f"Product : {result[0]['product_id']}")
    print(f"Store   : {result[0]['store_id']}")
    print(
        f"Predicted demand: "
        f"{result[0]['predicted_demand']} units"
    )

    print("\nComplete prediction response:")
    print(result)

    print("=" * 60)
    print("STRUCTURED PREDICTION TEST COMPLETE")
    print("=" * 60)