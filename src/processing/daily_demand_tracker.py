from collections import defaultdict
from datetime import datetime


class DailyDemandTracker:

    def __init__(self):
        # Structure:
        # {
        #     "2026-09-30": {
        #         ("P1001", "S001"): 79
        #     }
        # }
        self.daily_demand = defaultdict(lambda: defaultdict(int))

    def add_transactions(self, transactions):
        """
        Add completed-bucket transactions to the daily demand state.
        """

        for transaction in transactions:

            timestamp = transaction["timestamp"]

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                )

            date_key = timestamp.date().isoformat()

            product_id = transaction["product_id"]
            store_id = transaction["store_id"]
            quantity = transaction["quantity"]

            self.daily_demand[date_key][
                (product_id, store_id)
            ] += quantity

    def get_daily_demand(
        self,
        date,
        product_id,
        store_id
    ):
        """
        Get accumulated demand for a product/store on a specific day.
        """

        date_key = self._normalize_date(date)

        return self.daily_demand[date_key].get(
            (product_id, store_id),
            0
        )

    def get_product_store_demand(
        self,
        product_id,
        store_id
    ):
        """
        Return the complete daily demand history
        for a product/store pair.
        """

        history = []

        for date_key in sorted(self.daily_demand.keys()):

            quantity = self.daily_demand[date_key].get(
                (product_id, store_id),
                0
            )

            history.append({
                "date": date_key,
                "product_id": product_id,
                "store_id": store_id,
                "demand": quantity
            })

        return history

    @staticmethod
    def _normalize_date(date):

        if isinstance(date, datetime):
            return date.date().isoformat()

        if hasattr(date, "isoformat"):
            return date.isoformat()

        return str(date)


if __name__ == "__main__":

    tracker = DailyDemandTracker()

    transactions = [
        {
            "timestamp": "2026-10-01T10:01:15+00:00",
            "product_id": "P1001",
            "store_id": "S001",
            "quantity": 3
        },
        {
            "timestamp": "2026-10-01T10:02:20+00:00",
            "product_id": "P1001",
            "store_id": "S001",
            "quantity": 5
        },
        {
            "timestamp": "2026-10-01T10:03:10+00:00",
            "product_id": "P1001",
            "store_id": "S002",
            "quantity": 4
        },
        {
            "timestamp": "2026-10-01T11:01:05+00:00",
            "product_id": "P1001",
            "store_id": "S001",
            "quantity": 2
        }
    ]

    tracker.add_transactions(transactions)

    print("=" * 60)
    print("DAILY DEMAND TRACKER TEST")
    print("=" * 60)

    demand = tracker.get_daily_demand(
        "2026-10-01",
        "P1001",
        "S001"
    )

    print("\nP1001 + S001 daily demand:")
    print(demand)

    print("\nComplete product/store history:")

    history = tracker.get_product_store_demand(
        "P1001",
        "S001"
    )

    for record in history:
        print(record)

    print("=" * 60)
    print("DAILY DEMAND TRACKER TEST COMPLETE")
    print("=" * 60)