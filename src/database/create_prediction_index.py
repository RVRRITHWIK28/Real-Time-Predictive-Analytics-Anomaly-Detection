from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def create_prediction_unique_index():

    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["predictions"]

        index_name = collection.create_index(
            [
                ("product_id", 1),
                ("store_id", 1),
                ("prediction_date", 1),
                ("model_version", 1),
            ],
            unique=True,
            name="unique_prediction",
        )

        print(
            f"Unique prediction index created: {index_name}"
        )

    finally:
        client.close()


if __name__ == "__main__":
    create_prediction_unique_index()