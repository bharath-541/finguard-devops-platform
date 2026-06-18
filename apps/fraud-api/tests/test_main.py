from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint_reports_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_low_risk_transaction_is_allowed():
    response = client.post(
        "/api/score",
        json={
            "transactionId": "txn-safe-1",
            "amount": 1200,
            "currency": "INR",
            "country": "IN",
            "deviceId": "device-known",
            "customerId": "cust-1",
            "failedLogins": 0,
            "velocity": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "ALLOW"


def test_high_risk_transaction_is_blocked():
    response = client.post(
        "/api/score",
        json={
            "transactionId": "txn-risk-1",
            "amount": 145000,
            "currency": "INR",
            "country": "BR",
            "deviceId": "new-device",
            "customerId": "cust-2",
            "failedLogins": 6,
            "velocity": 12,
            "networkStatus": "DOWN",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["decision"] == "BLOCK"
    assert "high_amount" in body["reasons"]
    assert "payment_network_timeout" in body["reasons"]


def test_metrics_endpoint_exposes_prometheus_data():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "finguard_http_requests_total" in response.text
