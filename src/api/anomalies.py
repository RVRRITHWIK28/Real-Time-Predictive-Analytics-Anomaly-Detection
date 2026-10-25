from fastapi import APIRouter, HTTPException

from src.database.mongodb import (
    create_mongo_client,
    get_database
)


REVENUE_ANOMALY_TYPES = ("revenue_spike", "revenue_drop")

router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"]
)


@router.get("/")
def get_anomalies(
    anomaly_type: str | None = None,
    is_anomaly: bool | None = None,
    limit: int = 20
):

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 100"
        )

    if anomaly_type is not None and anomaly_type not in REVENUE_ANOMALY_TYPES:
        return {
            "count": 0,
            "anomalies": []
        }

    client = None

    try:

        client = create_mongo_client()

        database = get_database(client)

        collection = database["anomalies"]

        query = {
            "anomaly_type": (
                anomaly_type
                if anomaly_type is not None
                else {"$in": list(REVENUE_ANOMALY_TYPES)}
            ),
            "is_anomaly": True if is_anomaly is None else is_anomaly,
        }

        anomalies = list(
            collection.find(
                query,
                {"_id": 0}
            )
            .sort("bucket", -1)
            .limit(limit)
        )

        return {
            "count": len(anomalies),
            "anomalies": anomalies
        }

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    finally:

        if client is not None:
            client.close()
