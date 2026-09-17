from datetime import datetime, timezone

from src.streaming.consumer import (
    create_consumer,
    consume_transactions,
)

from src.ml.realtime_predict_and_store import (
    RealtimePredictionPersistence,
)


def run_ml_prediction_consumer():

    consumer = create_consumer()
    prediction_service = RealtimePredictionPersistence()

    print("=" * 60)
    print("KAFKA ML PREDICTION CONSUMER")
    print("=" * 60)

    print("Kafka consumer started.")
    print("Waiting for transactions...")

    processed_count = 0

    try:

        for transaction in consume_transactions(consumer):

            processed_count += 1

            print(
                f"Received transaction #{processed_count}: "
                f"{transaction['event_id']} | "
                f"Product: {transaction['product_id']} | "
                f"Store: {transaction['store_id']} | "
                f"Quantity: {transaction['quantity']}"
            )

            # For this first integration test,
            # trigger a prediction after receiving
            # the first transaction.
            if processed_count == 1:

                product_id = transaction["product_id"]
                store_id = transaction["store_id"]

                prediction_date = (
                    datetime.now(timezone.utc)
                    .date()
                )

                result = prediction_service.predict_and_store(
                    product_id=product_id,
                    store_id=store_id,
                    prediction_date=str(prediction_date)
                )

                print("\nML prediction generated:")
                print(
                    f"Product          : "
                    f"{result['product_id']}"
                )
                print(
                    f"Store            : "
                    f"{result['store_id']}"
                )
                print(
                    f"Predicted demand : "
                    f"{result['predicted_demand']} units"
                )
                print(
                    f"MongoDB ID       : "
                    f"{result['mongo_id']}"
                )

                print(
                    "\nKafka → ML → MongoDB "
                    "integration successful."
                )

                break

    except KeyboardInterrupt:

        print("\nConsumer stopped.")

    finally:

        consumer.close()
        prediction_service.close()


if __name__ == "__main__":
    run_ml_prediction_consumer()