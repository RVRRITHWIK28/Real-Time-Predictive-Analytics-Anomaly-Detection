from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def cleanup_anomalies():

    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["anomalies"]

        old_filter = {
            "$or": [
                {"entity_id": {"$exists": False}},
                {"severity": {"$exists": False}},
                {"reason": {"$exists": False}},
            ]
        }

        old_documents = list(
            collection.find(
                old_filter,
                {
                    "_id": 1,
                    "anomaly_type": 1,
                    "timestamp": 1,
                    "bucket": 1,
                }
            )
        )

        print("=" * 60)
        print("OLD / TEST ANOMALY RECORDS")
        print("=" * 60)

        print(f"Records found: {len(old_documents)}")

        for document in old_documents:
            print(document)

        if not old_documents:
            print("No old/test records found.")
            return

        print("\nDeleting old/test records...")

        result = collection.delete_many(old_filter)

        print(
            f"Deleted: {result.deleted_count}"
        )

        print("=" * 60)
        print("CLEANUP COMPLETE")
        print("=" * 60)

    finally:
        client.close()


if __name__ == "__main__":
    cleanup_anomalies()