import calendar

from fastapi import APIRouter, HTTPException

from src.database.mongodb import (
    create_mongo_client,
    get_database,
)


ISOLATION_FOREST_MODEL_VERSION = "isolation_forest_v1"
REVENUE_ANOMALY_TYPES = (
    "hourly_revenue_spike",
    "hourly_revenue_drop",
    "daily_revenue_spike",
    "daily_revenue_drop",
)
SUPPORTED_YEARS = {2009, 2010, 2011}

router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"],
)


@router.get("/")
def get_anomalies(
    anomaly_type: str | None = None,
    time_scale: str | None = None,
    is_anomaly: bool | None = None,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
    limit: int = 20,
    offset: int = 0,
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100",
        )
    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="offset must be zero or greater",
        )
    if time_scale is not None and time_scale not in {"hourly", "daily"}:
        raise HTTPException(
            status_code=400,
            detail="time_scale must be hourly or daily",
        )
    if year is not None and year not in SUPPORTED_YEARS:
        raise HTTPException(
            status_code=400,
            detail="year must be 2009, 2010, or 2011",
        )
    if month is not None and month not in range(1, 13):
        raise HTTPException(
            status_code=400,
            detail="month must be between 1 and 12",
        )
    if day is not None and day not in range(1, 32):
        raise HTTPException(
            status_code=400,
            detail="day must be between 1 and 31",
        )
    if day is not None and month is None:
        raise HTTPException(
            status_code=400,
            detail="month is required when filtering by day",
        )
    if month is not None and day is not None:
        years_to_check = [year] if year is not None else sorted(SUPPORTED_YEARS)
        latest_valid_day = max(
            calendar.monthrange(candidate_year, month)[1]
            for candidate_year in years_to_check
        )
        if day > latest_valid_day:
            raise HTTPException(
                status_code=400,
                detail="day is not valid for the selected month and year",
            )
    if hour is not None and hour not in range(24):
        raise HTTPException(
            status_code=400,
            detail="hour must be between 0 and 23",
        )
    if hour is not None and time_scale == "daily":
        raise HTTPException(
            status_code=400,
            detail="hour filtering is only available for hourly anomalies",
        )
    if anomaly_type is not None and anomaly_type not in REVENUE_ANOMALY_TYPES:
        return {"count": 0, "total_count": 0, "anomalies": []}

    client = None
    try:
        client = create_mongo_client()
        database = get_database(client)
        collection = database["anomalies"]

        query = {
            "model_version": ISOLATION_FOREST_MODEL_VERSION,
            "anomaly_type": (
                anomaly_type
                if anomaly_type is not None
                else {"$in": list(REVENUE_ANOMALY_TYPES)}
            ),
            "is_anomaly": True if is_anomaly is None else is_anomaly,
        }
        if time_scale is not None:
            query["time_scale"] = time_scale
        elif hour is not None:
            query["time_scale"] = "hourly"

        date_parts = []
        if year is not None:
            date_parts.append({"$eq": [{"$year": "$bucket"}, year]})
        if month is not None:
            date_parts.append({"$eq": [{"$month": "$bucket"}, month]})
        if day is not None:
            date_parts.append({"$eq": [{"$dayOfMonth": "$bucket"}, day]})
        if hour is not None:
            date_parts.append({"$eq": [{"$hour": "$bucket"}, hour]})
        if date_parts:
            query["$expr"] = {"$and": date_parts}

        total_count = collection.count_documents(query)
        anomalies = list(
            collection.find(query, {"_id": 0})
            .sort("bucket", -1)
            .skip(offset)
            .limit(limit)
        )
        return {
            "count": len(anomalies),
            "total_count": total_count,
            "anomalies": anomalies,
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable",
        )
    finally:
        if client is not None:
            client.close()
