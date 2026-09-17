from collections import defaultdict, deque
from datetime import datetime


class StreamAnalytics:
    def __init__(self):
        self.total_transactions = 0
        self.total_quantity = 0
        self.total_revenue = 0.0

        self.product_metrics = defaultdict(
            lambda: {
                "transactions": 0,
                "quantity": 0,
                "revenue": 0.0,
            }
        )

        self.store_metrics = defaultdict(
            lambda: {
                "transactions": 0,
                "quantity": 0,
                "revenue": 0.0,
            }
        )

        self.recent_transactions = deque()

        # Revenue and quantity tracked by minute
        self.minute_revenue = defaultdict(float)
        self.minute_quantity = defaultdict(int)

        # Quantity tracked by product and minute
        self.product_minute_quantity = defaultdict(
            lambda: defaultdict(int)
        )

        # Quantity tracked by store and minute
        self.store_minute_quantity = defaultdict(
            lambda: defaultdict(int)
        )

    def process_transaction(self, transaction):

        self.total_transactions += 1

        self.total_quantity += (
            transaction["quantity"]
        )

        self.total_revenue += (
            transaction["revenue"]
        )

        event_time = datetime.fromisoformat(
            transaction["timestamp"].replace(
                "Z",
                "+00:00",
            )
        )

        minute_bucket = event_time.replace(
            second=0,
            microsecond=0,
        )

        # Get product and store IDs
        product_id = transaction["product_id"]
        store_id = transaction["store_id"]

        # Track revenue and quantity for this minute
        self.minute_revenue[minute_bucket] += (
            transaction["revenue"]
        )

        self.minute_quantity[minute_bucket] += (
            transaction["quantity"]
        )

        # Track quantity for this product and minute
        self.product_minute_quantity[
            product_id
        ][minute_bucket] += (
            transaction["quantity"]
        )

        # Track quantity for this store and minute
        self.store_minute_quantity[
            store_id
        ][minute_bucket] += (
            transaction["quantity"]
        )

        # Product-level metrics
        self.product_metrics[product_id][
            "transactions"
        ] += 1

        self.product_metrics[product_id][
            "quantity"
        ] += transaction["quantity"]

        self.product_metrics[product_id][
            "revenue"
        ] += transaction["revenue"]

        # Store-level metrics
        self.store_metrics[store_id][
            "transactions"
        ] += 1

        self.store_metrics[store_id][
            "quantity"
        ] += transaction["quantity"]

        self.store_metrics[store_id][
            "revenue"
        ] += transaction["revenue"]

        # Add transaction to the 60-second window
        self.recent_transactions.append(
            transaction
        )

        # Remove transactions older than 60 seconds
        while self.recent_transactions:

            oldest_transaction = (
                self.recent_transactions[0]
            )

            oldest_time = datetime.fromisoformat(
                oldest_transaction[
                    "timestamp"
                ].replace(
                    "Z",
                    "+00:00",
                )
            )

            age_seconds = (
                event_time - oldest_time
            ).total_seconds()

            if age_seconds <= 60:
                break

            self.recent_transactions.popleft()

    def get_metrics(self):

        average_order_value = 0.0

        if self.total_transactions > 0:

            average_order_value = (
                self.total_revenue
                / self.total_transactions
            )

        return {
            "total_transactions": (
                self.total_transactions
            ),
            "total_quantity": (
                self.total_quantity
            ),
            "total_revenue": round(
                self.total_revenue,
                2,
            ),
            "average_order_value": round(
                average_order_value,
                2,
            ),
        }

    def get_product_metrics(self):

        return dict(
            self.product_metrics
        )

    def get_store_metrics(self):

        return dict(
            self.store_metrics
        )

    def get_window_metrics(self):

        window_transactions = len(
            self.recent_transactions
        )

        window_quantity = sum(
            transaction["quantity"]
            for transaction
            in self.recent_transactions
        )

        window_revenue = sum(
            transaction["revenue"]
            for transaction
            in self.recent_transactions
        )

        return {
            "transactions": (
                window_transactions
            ),
            "quantity": window_quantity,
            "revenue": round(
                window_revenue,
                2,
            ),
        }

    def get_minute_revenue(self):

        return {
            bucket: round(
                revenue,
                2,
            )
            for bucket, revenue
            in self.minute_revenue.items()
        }

    def get_minute_quantity(self):

        return dict(
            self.minute_quantity
        )

    def get_product_minute_quantity(self):

        return {
            product_id: dict(minute_data)
            for product_id, minute_data
            in self.product_minute_quantity.items()
        }

    def get_store_minute_quantity(self):

        return {
            store_id: dict(minute_data)
            for store_id, minute_data
            in self.store_minute_quantity.items()
        }

    def print_metrics(self):

        metrics = self.get_metrics()

        print(
            f"Transactions: "
            f"{metrics['total_transactions']} | "
            f"Units: "
            f"{metrics['total_quantity']} | "
            f"Revenue: "
            f"Rs.{metrics['total_revenue']} | "
            f"AOV: "
            f"Rs.{metrics['average_order_value']}"
        )


if __name__ == "__main__":
    print(
        "StreamAnalytics module loaded successfully."
    )