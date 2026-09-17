from fastapi import FastAPI
from src.api.predictions import router as predictions_router
from src.api.anomalies import router as anomalies_router
from src.api.analytics import router as analytics_router
from src.api.products import router as products_router
from src.api.stores import router as stores_router
from src.database.mongodb import (
    create_mongo_client,
    get_database
)

app = FastAPI(
    title="Real-Time Predictive Analytics API",
    description=(
        "Backend API for real-time retail analytics, "
        "demand prediction, and anomaly detection."
    ),
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Real-Time Predictive Analytics API is running",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/health/detailed")
def detailed_health_check():

    client = None

    try:
        client = create_mongo_client()

        database = get_database(client)

        database.command("ping")

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:

        return {
            "status": "unhealthy",
            "database": "unavailable"
        }

    finally:

        if client is not None:
            client.close()


# Register API routers
app.include_router(predictions_router)
app.include_router(anomalies_router)
app.include_router(analytics_router)
app.include_router(products_router)
app.include_router(stores_router)
