from fastapi import APIRouter, HTTPException

from src.database.mongodb import (
    create_mongo_client,
    get_database
)


router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)


@router.get("/")
def get_predictions(
    product_id: str | None = None,
    store_id: str | None = None,
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

        collection = database["predictions"]

        query = {}

        if product_id:
            query["product_id"] = product_id

        if store_id:
            query["store_id"] = store_id

        predictions = list(
            collection.find(
                query,
                {"_id": 0}
            )
            .sort("created_at", -1)
            .limit(limit)
        )

        return {
            "count": len(predictions),
            "predictions": predictions
        }

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    finally:

        if client is not None:
            client.close()