import os

from dotenv import load_dotenv


load_dotenv()


PROJECT_NAME = os.getenv(
    "PROJECT_NAME",
    "Real-Time Predictive Analytics & Anomaly Detection",
)

VERSION = os.getenv(
    "VERSION",
    "1.0.0",
)

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development",
)


KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092",
)

TRANSACTION_TOPIC = os.getenv(
    "TRANSACTION_TOPIC",
    "transactions",
)

CONSUMER_GROUP = os.getenv(
    "CONSUMER_GROUP",
    "analytics-group",
)


MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017",
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "retail_analytics",
)

TRANSACTIONS_COLLECTION = os.getenv(
    "TRANSACTIONS_COLLECTION",
    "transactions",
)

ANOMALIES_COLLECTION = os.getenv(
    "ANOMALIES_COLLECTION",
    "anomalies",
)

PREDICTIONS_COLLECTION = os.getenv(
    "PREDICTIONS_COLLECTION",
    "predictions",
)