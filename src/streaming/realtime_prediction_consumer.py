from datetime import datetime, timezone

from src.streaming.consumer import (
    create_consumer,
    consume_transactions,
)

from src.processing.streaming_prediction_pipeline import (
    StreamingPredictionPipeline,
)


# Required fields for a valid transaction
REQUIRED_FIELDS = {
    "event_id",
    "timestamp",
    "product_id",
    "store_id",
    "quantity",
    "revenue",
}


def validate_transaction(transaction):
    """
    Check whether the Kafka transaction contains
    all fields required by the prediction pipeline.
    """

    return REQUIRED_FIELDS - transaction.keys()


def run_realtime_prediction_consumer():

    consumer = create_consumer(
        group_id="prediction-group"
    )

    pipeline = StreamingPredictionPipeline()

    print("=" * 60)
    print("REAL-TIME KAFKA → ML PREDICTION PIPELINE")
    print("=" * 60)

    print("Kafka consumer started.")
    print("Waiting for transactions...")

    try:

        for transaction in consume_transactions(
            consumer
        ):

            # --------------------------------------------------
            # 1. Validate incoming Kafka transaction
            # --------------------------------------------------

            missing_fields = validate_transaction(
                transaction
            )

            if missing_fields:

                print(
                    f"WARNING: Invalid transaction skipped | "
                    f"Event: {transaction.get('event_id', 'unknown')} | "
                    f"Missing fields: "
                    f"{sorted(missing_fields)}"
                )

                continue

            try:

                # --------------------------------------------------
                # 2. Add transaction to completed-bucket processor
                # --------------------------------------------------

                bucket = pipeline.add_transaction(
                    transaction
                )

                print(
                    f"Received: "
                    f"{transaction['event_id']} | "
                    f"Product: {transaction['product_id']} | "
                    f"Store: {transaction['store_id']} | "
                    f"Quantity: {transaction['quantity']} | "
                    f"Bucket: {bucket}"
                )

                # --------------------------------------------------
                # 3. Process completed minute buckets
                # --------------------------------------------------

                current_time = datetime.now(
                    timezone.utc
                )

                predictions = (
                    pipeline.process_completed_buckets(
                        current_time
                    )
                )

                # --------------------------------------------------
                # 4. Display generated predictions
                # --------------------------------------------------

                for prediction in predictions:

                    print("\n" + "-" * 60)
                    print("NEW ML PREDICTION")
                    print("-" * 60)

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

                    print("-" * 60)

            except Exception as error:

                print(
                    f"ERROR processing transaction "
                    f"{transaction.get('event_id', 'unknown')}: "
                    f"{error}"
                )

                continue

    except KeyboardInterrupt:

        print(
            "\nStopping real-time prediction consumer..."
        )

    finally:

        consumer.close()
        pipeline.close()

        print(
            "Real-time prediction consumer stopped."
        )


if __name__ == "__main__":
    run_realtime_prediction_consumer()