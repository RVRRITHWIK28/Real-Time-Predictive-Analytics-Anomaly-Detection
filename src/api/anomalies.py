from fastapi import APIRouter, HTTPException

from src.database.mongodb import (
    create_mongo_client,
    get_database
)


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

    client = None

    try:

        client = create_mongo_client()

        database = get_database(client)

        collection = database["anomalies"]

        query = {}

        if anomaly_type:
            query["anomaly_type"] = anomaly_type

        if is_anomaly is not None:
            query["is_anomaly"] = is_anomaly

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