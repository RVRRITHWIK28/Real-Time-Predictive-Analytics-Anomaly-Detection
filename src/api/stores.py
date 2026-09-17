from fastapi import APIRouter, HTTPException

from src.database.mongodb import (
    create_mongo_client,
    get_database
)


router = APIRouter(
    prefix="/stores",
    tags=["Stores"]
)


@router.get("/")
def get_stores():

    client = None

    try:

        client = create_mongo_client()

        database = get_database(client)

        collection = database["transactions"]

        stores = list(
            collection.aggregate(
                [
                    {
                        "$group": {
                            "_id": "$store_id",
                            "total_quantity": {"$sum": "$quantity"},
                            "total_revenue": {"$sum": "$revenue"},
                            "transaction_count": {"$sum": 1}
                        }
                    },
                    {
                        "$sort": {
                            "total_revenue": -1
                        }
                    }
                ]
            )
        )

        result = []

        for store in stores:

            result.append(
                {
                    "store_id": store["_id"],
                    "total_quantity": store["total_quantity"],
                    "total_revenue": round(
                        store["total_revenue"],
                        2
                    ),
                    "transaction_count": store["transaction_count"]
                }
            )

        return {
            "count": len(result),
            "stores": result
        }

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    finally:

        if client is not None:
            client.close()


@router.get("/{store_id}")
def get_store(store_id: str):

    client = None

    try:

        client = create_mongo_client()

        database = get_database(client)

        collection = database["transactions"]

        result = collection.aggregate(
            [
                {
                    "$match": {
                        "store_id": store_id
                    }
                },
                {
                    "$group": {
                        "_id": "$store_id",
                        "region": {"$first": "$region"},
                        "total_quantity": {"$sum": "$quantity"},
                        "total_revenue": {"$sum": "$revenue"},
                        "transaction_count": {"$sum": 1}
                    }
                }
            ]
        )

        store = next(result, None)

        if store is None:

            raise HTTPException(
                status_code=404,
                detail=f"Store {store_id} not found"
            )

        return {
            "store_id": store["_id"],
            "region": store["region"],
            "total_quantity": store["total_quantity"],
            "total_revenue": round(
                store["total_revenue"],
                2
            ),
            "transaction_count": store["transaction_count"]
        }

    except HTTPException:

        raise

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    finally:

        if client is not None:
            client.close()