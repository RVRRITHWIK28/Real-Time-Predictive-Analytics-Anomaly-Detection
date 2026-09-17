from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_anomalies_collection,
    insert_anomaly,
)


def save_anomaly_event(event):
    """
    Save a unified anomaly event to MongoDB.
    """

    client = create_mongo_client()

    try:
        database = get_database(client)

        collection = get_anomalies_collection(
            database
        )

        event_data = event.model_dump(
            mode="json"
        )

        inserted_id = insert_anomaly(
            collection,
            event_data,
        )

        return inserted_id

    finally:
        client.close()