from collections import deque


class RevenueAnomalyDetector:

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

    def detect(self, current_revenue):

        baseline = self.calculate_baseline()

        # No historical revenue available
        if baseline <= 0:

            self.history.append(
                current_revenue
            )

            return {
                "is_anomaly": False,
                "reason": "Building baseline",
                "ratio": None,
                "current_revenue": round(
                    current_revenue,
                    2,
                ),
                "baseline_revenue": 0.0,
            }

        ratio = (
            current_revenue / baseline
        )

        if ratio >= self.upper_threshold:

            is_anomaly = True

            reason = "Revenue spike"

        elif ratio <= self.lower_threshold:

            is_anomaly = True

            reason = "Revenue drop"

        else:

            is_anomaly = False

            reason = "Normal revenue"

        result = {
            "is_anomaly": is_anomaly,

            "reason": reason,

            "ratio": round(
                ratio,
                2,
            ),

            "current_revenue": round(
                current_revenue,
                2,
            ),

            "baseline_revenue": round(
                baseline,
                2,
            ),
        }

        # Add current value only after
        # comparing it with the old baseline.
        self.history.append(
            current_revenue
        )

        return result