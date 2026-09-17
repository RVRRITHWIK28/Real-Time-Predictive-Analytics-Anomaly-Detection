from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_transactions_collection,
)


client = create_mongo_client()

try:
    database = get_database(client)
    transactions = get_transactions_collection(database)

    count = transactions.count_documents({})

    print(f"Total transactions in MongoDB: {count}")

    print("\nLatest 5 transactions:")

    latest_transactions = transactions.find().sort(
        "_id",
        -1,
    ).limit(5)

    for transaction in latest_transactions:
        print(
            f"{transaction['event_id']} | "
            f"{transaction['product_id']} | "
            f"Quantity: {transaction['quantity']} | "
            f"Revenue: Rs.{transaction['revenue']}"
        )

finally:
    client.close()