from src.streaming.consumer import (
    create_consumer,
    consume_transactions,
)

from src.processing.stream_processor import StreamAnalytics


def run_live_analytics():
    consumer = create_consumer()
    analytics = StreamAnalytics()

    print("Live analytics processor started.")
    print("Waiting for transactions...\n")

    try:
        for transaction in consume_transactions(consumer):
            analytics.process_transaction(transaction)

            overall = analytics.get_metrics()
            window = analytics.get_window_metrics()

            print(
                f"\nProcessed: {transaction['event_id']}"
            )

            print(
                f"TOTAL | "
                f"Transactions: {overall['total_transactions']} | "
                f"Units: {overall['total_quantity']} | "
                f"Revenue: Rs.{overall['total_revenue']} | "
                f"AOV: Rs.{overall['average_order_value']}"
            )

            print(
                f"LAST 60 SEC | "
                f"Transactions: {window['transactions']} | "
                f"Units: {window['quantity']} | "
                f"Revenue: Rs.{window['revenue']}"
            )

    except KeyboardInterrupt:
        print("\nLive analytics processor stopped.")

    finally:
        consumer.close()


if __name__ == "__main__":
    run_live_analytics()