from datetime import datetime, timezone

from src.processing.completed_bucket_demand import (
    CompletedBucketDemandPipeline,
)

from src.ml.realtime_prediction import (
    RealtimeDemandPredictor,
)

from src.database.prediction_repository import (
    PredictionRepository,
)


class StreamingPredictionPipeline:

    def __init__(self):

        self.demand_pipeline = (
            CompletedBucketDemandPipeline()
        )

        self.predictor = RealtimeDemandPredictor()

        self.repository = PredictionRepository()

    def add_transaction(self, transaction):
        """
        Add a Kafka transaction to the completed-bucket processor.
        """

        return self.demand_pipeline.add_transaction(
            transaction
        )

    def process_completed_buckets(self, current_time):
        """
        Process completed minute buckets and generate
        predictions when sufficient historical data exists.
        """

        completed_results = (
            self.demand_pipeline.process_completed_buckets(
                current_time
            )
        )

        predictions = []

        for result in completed_results:

            transactions = result["transactions"]

            if not transactions:
                continue

            # Find product/store combinations present
            # in this completed bucket.
            combinations = set()

            for transaction in transactions:

                combinations.add(
                    (
                        transaction["product_id"],
                        transaction["store_id"]
                    )
                )

            for product_id, store_id in combinations:

                # Current calendar date
                prediction_date = (
                    datetime.now(timezone.utc)
                    .date()
                    .isoformat()
                )

                try:

                    prediction = self.predictor.predict(
                        product_id=product_id,
                        store_id=store_id,
                        prediction_date=prediction_date
                    )

                    prediction_id = (
                        self.repository.save_prediction(
                            product_id=product_id,
                            store_id=store_id,
                            predicted_demand=(
                                prediction[
                                    "predicted_demand"
                                ]
                            ),
                            prediction_date=(
                                datetime.fromisoformat(
                                    prediction_date
                                )
                            ),
                            model_version="1.0"
                        )
                    )

                    predictions.append({
                        "product_id": product_id,
                        "store_id": store_id,
                        "prediction_date": prediction_date,
                        "predicted_demand": (
                            prediction[
                                "predicted_demand"
                            ]
                        ),
                        "mongo_id": prediction_id
                    })

                except ValueError:
                    # Not enough historical data.
                    # Prediction will become available
                    # once sufficient history exists.
                    continue

        return predictions

    def close(self):
        self.repository.close()


if __name__ == "__main__":

    pipeline = StreamingPredictionPipeline()

    try:

        # Simulate transactions arriving from Kafka.
        transactions = [
            {
                "event_id": "evt_001",
                "timestamp": (
                    "2026-09-30T10:01:15+00:00"
                ),
                "product_id": "P1001",
                "store_id": "S001",
                "quantity": 3,
                "revenue": 3000
            },
            {
                "event_id": "evt_002",
                "timestamp": (
                    "2026-09-30T10:01:40+00:00"
                ),
                "product_id": "P1001",
                "store_id": "S001",
                "quantity": 5,
                "revenue": 5000
            }
        ]

        for transaction in transactions:
            pipeline.add_transaction(transaction)

        # The 10:01 bucket becomes complete
        # at 10:02.
        current_time = datetime.fromisoformat(
            "2026-09-30T10:02:30+00:00"
        )

        predictions = (
            pipeline.process_completed_buckets(
                current_time
            )
        )

        print("=" * 60)
        print("STREAMING PREDICTION PIPELINE TEST")
        print("=" * 60)

        print(
            f"\nCompleted bucket processed."
        )

        print(
            f"Predictions generated: "
            f"{len(predictions)}"
        )

        for prediction in predictions:

            print("\nPrediction:")

            print(
                f"Product          : "
                f"{prediction['product_id']}"
            )

            print(
                f"Store            : "
                f"{prediction['store_id']}"
            )

            print(
                f"Predicted demand : "
                f"{prediction['predicted_demand']} units"
            )

            print(
                f"MongoDB ID       : "
                f"{prediction['mongo_id']}"
            )

        print("=" * 60)
        print(
            "STREAMING PREDICTION PIPELINE TEST COMPLETE"
        )
        print("=" * 60)

    finally:

        pipeline.close()