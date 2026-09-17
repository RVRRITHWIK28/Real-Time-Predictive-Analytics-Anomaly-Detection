from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def cleanup_duplicates():

    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["anomalies"]

        pipeline = [
            {
                "$group": {
                    "_id": {
                        "timestamp": "$timestamp",
                        "bucket": "$bucket",
                        "anomaly_type": "$anomaly_type",
                        "entity_id": "$entity_id",
                    },
                    "documents": {
                        "$push": "$_id"
                    },
                    "count": {
                        "$sum": 1
                    },
                }
            },
            {
                "$match": {
                    "count": {
                        "$gt": 1
                    }
                }
            },
        ]

        duplicate_groups = list(
            collection.aggregate(pipeline)
        )

        print("=" * 60)
        print("ANOMALY DUPLICATE CLEANUP")
        print("=" * 60)

        print(
            f"Duplicate groups found: "
            f"{len(duplicate_groups)}"
        )

        total_deleted = 0

        for group in duplicate_groups:

            document_ids = group["documents"]

            # Keep the first document
            documents_to_delete = document_ids[1:]

            if documents_to_delete:

                result = collection.delete_many(
                    {
                        "_id": {
                            "$in": documents_to_delete
                        }
                    }
                )

                total_deleted += result.deleted_count

                print(
                    f"\nGroup: {group['_id']}"
                )

                print(
                    f"Documents before: "
                    f"{group['count']}"
                )

                print(
                    f"Deleted duplicates: "
                    f"{result.deleted_count}"
                )

        print("\n" + "=" * 60)
        print(
            f"Total duplicate documents deleted: "
            f"{total_deleted}"
        )
        print("=" * 60)

    finally:
        client.close()


if __name__ == "__main__":
    cleanup_duplicates()