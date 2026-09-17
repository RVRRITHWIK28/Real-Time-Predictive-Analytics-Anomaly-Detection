from fastapi import APIRouter, HTTPException

from src.database.mongodb import (
    create_mongo_client,
    get_database
)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/")
def get_products():

    client = None

    try:

        client = create_mongo_client()

        database = get_database(client)

        collection = database["transactions"]

        products = list(
            collection.aggregate(
                [
                    {
                        "$group": {
                            "_id": "$product_id",
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

        for product in products:

            result.append(
                {
                    "product_id": product["_id"],
                    "total_quantity": product["total_quantity"],
                    "total_revenue": round(
                        product["total_revenue"],
                        2
                    ),
                    "transaction_count": product["transaction_count"]
                }
            )

        return {
            "count": len(result),
            "products": result
        }

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )

    finally:

        if client is not None:
            client.close()


@router.get("/{product_id}")
def get_product(product_id: str):

    client = None

    try:

        client = create_mongo_client()

        database = get_database(client)

        collection = database["transactions"]

        result = collection.aggregate(
            [
                {
                    "$match": {
                        "product_id": product_id
                    }
                },
                {
                    "$group": {
                        "_id": "$product_id",
                        "category": {"$first": "$category"},
                        "total_quantity": {"$sum": "$quantity"},
                        "total_revenue": {"$sum": "$revenue"},
                        "transaction_count": {"$sum": 1}
                    }
                }
            ]
        )

        product = next(result, None)

        if product is None:

            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found"
            )

        return {
            "product_id": product["_id"],
            "category": product["category"],
            "total_quantity": product["total_quantity"],
            "total_revenue": round(
                product["total_revenue"],
                2
            ),
            "transaction_count": product["transaction_count"]
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