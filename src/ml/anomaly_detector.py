from collections import deque


class TransactionVolumeDetector:
    def __init__(
        self,
        threshold=2.0,
        history_size=5,
    ):
        self.threshold = threshold

        self.history = deque(
            maxlen=history_size
        )

    def calculate_baseline(self):
        if not self.history:
            return 0.0

        return sum(self.history) / len(self.history)

    def detect(self, current_count, baseline_count=None):

        if baseline_count is None:
            baseline_count = self.calculate_baseline()

        # No baseline available yet
        if baseline_count <= 0:

            self.history.append(current_count)

            return {
                "is_anomaly": False,
                "reason": "Building baseline",
                "ratio": None,
                "current_count": current_count,
                "baseline_count": 0.0,
            }

        ratio = current_count / baseline_count

        is_anomaly = ratio >= self.threshold

        result = {
            "is_anomaly": is_anomaly,

            "reason": (
                "Transaction volume spike"
                if is_anomaly
                else "Normal transaction volume"
            ),

            "ratio": round(
                ratio,
                2,
            ),

            "current_count": current_count,

            "baseline_count": round(
                baseline_count,
                2,
            ),
        }

        # Add current observation to history
        self.history.append(current_count)

        return result