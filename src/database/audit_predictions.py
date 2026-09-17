from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def audit_predictions():

    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["predictions"]

        total = collection.count_documents({})

        print("=" * 60)
        print("PREDICTION COLLECTION AUDIT")
        print("=" * 60)

        print(f"Total prediction documents: {total}")

        # Show all predictions
        print("\nPrediction records:")

        cursor = collection.find(
            {},
            {
                "_id": 0,
                "product_id": 1,
                "store_id": 1,
                "prediction_date": 1,
                "predicted_demand": 1,
                "model_version": 1,
                "created_at": 1,
            }
        ).sort(
            "prediction_date",
            1
        )

        for document in cursor:
            print(document)

        # Find duplicate prediction identities
        print("\nPossible duplicate groups:")

        pipeline = [
            {
                "$group": {
                    "_id": {
                        "product_id": "$product_id",
                        "store_id": "$store_id",
                        "prediction_date": "$prediction_date",
                        "model_version": "$model_version",
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
            {
                "$sort": {
                    "count": -1
                }
            },
        ]

        duplicates = list(
            collection.aggregate(pipeline)
        )

        if duplicates:

            for duplicate in duplicates:

                print(
                    f"  {duplicate['_id']} "
                    f"→ {duplicate['count']} documents"
                )

        else:

            print("  No duplicate groups found.")

        print("=" * 60)
        print("AUDIT COMPLETE")
        print("=" * 60)

    finally:
        client.close()


if __name__ == "__main__":
    audit_predictions()