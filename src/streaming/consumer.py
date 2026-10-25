import json

from kafka import KafkaConsumer

from src.streaming.kafka_config import (
    KAFKA_BOOTSTRAP_SERVERS,
    TRANSACTION_TOPIC,
    CONSUMER_GROUP,
)


def deserialize_transaction(value):
    return json.loads(value.decode("utf-8"))


def create_consumer(
    group_id=None,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    max_poll_interval_ms=300000,
):
    if group_id is None:
        group_id = CONSUMER_GROUP

    return KafkaConsumer(
        TRANSACTION_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=group_id,
        value_deserializer=deserialize_transaction,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=enable_auto_commit,
        max_poll_interval_ms=max_poll_interval_ms,
    )


def consume_transactions(consumer):
    for message in consumer:
        yield message.value

