from src.streaming.consumer import (
    create_consumer,
    consume_transactions,
)

from src.processing.stream_processor import StreamAnalytics

from src.ml.anomaly_detector import (
    TransactionVolumeDetector,
)


def run_live_anomaly_detection():

    consumer = create_consumer()

    analytics = StreamAnalytics()

    detector = TransactionVolumeDetector(
        threshold=2.0,
        history_size=5,
    )

    print("Live anomaly detection started.")
    print("Waiting for transactions...\n")

    try:

        for transaction in consume_transactions(consumer):

            # Process incoming transaction
            analytics.process_transaction(
                transaction
            )

            # Get current 60-second metrics
            window = analytics.get_window_metrics()

            current_count = window["transactions"]

            # Detect anomaly
            result = detector.detect(
                current_count
            )

            print(
                f"\nTransaction: "
                f"{transaction['event_id']}"
            )

            print(
                f"Current 60-sec volume : "
                f"{current_count}"
            )

            print(
                f"Baseline volume       : "
                f"{result['baseline_count']}"
            )

            print(
                f"Ratio                  : "
                f"{result['ratio']}"
            )

            print(
                f"Anomaly                : "
                f"{result['is_anomaly']}"
            )

            print(
                f"Reason                 : "
                f"{result['reason']}"
            )

    except KeyboardInterrupt:

        print(
            "\nLive anomaly detection stopped."
        )

    finally:

        consumer.close()


if __name__ == "__main__":
    run_live_anomaly_detection()