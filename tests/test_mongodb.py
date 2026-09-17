from src.database.mongodb import create_mongo_client, get_database


client = create_mongo_client()

try:
    database = get_database(client)
    transactions = database["transactions"]

    test_transaction = {
        "event_id": "mongo_test_001",
        "product_id": "P1001",
        "quantity": 2,
        "unit_price": 24999.00,
        "discount": 0.10,
        "revenue": 44998.20,
    }

    # Insert document
    result = transactions.insert_one(test_transaction)

    print("Transaction inserted successfully!")
    print(f"Document ID: {result.inserted_id}")

    # Read document
    saved_transaction = transactions.find_one(
        {"event_id": "mongo_test_001"}
    )

    print("\nTransaction retrieved from MongoDB:")
    print(saved_transaction)

finally:
    client.close()