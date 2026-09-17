from pymongo import MongoClient

from src.config.settings import (
    MONGODB_URI,
    DATABASE_NAME,
    TRANSACTIONS_COLLECTION,
    ANOMALIES_COLLECTION,
    PREDICTIONS_COLLECTION,
)


def create_mongo_client():
    client = MongoClient(MONGODB_URI)

    return client


def get_database(client):
    return client[DATABASE_NAME]


def get_transactions_collection(database):
    return database[TRANSACTIONS_COLLECTION]


def insert_transaction(collection, transaction):
    result = collection.insert_one(transaction)

    return result.inserted_id


def get_anomalies_collection(database):
    return database[ANOMALIES_COLLECTION]


def insert_anomaly(collection, anomaly):
    result = collection.insert_one(anomaly)

    return result.inserted_id