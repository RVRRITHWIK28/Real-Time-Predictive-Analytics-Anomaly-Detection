from src.streaming.producer import create_producer, send_transaction
from src.database.mongodb import create_mongo_client, get_database


EVENT_ID = "evt_7c75b8bdcf45"


def replay_transaction():
    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["transactions"]

        transaction = collection.find_one(
            {"event_id": EVENT_ID},
            {"_id": 0}
        )

        if transaction is None:
            print(f"Transaction not found: {EVENT_ID}")
            return

        print(f"Replaying transaction: {EVENT_ID}")

        producer = create_producer()

        try:
            send_transaction(producer, transaction)

            print(
                f"Sent existing transaction to Kafka: "
                f"{transaction['event_id']}"
            )

        finally:
            producer.close()

    finally:
        client.close()


if __name__ == "__main__":
    replay_transaction()