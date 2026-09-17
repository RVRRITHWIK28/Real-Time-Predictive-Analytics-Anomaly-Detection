from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_anomalies_collection,
    insert_anomaly,
)


client = create_mongo_client()

try:

    database = get_database(client)

    anomalies = get_anomalies_collection(
        database
    )

    anomaly = {
        "bucket": "2026-09-16T10:25:00+00:00",

        "anomaly_type": (
            "transaction_volume_spike"
        ),

        "current_count": 59,

        "baseline_count": 17.0,

        "ratio": 3.47,

        "is_anomaly": True,
    }

    document_id = insert_anomaly(
        anomalies,
        anomaly,
    )

    print(
        "Anomaly inserted successfully!"
    )

    print(
        f"Document ID: {document_id}"
    )

    retrieved = anomalies.find_one(
        {"_id": document_id}
    )

    print(
        "\nStored anomaly:"
    )

    print(retrieved)

finally:

    client.close()