import re
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from src.database.mongodb import (
    create_mongo_client,
    get_database,
)
from src.ml.weekly_demand_forecast import (
    InsufficientHistoryError,
    forecast_weekly_units,
)


router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
)


@router.get("/")
def get_predictions(
    product_id: str | None = None,
    store_id: str | None = None,
    limit: int = 20,
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100",
        )

    client = None
    try:
        client = create_mongo_client()
        collection = get_database(client)["predictions"]
        query = {}
        if product_id:
            query["product_id"] = product_id
        if store_id:
            query["store_id"] = store_id

        predictions = list(
            collection.find(query, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
        return {"count": len(predictions), "predictions": predictions}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable",
        )
    finally:
        if client is not None:
            client.close()


@router.get("/weekly/options")
def get_weekly_forecast_options(
    country: str | None = None,
    search: str | None = None,
    limit: int = 50,
):
    """Return country choices and country-scoped StockCode search results."""
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100",
        )

    client = None
    try:
        client = create_mongo_client()
        collection = get_database(client)["transactions"]
        countries = []
        if not country:
            countries = sorted(
                value
                for value in collection.distinct(
                    "store_id",
                    {"quantity": {"$gt": 0}, "store_id": {"$type": "string"}},
                )
                if value and isinstance(value, str)
            )

        stock_codes = []
        if country:
            match = {
                "store_id": country,
                "quantity": {"$gt": 0},
                "product_id": {"$type": "string", "$ne": ""},
            }
            if search and search.strip():
                pattern = re.escape(search.strip())
                match["$or"] = [
                    {"product_id": {"$regex": pattern, "$options": "i"}},
                    {"description": {"$regex": pattern, "$options": "i"}},
                ]

            stock_codes = list(
                collection.aggregate(
                    [
                        {"$match": match},
                        {
                            "$group": {
                                "_id": "$product_id",
                                "description": {"$first": "$description"},
                                "sale_lines": {"$sum": 1},
                                "units_sold": {"$sum": "$quantity"},
                            }
                        },
                        {"$sort": {"sale_lines": -1, "_id": 1}},
                        {"$limit": limit},
                        {
                            "$project": {
                                "_id": 0,
                                "stock_code": "$_id",
                                "description": 1,
                                "sale_lines": 1,
                                "units_sold": 1,
                            }
                        },
                    ]
                )
            )

        return {"countries": countries, "stock_codes": stock_codes}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable",
        )
    finally:
        if client is not None:
            client.close()


@router.get("/weekly-forecast")
def get_weekly_demand_forecast(
    country: str,
    stock_code: str,
    weeks: int = Query(default=13, ge=1, le=13),
):
    """Forecast weekly unit demand for one StockCode in one country."""
    client = None
    try:
        client = create_mongo_client()
        collection = get_database(client)["transactions"]
        weekly_history = list(
            collection.aggregate(
                [
                    {
                        "$match": {
                            "store_id": country,
                            "product_id": stock_code,
                            "quantity": {"$gt": 0},
                        }
                    },
                    {
                        "$set": {
                            "_event_datetime": {
                                "$convert": {
                                    "input": "$timestamp",
                                    "to": "date",
                                    "onError": None,
                                    "onNull": None,
                                }
                            }
                        }
                    },
                    {"$match": {"_event_datetime": {"$ne": None}}},
                    {
                        "$set": {
                            "_week_start": {
                                "$dateTrunc": {
                                    "date": "$_event_datetime",
                                    "unit": "week",
                                    "startOfWeek": "monday",
                                    "timezone": "Europe/London",
                                }
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": "$_week_start",
                            "units": {"$sum": "$quantity"},
                            "sale_lines": {"$sum": 1},
                            "description": {"$first": "$description"},
                        }
                    },
                    {"$sort": {"_id": 1}},
                    {
                        "$project": {
                            "_id": 0,
                            "week_start": {
                                "$dateToString": {
                                    "date": "$_id",
                                    "format": "%Y-%m-%d",
                                    "timezone": "Europe/London",
                                }
                            },
                            "units": 1,
                            "sale_lines": 1,
                            "description": 1,
                        }
                    },
                ]
            )
        )

        if not weekly_history:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No positive sales history was found for this Country and "
                    "StockCode."
                ),
            )

        history = [
            {
                "week_start": date.fromisoformat(row["week_start"]),
                "units": row["units"],
            }
            for row in weekly_history
        ]
        try:
            forecast = forecast_weekly_units(history, weeks)
        except InsufficientHistoryError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

        return {
            "country": country,
            "stock_code": stock_code,
            "description": weekly_history[-1].get("description"),
            "model": "RandomForestRegressor",
            "model_version": "weekly_random_forest_v1",
            "horizon_weeks": weeks,
            **forecast,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Could not build the weekly forecast",
        )
    finally:
        if client is not None:
            client.close()
