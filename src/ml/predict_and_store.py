from src.ml.prediction_service import DemandPredictionService
from src.database.prediction_repository import PredictionRepository


def predict_and_store(input_data):
    """
    Generate a demand prediction and store it in MongoDB.
    """

    # Load ML prediction service
    prediction_service = DemandPredictionService()

    # Create MongoDB repository
    repository = PredictionRepository()

    # Generate prediction
    prediction_result = prediction_service.predict(input_data)

    saved_predictions = []

    # Store each prediction
    for prediction in prediction_result:

        prediction_id = repository.save_prediction(
            product_id=prediction["product_id"],
            store_id=prediction["store_id"],
            predicted_demand=prediction["predicted_demand"]
        )

        saved_predictions.append({
            **prediction,
            "mongo_id": prediction_id
        })

    # Close MongoDB connection
    repository.close()

    return saved_predictions


if __name__ == "__main__":

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

    result = predict_and_store(sample_input)

    print("=" * 60)
    print("PREDICT AND STORE TEST")
    print("=" * 60)

    for prediction in result:
        print(f"Product          : {prediction['product_id']}")
        print(f"Store            : {prediction['store_id']}")
        print(
            f"Predicted demand : "
            f"{prediction['predicted_demand']} units"
        )
        print(f"MongoDB ID       : {prediction['mongo_id']}")

    print("=" * 60)
    print("PREDICT AND STORE TEST COMPLETE")
    print("=" * 60)