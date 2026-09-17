from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

from src.database.mongodb import (
    create_mongo_client,
    get_database
)


PREDICTIONS_COLLECTION = "predictions"


class PredictionRepository:

    def __init__(self):
        # Create MongoDB client
        self.client = create_mongo_client()

        # Get retail_analytics database
        self.db = get_database(self.client)

        # Get predictions collection
        self.collection = self.db[PREDICTIONS_COLLECTION]

    def save_prediction(
        self,
        product_id,
        store_id,
        predicted_demand,
        prediction_date=None,
        model_version="1.0"
    ):
        """
        Save a demand prediction to MongoDB.

        If the prediction already exists, return the
        existing prediction ID instead of creating a duplicate.
        """

        if prediction_date is None:
            prediction_date = datetime.now(timezone.utc)

        document = {
            "product_id": product_id,
            "store_id": store_id,
            "predicted_demand": float(predicted_demand),
            "prediction_date": prediction_date,
            "model_version": model_version,
            "created_at": datetime.now(timezone.utc)
        }

        try:
            result = self.collection.insert_one(document)

            return str(result.inserted_id)

        except DuplicateKeyError:

            existing = self.collection.find_one(
                {
                    "product_id": product_id,
                    "store_id": store_id,
                    "prediction_date": prediction_date,
                    "model_version": model_version,
                }
            )

            if existing:
                return str(existing["_id"])

            raise


    def get_predictions(self, limit=10):
        """
        Retrieve the most recent predictions.
        """

        predictions = (
            self.collection
            .find({}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )

        return list(predictions)

    def close(self):
        """
        Close MongoDB connection.
        """

        self.client.close()