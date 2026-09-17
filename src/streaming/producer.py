import json

from kafka import KafkaProducer

from src.streaming.kafka_config import (
    KAFKA_BOOTSTRAP_SERVERS,
    TRANSACTION_TOPIC,
)


def serialize_transaction(transaction):
    return json.dumps(transaction).encode("utf-8")


def create_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=serialize_transaction,
    )

    return producer


def send_transaction(producer, transaction):
    producer.send(
        TRANSACTION_TOPIC,
        value=transaction,
    )

    producer.flush()