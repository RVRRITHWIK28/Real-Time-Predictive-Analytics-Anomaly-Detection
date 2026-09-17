import logging

from pymongo.errors import DuplicateKeyError

from src.streaming.consumer import (
    create_consumer,
    consume_transactions,
)

from src.database.mongodb import (
    create_mongo_client,
    get_database,
)

from src.config.logging_config import (
    setup_logging,
    get_logger,
)


setup_logging()

logger = get_logger(
    "transaction_consumer"
)


def run_consumer():

    consumer = create_consumer()

    client = create_mongo_client()

    database = get_database(
        client
    )

    collection = database[
        "transactions"
    ]

    logger.info(
        "Transaction consumer started"
    )

    logger.info(
        "Waiting for transactions..."
    )

    inserted_count = 0

    duplicate_count = 0

    try:

        for transaction in consume_transactions(
            consumer
        ):

            try:

                collection.insert_one(
                    transaction
                )

                inserted_count += 1

                logger.info(
                    "Inserted transaction: %s | Product: %s | Revenue: Rs.%s",
                    transaction["event_id"],
                    transaction["product_id"],
                    transaction["revenue"],
                )

            except DuplicateKeyError:

                duplicate_count += 1

                logger.warning(
                    "Duplicate transaction skipped: %s",
                    transaction["event_id"],
                )

    except KeyboardInterrupt:

        logger.info(
            "Transaction consumer stopped by user."
        )

    except Exception:

        logger.exception(
            "Unexpected error in transaction consumer."
        )

        raise

    finally:

        consumer.close()

        client.close()

        logger.info(
            "Consumer summary | Inserted: %s | Duplicates skipped: %s",
            inserted_count,
            duplicate_count,
        )


if __name__ == "__main__":

    run_consumer()