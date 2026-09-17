from src.streaming.consumer import (
    create_consumer,
    consume_transactions,
)

from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_transactions_collection,
    insert_transaction,
)


def run_consumer():
    kafka_consumer = create_consumer()

    mongo_client = create_mongo_client()
    database = get_database(mongo_client)
    transactions_collection = get_transactions_collection(database)

    print("Kafka → MongoDB consumer started.")
    print("Waiting for transactions...")

    try:
        for transaction in consume_transactions(kafka_consumer):

            insert_transaction(
                transactions_collection,
                transaction,
            )

            print(
                f"Stored transaction: "
                f"{transaction['event_id']} | "
                f"Product: {transaction['product_id']} | "
                f"Revenue: Rs.{transaction['revenue']}"
            )

    except KeyboardInterrupt:
        print("\nKafka → MongoDB consumer stopped.")

    finally:
        kafka_consumer.close()
        mongo_client.close()


if __name__ == "__main__":
    run_consumer()