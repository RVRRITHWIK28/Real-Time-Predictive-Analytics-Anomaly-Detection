from collections import deque


class ProductQuantityAnomalyDetector:

    def __init__(
        self,
        upper_threshold=2.0,
        lower_threshold=0.5,
        history_size=5,
    ):
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold
        self.history_size = history_size

        # Separate history for every product
        self.product_history = {}

    def calculate_baseline(self, product_id):

        history = self.product_history.get(
            product_id,
            deque(maxlen=self.history_size),
        )

        if not history:
            return 0.0

        return sum(history) / len(history)

    def detect(
        self,
        product_id,
        current_quantity,
    ):

        if product_id not in self.product_history:
            self.product_history[product_id] = deque(
                maxlen=self.history_size
            )

        history = self.product_history[
            product_id
        ]

        baseline = self.calculate_baseline(
            product_id
        )

        # No historical data yet
        if baseline <= 0:

            history.append(
                current_quantity
            )

            return {
                "product_id": product_id,
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
            reason = "Product quantity spike"

        elif ratio <= self.lower_threshold:

            is_anomaly = True
            reason = "Product quantity drop"

        else:

            is_anomaly = False
            reason = "Normal product quantity"

        result = {
            "product_id": product_id,
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