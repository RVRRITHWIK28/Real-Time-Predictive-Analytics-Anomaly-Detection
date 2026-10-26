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

        unique_countries = len(
            [country for country in transactions.distinct("country") if country]
        )
        if unique_countries == 0:
            # Keep the endpoint compatible with older synthetic records.
            unique_countries = len(transactions.distinct("store_id"))

        model_query = {
            "is_anomaly": True,
            "model_version": "isolation_forest_v1",
        }
        hourly_revenue_anomalies = anomalies.count_documents(
            {**model_query, "time_scale": "hourly"}
        )
        daily_revenue_anomalies = anomalies.count_documents(
            {**model_query, "time_scale": "daily"}
        )
        total_anomalies = (
            hourly_revenue_anomalies + daily_revenue_anomalies
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
            "average_sale_line_value": round(
                average_order_value,
                2
            ),
            "unique_products": unique_products,
            "unique_countries": unique_countries,
            "unique_stores": unique_countries,
            "total_anomalies": total_anomalies,
            "hourly_revenue_anomalies": hourly_revenue_anomalies,
            "daily_revenue_anomalies": daily_revenue_anomalies
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
def get_daily_analytics(country: str | None = None, product_id: str | None = None):

    client = None

    try:
        client = create_mongo_client()

        database = get_database(client)

        collection = database["transactions"]

        transaction_match = {}
        if country:
            transaction_match["$or"] = [
                {"country": country},
                {"store_id": country},
            ]
        if product_id:
            transaction_match["product_id"] = product_id

        # Scope the source collection before date extraction so filters reduce
        # the work required by the daily aggregation.
        pipeline = []
        if transaction_match:
            pipeline.append({"$match": transaction_match})

        # Online Retail II events already carry this date, so prefer it over
        # parsing every timestamp while scanning the full transaction history.
        pipeline.extend([
            {
                "$addFields": {
                    "analytics_date": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {
                                        "$eq": [
                                            {"$type": "$business_date"},
                                            "string",
                                        ]
                                    },
                                    "then": "$business_date",
                                },
                                {
                                    "case": {
                                        "$eq": [{"$type": "$timestamp"}, "string"]
                                    },
                                    "then": {"$substrBytes": ["$timestamp", 0, 10]},
                                },
                                {
                                    "case": {
                                        "$eq": [{"$type": "$timestamp"}, "date"]
                                    },
                                    "then": {
                                        "$dateToString": {
                                            "format": "%Y-%m-%d",
                                            "date": "$timestamp",
                                            "timezone": "UTC",
                                        }
                                    },
                                },
                            ],
                            "default": None,
                        }
                    }
                }
            },
            {
                "$match": {
                    "analytics_date": {
                        "$regex": r"^\d{4}-\d{2}-\d{2}$"
                    }
                }
            },
            {
                "$group": {
                    "_id": "$analytics_date",
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
        ])
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
