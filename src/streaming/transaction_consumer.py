from pymongo.errors import DuplicateKeyError

from src.streaming.consumer import (
    create_consumer,
    consume_transactions,
)

from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def run_consumer():
    consumer = create_consumer()

    client = create_mongo_client()
    database = get_database(client)
    collection = database["transactions"]

    print("Transaction consumer started.")
    print("Waiting for transactions...")

    inserted_count = 0
    duplicate_count = 0

    try:
        for transaction in consume_transactions(consumer):

            try:
                collection.insert_one(transaction)
                inserted_count += 1

                print(
                    f"Inserted transaction: "
                    f"{transaction['event_id']} | "
                    f"Product: {transaction['product_id']} | "
                    f"Revenue: Rs.{transaction['revenue']}"
                )

            except DuplicateKeyError:
                duplicate_count += 1

                print(
                    f"Duplicate skipped: "
                    f"{transaction['event_id']}"
                )

    except KeyboardInterrupt:
        print("\nConsumer stopped.")

    finally:
        consumer.close()
        client.close()

        print("\nConsumer summary:")
        print(f"Inserted: {inserted_count}")
        print(f"Duplicates skipped: {duplicate_count}")


if __name__ == "__main__":
    run_consumer()