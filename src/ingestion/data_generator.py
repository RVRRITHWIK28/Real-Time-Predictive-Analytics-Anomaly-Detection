import random
import uuid
from datetime import datetime, timezone

from src.ingestion.master_data import PRODUCTS, STORES, CUSTOMERS
from src.ingestion.schemas import TransactionEvent


PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Cash",
    "Net Banking",
]

CHANNELS = [
    "online",
    "offline",
]


def choose_product():
    products = PRODUCTS
    weights = [product["demand_weight"] for product in products]

    return random.choices(products, weights=weights, k=1)[0]


def choose_store():
    return random.choice(STORES)


def choose_customer():
    return random.choice(CUSTOMERS)


def generate_transaction():
    product = choose_product()
    store = choose_store()
    customer = choose_customer()

    quantity = random.randint(1, 5)

    price_variation = random.uniform(0.95, 1.05)
    unit_price = round(
        product["base_price"] * price_variation,
        2,
    )

    discount = round(
        random.uniform(0.00, 0.20),
        2,
    )

    revenue = round(
        quantity * unit_price * (1 - discount),
        2,
    )

    event = TransactionEvent(
        event_id=f"evt_{uuid.uuid4().hex[:12]}",
        timestamp=datetime.now(timezone.utc),

        customer_id=customer,
        product_id=product["product_id"],
        category=product["category"],

        store_id=store["store_id"],
        region=store["region"],

        quantity=quantity,
        unit_price=unit_price,
        discount=discount,

        payment_method=random.choice(PAYMENT_METHODS),
        channel=random.choice(CHANNELS),

        revenue=revenue,
    )

    return event

def get_time_demand_multiplier(hour: int) -> float:
    """
    Return a demand multiplier based on the hour of day.
    """

    if 0 <= hour < 6:
        return 0.20

    if 6 <= hour < 9:
        return 0.50

    if 9 <= hour < 12:
        return 0.80

    if 12 <= hour < 15:
        return 1.20

    if 15 <= hour < 18:
        return 1.00

    if 18 <= hour < 21:
        return 1.50

    if 21 <= hour < 24:
        return 0.70

    return 1.0