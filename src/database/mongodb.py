from pymongo import MongoClient

MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "retail_analytics"
TRANSACTIONS_COLLECTION = "transactions"
ANOMALIES_COLLECTION = "anomalies"

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
