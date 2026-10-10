import base64
import hashlib
import hmac
import json
from fastapi.testclient import TestClient
from day06.main import app


client = TestClient(app)


def make_signature(payload: bytes, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_signature(monkeypatch):
    monkeypatch.setenv(
        "WOOCOMMERCE_WEBHOOK_SECRET",
        "test-secret"
    )

    response = client.post(
        "/webhooks/woocommerce",
        content=b'{"id": 42}',
        headers={
            "X-WC-Webhook-Signature": "invalid",
            "X-WC-Webhook-Topic": "order.updated",
        }
    )

    assert response.status_code == 401


def test_missing_signature(monkeypatch):
    monkeypatch.setenv(
        "WOOCOMMERCE_WEBHOOK_SECRET",
        "test-secret"
    )

    response = client.post(
        "/webhooks/woocommerce",
        content=b'{"id": 42}',
        headers={
            "X-WC-Webhook-Topic": "order.updated",
        }
    )

    assert response.status_code == 401


def test_valid_webhook(monkeypatch):
    monkeypatch.setenv(
        "WOOCOMMERCE_WEBHOOK_SECRET",
        "test-secret"
    )

    # Replace the actual workflow with a safe fake.
    processed_orders = []

    def fake_process_order_event(order_id):
        processed_orders.append(order_id)

    monkeypatch.setattr(
        "day06.main.process_order_event",
        fake_process_order_event
    )

    payload = json.dumps({"id": 42}).encode("utf-8")

    signature = make_signature(
        payload,
        "test-secret"
    )

    response = client.post(
        "/webhooks/woocommerce",
        content=payload,
        headers={
            "X-WC-Webhook-Signature": signature,
            "X-WC-Webhook-Topic": "order.updated",
        }
    )

    assert response.status_code == 200
    assert response.json()["order_id"] == 42
    assert processed_orders == [42]


def test_invalid_order_id(monkeypatch):
    monkeypatch.setenv(
        "WOOCOMMERCE_WEBHOOK_SECRET",
        "test-secret"
    )

    payload = b'{"id": "not-an-integer"}'

    signature = make_signature(
        payload,
        "test-secret"
    )

    response = client.post(
        "/webhooks/woocommerce",
        content=payload,
        headers={
            "X-WC-Webhook-Signature": signature,
            "X-WC-Webhook-Topic": "order.updated",
        }
    )

    assert response.status_code == 400
