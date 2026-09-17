from collections import deque


class QuantityAnomalyDetector:

    def __init__(
        self,
        upper_threshold=2.0,
        lower_threshold=0.5,
        history_size=5,
    ):
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold

        self.history = deque(
            maxlen=history_size
        )

    def calculate_baseline(self):

        if not self.history:
            return 0.0

        return sum(self.history) / len(
            self.history
        )

    def detect(self, current_quantity):

        baseline = self.calculate_baseline()

        # No historical quantity available
        if baseline <= 0:

            self.history.append(
                current_quantity
            )

            return {
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

            reason = "Quantity spike"

        elif ratio <= self.lower_threshold:

            is_anomaly = True

            reason = "Quantity drop"

        else:

            is_anomaly = False

            reason = "Normal quantity"

        result = {
            "is_anomaly": is_anomaly,

            "reason": reason,

            "ratio": round(
                ratio,
                2,
            ),

            "current_quantity": (
                current_quantity
            ),

            "baseline_quantity": round(
                baseline,
                2,
            ),
        }

        # Add current value after comparison
        self.history.append(
            current_quantity
        )

        return result