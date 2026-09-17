import json

from kafka import KafkaConsumer

from src.streaming.kafka_config import (
    KAFKA_BOOTSTRAP_SERVERS,
    TRANSACTION_TOPIC,
    CONSUMER_GROUP,
)


def deserialize_transaction(value):
    return json.loads(value.decode("utf-8"))


def create_consumer(group_id=None):
    if group_id is None:
        group_id = CONSUMER_GROUP

    consumer = KafkaConsumer(
        TRANSACTION_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        value_deserializer=deserialize_transaction,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

    return consumer


def consume_transactions(consumer):
    for message in consumer:
        transaction = message.value
        yield transaction