from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def create_anomaly_unique_index():

    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["anomalies"]

        index_name = collection.create_index(
            [
                ("timestamp", 1),
                ("bucket", 1),
                ("anomaly_type", 1),
                ("entity_id", 1),
            ],
            unique=True,
            name="unique_anomaly_event",
        )

        print(
            f"Unique anomaly index created: {index_name}"
        )

    finally:
        client.close()


if __name__ == "__main__":
    create_anomaly_unique_index()