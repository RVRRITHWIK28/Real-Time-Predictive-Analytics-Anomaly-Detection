from datetime import datetime

from pydantic import BaseModel, Field


class TransactionEvent(BaseModel):
    event_id: str
    timestamp: datetime

    customer_id: str
    product_id: str
    category: str

    store_id: str
    region: str

    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    discount: float = Field(ge=0, le=1)

    payment_method: str
    channel: str

    revenue: float = Field(gt=0)