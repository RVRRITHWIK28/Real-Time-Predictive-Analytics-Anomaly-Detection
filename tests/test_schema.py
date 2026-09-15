from datetime import datetime

from src.ingestion.schemas import TransactionEvent


event = TransactionEvent(
    event_id="evt_000001",
    timestamp=datetime.now(),

    customer_id="C1029",
    product_id="P1007",
    category="Electronics",

    store_id="S03",
    region="South",

    quantity=2,
    unit_price=799.0,
    discount=0.10,

    payment_method="UPI",
    channel="online",

    revenue=1438.20,
)

print(event)
print("\nTransaction event is valid!")