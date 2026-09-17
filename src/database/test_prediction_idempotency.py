from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


def test_prediction_idempotency():

    client = create_mongo_client()

    try:
        database = get_database(client)
        collection = database["predictions"]

        test_prediction = {
            "product_id": "TEST_PRODUCT",
            "store_id": "TEST_STORE",
            "prediction_date": datetime(
                2099,
                1,
                1,
                tzinfo=timezone.utc,
            ),
            "predicted_demand": 100.0,
            "model_version": "TEST_1.0",
            "created_at": datetime.now(
                timezone.utc
            ),
        }

        # Remove any previous test document.
        collection.delete_one({
            "product_id": test_prediction["product_id"],
            "store_id": test_prediction["store_id"],
            "prediction_date": test_prediction["prediction_date"],
            "model_version": test_prediction["model_version"],
        })

        # ---------------------------------
        # First insertion
        # ---------------------------------

        collection.insert_one(test_prediction)

        print("First insert: SUCCESS")

        # ---------------------------------
        # Duplicate insertion
        # ---------------------------------

        try:

            collection.insert_one(
                test_prediction
            )

            print(
                "ERROR: Duplicate prediction "
                "was inserted."
            )

        except DuplicateKeyError:

            print(
                "Second insert: BLOCKED "
                "(duplicate detected)"
            )

        # ---------------------------------
        # Cleanup
        # ---------------------------------

        collection.delete_one({
            "product_id": test_prediction["product_id"],
            "store_id": test_prediction["store_id"],
            "prediction_date": test_prediction["prediction_date"],
            "model_version": test_prediction["model_version"],
        })

        print("Test prediction removed.")

        print(
            "PREDICTION IDEMPOTENCY TEST PASSED"
        )

    finally:
        client.close()


if __name__ == "__main__":
    test_prediction_idempotency()