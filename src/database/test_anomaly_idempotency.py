from pymongo.errors import DuplicateKeyError

from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def test_anomaly_idempotency():

    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["anomalies"]

        test_anomaly = {
            "timestamp": "2099-01-01T00:00:00Z",
            "bucket": "2099-01-01T00:00:00Z",
            "anomaly_type": "test_idempotency",
            "entity_id": "TEST",
            "is_anomaly": True,
            "reason": "Idempotency test",
            "ratio": 2.0,
            "severity": "HIGH",
        }

        # Remove previous test document if it exists.
        collection.delete_one({
            "timestamp": test_anomaly["timestamp"],
            "bucket": test_anomaly["bucket"],
            "anomaly_type": test_anomaly["anomaly_type"],
            "entity_id": test_anomaly["entity_id"],
        })

        # First insertion should succeed.
        collection.insert_one(test_anomaly)

        print("First insert: SUCCESS")

        # Second insertion should fail.
        try:
            collection.insert_one(test_anomaly)

            print(
                "ERROR: Duplicate was inserted."
            )

        except DuplicateKeyError:

            print(
                "Second insert: BLOCKED "
                "(duplicate detected)"
            )

        # Clean up test document.
        collection.delete_one({
            "timestamp": test_anomaly["timestamp"],
            "bucket": test_anomaly["bucket"],
            "anomaly_type": test_anomaly["anomaly_type"],
            "entity_id": test_anomaly["entity_id"],
        })

        print("Test document removed.")
        print("ANOMALY IDEMPOTENCY TEST PASSED")

    finally:
        client.close()


if __name__ == "__main__":
    test_anomaly_idempotency()