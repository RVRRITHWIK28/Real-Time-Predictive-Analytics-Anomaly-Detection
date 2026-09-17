from src.processing.completed_anomaly_pipeline import (
    CompletedAnomalyPipeline,
)

from src.database.anomaly_repository import (
    save_anomaly_event,
)


class CompletedAnomalyPersistencePipeline:

    def __init__(self):

        self.anomaly_pipeline = (
            CompletedAnomalyPipeline()
        )

    def add_transaction(self, transaction):

        return self.anomaly_pipeline.add_transaction(
            transaction
        )

    def process_completed_buckets(
        self,
        current_time,
    ):

        events = (
            self.anomaly_pipeline
            .process_completed_buckets(
                current_time
            )
        )

        saved_events = []

        for event in events:

            inserted_id = save_anomaly_event(
                event
            )

            saved_events.append(
                {
                    "event": event,
                    "inserted_id": inserted_id,
                }
            )

        return saved_events