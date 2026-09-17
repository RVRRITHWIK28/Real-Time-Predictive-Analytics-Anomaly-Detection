from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnomalyEvent(BaseModel):

    timestamp: datetime

    bucket: datetime

    anomaly_type: str

    entity_id: str

    is_anomaly: bool

    reason: str

    ratio: Optional[float]

    current_value: float

    baseline_value: float

    severity: str

    message: str

    business_impact: str

    recommendation: str