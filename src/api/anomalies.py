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

router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"],
)


@router.get("/")
def get_anomalies(
    anomaly_type: str | None = None,
    time_scale: str | None = None,
    is_anomaly: bool | None = None,
    limit: int = 20,
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100",
        )
    if time_scale is not None and time_scale not in {"hourly", "daily"}:
        raise HTTPException(
            status_code=400,
            detail="time_scale must be hourly or daily",
        )
    if anomaly_type is not None and anomaly_type not in REVENUE_ANOMALY_TYPES:
        return {"count": 0, "anomalies": []}

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

        anomalies = list(
            collection.find(query, {"_id": 0})
            .sort("bucket", -1)
            .limit(limit)
        )
        return {"count": len(anomalies), "anomalies": anomalies}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable",
        )
    finally:
        if client is not None:
            client.close()
