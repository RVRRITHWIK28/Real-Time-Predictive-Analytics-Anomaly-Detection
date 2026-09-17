from datetime import datetime, timedelta

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

        # Days for which a prediction has already
        # been generated.
        self.predicted_days = set()

        # Days that have received streaming data
        # but have not yet reached the end of the day.
        self.pending_dates = set()

    def add_transaction(self, transaction):
        """
        Add a Kafka transaction to the minute-bucket processor.
        """

        return self.demand_pipeline.add_transaction(
            transaction
        )

    def process_completed_buckets(self, current_time):
        """
        Process completed minute buckets.

        Completed minutes update the daily demand tracker.

        A prediction is generated only after the
        complete event day has finished.
        """

        completed_results = (
            self.demand_pipeline.process_completed_buckets(
                current_time
            )
        )

        predictions = []

        # --------------------------------------------------
        # 1. Process newly completed minute buckets
        # --------------------------------------------------

        for result in completed_results:

            transactions = result["transactions"]

            if not transactions:
                continue

            event_dates = set()

            for transaction in transactions:

                timestamp = transaction["timestamp"]

                if isinstance(timestamp, str):
                    event_datetime = datetime.fromisoformat(
                        timestamp.replace("Z", "+00:00")
                    )
                else:
                    event_datetime = timestamp

                event_dates.add(
                    event_datetime.date()
                )

            # Remember these dates.
            #
            # The minute is complete, but the entire
            # day may still be running.
            self.pending_dates.update(
                event_dates
            )

        # --------------------------------------------------
        # 2. Check whether any pending day is complete
        # --------------------------------------------------

        for event_date in list(self.pending_dates):

            next_day = (
                event_date + timedelta(days=1)
            )

            # Midnight of the following day.
            day_end = datetime.combine(
                next_day,
                datetime.min.time()
            ).replace(
                tzinfo=current_time.tzinfo
            )

            # The entire day is not finished yet.
            if current_time < day_end:
                continue

            # Prevent duplicate predictions.
            if event_date in self.predicted_days:
                continue

            # --------------------------------------------------
            # 3. Get product/store combinations for
            #    the completed day
            # --------------------------------------------------

            tracker = (
                self.demand_pipeline.demand_tracker
            )

            daily_data = tracker.daily_demand.get(
                event_date.isoformat(),
                {}
            )

            combinations = set()

            for product_id, store_id in daily_data.keys():

                combinations.add(
                    (
                        product_id,
                        store_id
                    )
                )

            # --------------------------------------------------
            # 4. Predict the next day
            # --------------------------------------------------

            prediction_date = next_day.isoformat()

            for product_id, store_id in combinations:

                live_demand = (
                    self.demand_pipeline.get_daily_demand(
                        date=event_date,
                        product_id=product_id,
                        store_id=store_id
                    )
                )

                try:

                    prediction = self.predictor.predict(
                        product_id=product_id,
                        store_id=store_id,
                        prediction_date=prediction_date,
                        live_demand=live_demand
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
                    # Prediction cannot be generated yet,
                    # usually because there is insufficient
                    # historical data.
                    continue

            # --------------------------------------------------
            # 5. Mark this day as completed
            # --------------------------------------------------

            self.predicted_days.add(
                event_date
            )

            self.pending_dates.discard(
                event_date
            )

        return predictions

    def close(self):
        self.repository.close()


if __name__ == "__main__":

    pipeline = StreamingPredictionPipeline()

    try:

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

            pipeline.add_transaction(
                transaction
            )

        # --------------------------------------------------
        # TEST 1
        #
        # Minute is complete.
        # Entire day is NOT complete.
        #
        # Expected:
        # 0 predictions
        # --------------------------------------------------

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
            "\nTest 1 - Completed minute:"
        )

        print(
            f"Predictions generated: "
            f"{len(predictions)}"
        )

        # --------------------------------------------------
        # TEST 2
        #
        # September 30 has now finished.
        #
        # Expected:
        # 1 prediction for October 1
        # --------------------------------------------------

        current_time = datetime.fromisoformat(
            "2026-10-01T00:00:30+00:00"
        )

        predictions = (
            pipeline.process_completed_buckets(
                current_time
            )
        )

        print(
            "\nTest 2 - Completed day:"
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
                f"Prediction date  : "
                f"{prediction['prediction_date']}"
            )

            print(
                f"Predicted demand : "
                f"{prediction['predicted_demand']:.0f} units"
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