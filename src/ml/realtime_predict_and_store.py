from src.ml.realtime_prediction import RealtimeDemandPredictor
from src.database.prediction_repository import PredictionRepository


class RealtimePredictionPersistence:

    def __init__(self):
        self.predictor = RealtimeDemandPredictor()
        self.repository = PredictionRepository()

    def predict_and_store(
        self,
        product_id,
        store_id,
        prediction_date
    ):
        """
        Generate a real-time demand prediction
        and store it in MongoDB.
        """

        # Generate prediction
        result = self.predictor.predict(
            product_id=product_id,
            store_id=store_id,
            prediction_date=prediction_date
        )

        # Save prediction to MongoDB
        mongo_id = self.repository.save_prediction(
            product_id=result["product_id"],
            store_id=result["store_id"],
            predicted_demand=result["predicted_demand"],
            prediction_date=prediction_date,
            model_version="1.0"
        )

        result["mongo_id"] = mongo_id

        return result

    def close(self):
        self.repository.close()


if __name__ == "__main__":

    service = RealtimePredictionPersistence()

    try:

        result = service.predict_and_store(
            product_id="P1001",
            store_id="S001",
            prediction_date="2026-10-01"
        )

        print("=" * 60)
        print("REAL-TIME PREDICTION + MONGODB TEST")
        print("=" * 60)

        print(f"Product          : {result['product_id']}")
        print(f"Store            : {result['store_id']}")
        print(f"Prediction date  : {result['prediction_date']}")
        print(
            f"Predicted demand : "
            f"{result['predicted_demand']} units"
        )
        print(f"MongoDB ID       : {result['mongo_id']}")

        print("\nPrediction successfully stored in MongoDB.")

        print("=" * 60)
        print("REAL-TIME PREDICTION + MONGODB TEST COMPLETE")
        print("=" * 60)

    finally:
        service.close()