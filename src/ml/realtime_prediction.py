from src.ml.realtime_features import RealtimeFeatureBuilder
from src.ml.prediction_service import DemandPredictionService


class RealtimeDemandPredictor:

    def __init__(self):
        self.feature_builder = RealtimeFeatureBuilder()
        self.prediction_service = DemandPredictionService()

    def predict(self, product_id, store_id, prediction_date):
        """
        Build real-time features and generate demand prediction.
        """

        # Step 1: Build features
        features = self.feature_builder.build_features(
            product_id=product_id,
            store_id=store_id,
            prediction_date=prediction_date
        )

        # Step 2: Generate prediction
        prediction_result = self.prediction_service.predict(features)

        return {
            "product_id": product_id,
            "store_id": store_id,
            "prediction_date": str(prediction_date),
            "predicted_demand": prediction_result[0]["predicted_demand"],
            "features": features
        }


if __name__ == "__main__":

    predictor = RealtimeDemandPredictor()

    result = predictor.predict(
        product_id="P1001",
        store_id="S001",
        prediction_date="2026-10-01"
    )

    print("=" * 60)
    print("REAL-TIME DEMAND PREDICTION TEST")
    print("=" * 60)

    print(f"Product          : {result['product_id']}")
    print(f"Store            : {result['store_id']}")
    print(f"Prediction date  : {result['prediction_date']}")
    print(
        f"Predicted demand : "
        f"{result['predicted_demand']} units"
    )

    print("\nFeatures used:")

    for key, value in result["features"].items():
        print(f"{key:20} : {value}")

    print("=" * 60)
    print("REAL-TIME DEMAND PREDICTION TEST COMPLETE")
    print("=" * 60)