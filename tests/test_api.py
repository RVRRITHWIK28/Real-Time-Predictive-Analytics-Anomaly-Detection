from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predictions():
    response = client.get("/predictions/")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "predictions" in data
    assert isinstance(data["predictions"], list)


def test_predictions_filter():
    response = client.get(
        "/predictions/",
        params={
            "product_id": "P1001",
            "store_id": "S001",
            "limit": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] <= 5

    for prediction in data["predictions"]:
        assert prediction["product_id"] == "P1001"
        assert prediction["store_id"] == "S001"


def test_anomalies():
    response = client.get("/anomalies/")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "anomalies" in data
    assert isinstance(data["anomalies"], list)


def test_analytics_summary():
    response = client.get("/analytics/summary")

    assert response.status_code == 200

    data = response.json()

    assert "total_transactions" in data
    assert "total_quantity" in data
    assert "total_revenue" in data
    assert "average_order_value" in data
    assert "unique_products" in data
    assert "unique_stores" in data
    assert "total_anomalies" in data


def test_products():
    response = client.get("/products/")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "products" in data
    assert isinstance(data["products"], list)


def test_product():
    response = client.get("/products/P1001")

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == "P1001"
    assert "category" in data
    assert "total_quantity" in data
    assert "total_revenue" in data
    assert "transaction_count" in data


def test_stores():
    response = client.get("/stores/")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "stores" in data
    assert isinstance(data["stores"], list)


def test_store():
    response = client.get("/stores/S001")

    assert response.status_code == 200

    data = response.json()

    assert data["store_id"] == "S001"
    assert "region" in data
    assert "total_quantity" in data
    assert "total_revenue" in data
    assert "transaction_count" in data