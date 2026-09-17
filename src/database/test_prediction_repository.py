from src.database.prediction_repository import PredictionRepository


def main():

    repository = PredictionRepository()

    prediction_id = repository.save_prediction(
        product_id="P1001",
        store_id="S001",
        predicted_demand=58.85
    )

    print("=" * 60)
    print("PREDICTION REPOSITORY TEST")
    print("=" * 60)

    print(f"Prediction saved successfully.")
    print(f"MongoDB ID: {prediction_id}")

    predictions = repository.get_predictions(limit=5)

    print("\nRecent predictions:")

    for prediction in predictions:
        print(prediction)

    print("=" * 60)
    print("PREDICTION REPOSITORY TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()