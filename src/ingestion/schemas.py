from datetime import datetime

from pydantic import BaseModel, Field


class TransactionEvent(BaseModel):
    event_id: str
    timestamp: datetime

    invoice_id: str | None = None
    business_date: str | None = None
    source_row: int | None = None
    source_sheet: str | None = None
    source_dataset: str | None = None

    customer_id: str | None = None
    product_id: str
    description: str | None = None
    category: str = "Unclassified"

    store_id: str
    country: str | None = None
    region: str | None = None

    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    discount: float | None = Field(default=None, ge=0, le=1)

    payment_method: str | None = None
    channel: str

    revenue: float = Field(gt=0)
