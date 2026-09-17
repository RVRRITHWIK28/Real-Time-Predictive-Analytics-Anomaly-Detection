from collections import Counter

from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def audit_anomalies():

    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["anomalies"]

        total = collection.count_documents({})

        print("=" * 60)
        print("ANOMALY COLLECTION AUDIT")
        print("=" * 60)

        print(f"Total anomaly documents: {total}")

        # ---------------------------------
        # Documents with production fields
        # ---------------------------------

        production_filter = {
            "entity_id": {"$exists": True},
            "severity": {"$exists": True},
            "reason": {"$exists": True},
        }

        production_count = collection.count_documents(
            production_filter
        )

        print(
            f"Production-style documents: "
            f"{production_count}"
        )

        # ---------------------------------
        # Older/test documents
        # ---------------------------------

        old_filter = {
            "$or": [
                {"entity_id": {"$exists": False}},
                {"severity": {"$exists": False}},
                {"reason": {"$exists": False}},
            ]
        }

        old_count = collection.count_documents(
            old_filter
        )

        print(
            f"Older/test-style documents: "
            f"{old_count}"
        )

        # ---------------------------------
        # Anomaly types
        # ---------------------------------

        anomaly_types = collection.distinct(
            "anomaly_type"
        )

        print("\nAnomaly types:")

        for anomaly_type in sorted(
            str(value)
            for value in anomaly_types
        ):
            count = collection.count_documents(
                {"anomaly_type": anomaly_type}
            )

            print(
                f"  {anomaly_type}: {count}"
            )

        # ---------------------------------
        # Production documents
        # ---------------------------------

        print("\nProduction-style anomaly records:")

        cursor = collection.find(
            production_filter,
            {
                "_id": 0,
                "timestamp": 1,
                "bucket": 1,
                "anomaly_type": 1,
                "entity_id": 1,
                "severity": 1,
                "ratio": 1,
            }
        ).sort(
            "timestamp",
            -1
        ).limit(20)

        for document in cursor:
            print(document)

        # ---------------------------------
        # Possible duplicates
        # ---------------------------------

        print("\nPossible duplicate groups:")

        pipeline = [
            {
                "$match": production_filter
            },
            {
                "$group": {
                    "_id": {
                        "timestamp": "$timestamp",
                        "bucket": "$bucket",
                        "anomaly_type": "$anomaly_type",
                        "entity_id": "$entity_id",
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
    audit_anomalies()