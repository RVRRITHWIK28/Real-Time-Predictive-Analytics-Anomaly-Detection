from collections import deque


class StoreQuantityAnomalyDetector:

    def __init__(
        self,
        upper_threshold=2.0,
        lower_threshold=0.5,
        history_size=5,
    ):
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.history_size = history_size

        # Separate history for every store
        self.store_history = {}

    def calculate_baseline(self, store_id):

        history = self.store_history.get(
            store_id,
            deque(maxlen=self.history_size),
        )

        if not history:
            return 0.0

        return sum(history) / len(history)

    def detect(
        self,
        store_id,
        current_quantity,
    ):

        if store_id not in self.store_history:
            self.store_history[store_id] = deque(
                maxlen=self.history_size
            )

        history = self.store_history[store_id]

        baseline = self.calculate_baseline(
            store_id
        )

        # No historical data yet
        if baseline <= 0:

            history.append(
                current_quantity
            )

            return {
                "store_id": store_id,
                "is_anomaly": False,
                "reason": "Building baseline",
                "ratio": None,
                "current_quantity": current_quantity,
                "baseline_quantity": 0.0,
            }

        ratio = (
            current_quantity / baseline
        )

        if ratio >= self.upper_threshold:

            is_anomaly = True
            reason = "Store quantity spike"

        elif ratio <= self.lower_threshold:

            is_anomaly = True
            reason = "Store quantity drop"

        else:

            is_anomaly = False
            reason = "Normal store quantity"

        result = {
            "store_id": store_id,
            "is_anomaly": is_anomaly,
            "reason": reason,
            "ratio": round(ratio, 2),
            "current_quantity": current_quantity,
            "baseline_quantity": round(
                baseline,
                2,
            ),
        }

        # Add current quantity after detection
        history.append(
            current_quantity
        )

        return result