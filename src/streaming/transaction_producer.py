import time

from src.ingestion.data_generator import generate_transaction
from src.streaming.producer import create_producer, send_transaction


def run_producer(interval_seconds=1):
    producer = create_producer()

    try:
        while True:
            event = generate_transaction()

            transaction = event.model_dump(mode="json")

            send_transaction(producer, transaction)

            print(
                f"Sent transaction: "
                f"{transaction['event_id']} | "
                f"Product: {transaction['product_id']} | "
                f"Revenue: Rs.{transaction['revenue']}"
            )

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nProducer stopped.")

    finally:
        producer.close()


if __name__ == "__main__":
    run_producer()