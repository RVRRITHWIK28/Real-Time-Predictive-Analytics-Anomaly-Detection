from fastapi import APIRouter, HTTPException

from src.database.mongodb import (
    create_mongo_client,
    get_database
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/summary")
def get_analytics_summary():

    client = None

    try:
        client = create_mongo_client()

        database = get_database(client)

        transactions = database["transactions"]
        anomalies = database["anomalies"]

        total_transactions = transactions.count_documents({})

        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_quantity": {"$sum": "$quantity"},
                    "total_revenue": {"$sum": "$revenue"},
                }
            }
        ]

        result = list(
            transactions.aggregate(pipeline)
        )

        if result:
            total_quantity = result[0]["total_quantity"]
            total_revenue = result[0]["total_revenue"]
        else:
            total_quantity = 0
            total_revenue = 0

        average_order_value = (
            total_revenue / total_transactions
            if total_transactions > 0
            else 0
        )

        unique_products = len(
            transactions.distinct("product_id")
        )

        unique_stores = len(
            transactions.distinct("store_id")
        )

        total_anomalies = anomalies.count_documents(
            {"is_anomaly": True}
        )

        return {
            "total_transactions": total_transactions,
            "total_quantity": total_quantity,
            "total_revenue": round(
                total_revenue,
                2
            ),
            "average_order_value": round(
                average_order_value,
                2
            ),
            "unique_products": unique_products,
            "unique_stores": unique_stores,
            "total_anomalies": total_anomalies
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    finally:
        if client is not None:
            client.close()


@router.get("/daily")
def get_daily_analytics():

    client = None

    try:
        client = create_mongo_client()

        database = get_database(client)

        collection = database["transactions"]

        pipeline = [
            {
                "$addFields": {
                    "timestamp_date": {
                        "$convert": {
                            "input": "$timestamp",
                            "to": "date",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            },
            {
                "$match": {
                    "timestamp_date": {
                        "$ne": None
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp_date",
                            "timezone": "UTC"
                        }
                    },
                    "transaction_count": {
                        "$sum": 1
                    },
                    "total_quantity": {
                        "$sum": "$quantity"
                    },
                    "total_revenue": {
                        "$sum": "$revenue"
                    }
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            }
        ]

        daily_data = list(
            collection.aggregate(pipeline)
        )

        result = []

        for day in daily_data:

            result.append({
                "date": day["_id"],
                "transaction_count": day[
                    "transaction_count"
                ],
                "total_quantity": day[
                    "total_quantity"
                ],
                "total_revenue": round(
                    day["total_revenue"],
                    2
                )
            })

        return {
            "count": len(result),
            "daily": result
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    finally:
        if client is not None:
            client.close()