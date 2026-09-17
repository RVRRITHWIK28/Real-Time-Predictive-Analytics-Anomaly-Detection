import csv

from src.streaming.producer import (
    create_producer,
    send_transaction,
)


INPUT_FILE = "data/raw/historical_transactions.csv"


def load_transactions(limit=None):
    transactions = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            transaction = {
                "event_id": row["event_id"],
                "timestamp": row["timestamp"],
                "customer_id": row["customer_id"],
                "product_id": row["product_id"],
                "category": row["category"],
                "store_id": row["store_id"],
                "region": row["region"],
                "quantity": int(row["quantity"]),
                "unit_price": float(row["unit_price"]),
                "discount": float(row["discount"]),
                "payment_method": row["payment_method"],
                "channel": row["channel"],
                "revenue": float(row["revenue"]),
            }

            transactions.append(transaction)

            if limit is not None and len(transactions) >= limit:
                break

    return transactions


def run_producer(limit=None):
    transactions = load_transactions(limit)

    print(f"Transactions loaded: {len(transactions)}")

    producer = create_producer()

    try:
        for transaction in transactions:
            send_transaction(producer, transaction)

            print(
                f"Sent historical transaction: "
                f"{transaction['event_id']} | "
                f"Product: {transaction['product_id']} | "
                f"Quantity: {transaction['quantity']}"
            )

    finally:
        producer.close()

    print("Historical Kafka replay completed.")


if __name__ == "__main__":
    run_producer()