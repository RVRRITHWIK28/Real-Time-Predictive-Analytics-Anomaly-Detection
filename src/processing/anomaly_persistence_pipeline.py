from src.processing.unified_anomaly_pipeline import (
    UnifiedAnomalyPipeline,
)
from src.database.anomaly_repository import (
    save_anomaly_event,
)


class AnomalyPersistencePipeline:

    def __init__(self):
        self.unified_pipeline = (
            UnifiedAnomalyPipeline()
        )

    def process_anomaly(
        self,
        timestamp,
        bucket,
        anomaly_type,
        entity_id,
        detection_result,
    ):
        # Step 1: Create unified anomaly event
        event = self.unified_pipeline.create_event(
            timestamp=timestamp,
            bucket=bucket,
            anomaly_type=anomaly_type,
            entity_id=entity_id,
            detection_result=detection_result,
        )

        # Step 2: Save event to MongoDB
        inserted_id = save_anomaly_event(event)

        # Step 3: Return both event and MongoDB ID
        return event, inserted_id