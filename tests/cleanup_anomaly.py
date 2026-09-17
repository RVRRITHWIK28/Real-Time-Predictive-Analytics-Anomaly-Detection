from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_anomalies_collection,
)


client = create_mongo_client()

try:

    database = get_database(client)

    anomalies = get_anomalies_collection(
        database
    )

    result = anomalies.delete_many(
        {
            "bucket": "2026-09-16T10:25:00+00:00",
            "anomaly_type": (
                "transaction_volume_spike"
            ),
        }
    )

    print(
        f"Test anomalies removed: "
        f"{result.deleted_count}"
    )

finally:

    client.close()