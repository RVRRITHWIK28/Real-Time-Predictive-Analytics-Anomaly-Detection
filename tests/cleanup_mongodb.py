from src.database.mongodb import (
    create_mongo_client,
    get_database,
    get_transactions_collection,
)


client = create_mongo_client()

try:
    database = get_database(client)
    transactions = get_transactions_collection(database)

    result = transactions.delete_one(
        {"event_id": "mongo_test_001"}
    )

    if result.deleted_count == 1:
        print("Test document removed successfully!")
    else:
        print("Test document was not found.")

    print(
        f"Remaining transactions: "
        f"{transactions.count_documents({})}"
    )

finally:
    client.close()