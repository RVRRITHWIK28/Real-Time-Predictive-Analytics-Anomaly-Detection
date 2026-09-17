from src.streaming.producer import create_producer, send_transaction


test_transaction = {
    "event_id": "test_001",
    "product_id": "P1001",
    "quantity": 2,
    "revenue": 49998.00,
}


producer = create_producer()

send_transaction(producer, test_transaction)

producer.close()

print("Test transaction sent successfully!")