
import pytest
from fastapi.testclient import TestClient
from ollama import ResponseError

from day03.main import app
from day01.lead_analyzer import LeadAnalysis


client = TestClient(app)


# -----------------------------------
# Test 1: Home endpoint
# -----------------------------------
def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to AI Automation API"


# -----------------------------------
# Test 2: Health endpoint
# -----------------------------------
def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "AI Automation API"


# -----------------------------------
# Test 3: Lead analysis success
# -----------------------------------
def test_analyze_lead_success(monkeypatch):

    mock_lead = LeadAnalysis(
        service="woocommerce",
        budget=15000,
        currency="USD",
        urgency="high",
        intent="hire_developer",
        summary="Customer needs a WooCommerce website urgently."
    )

    monkeypatch.setattr(
        "day03.main.analyze_lead",
        lambda message: mock_lead
    )

    response = client.post(
        "/analyze-lead",
        json={
            "message": (
                "I need a WooCommerce website with a "
                "budget of $15000 USD urgently."
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "woocommerce"
    assert data["budget"] == 15000
    assert data["currency"] == "USD"
    assert data["urgency"] == "high"
    assert data["intent"] == "hire_developer"
    assert data["lead_score"] == 100
    assert data["lead_quality"] == "hot"
    assert data["recommended_action"] == "contact_immediately"


# -----------------------------------
# Test 4: Invalid lead message
# -----------------------------------
@pytest.mark.parametrize(
    "message",
    ["", "Hi", "Short"]
)
def test_analyze_lead_invalid_message(message):

    response = client.post(
        "/analyze-lead",
        json={"message": message}
    )

    assert response.status_code == 422


# -----------------------------------
# Test 5: Missing lead message
# -----------------------------------
def test_analyze_lead_missing_message():

    response = client.post(
        "/analyze-lead",
        json={}
    )

    assert response.status_code == 422


# -----------------------------------
# Test 6: Order assistant success
# -----------------------------------
def test_ask_order_success(monkeypatch):

    monkeypatch.setattr(
        "day03.main.run_assistant",
        lambda question: (
            "Order 1003 is delivered. Total: 1800 INR."
        )
    )

    response = client.post(
        "/ask-order",
        json={
            "question": "What is the status and total of order 1003?"
        }
    )

    assert response.status_code == 200

    assert response.json()["answer"] == (
        "Order 1003 is delivered. Total: 1800 INR."
    )


# -----------------------------------
# Test 7: Unknown order
# -----------------------------------
def test_ask_order_not_found(monkeypatch):

    monkeypatch.setattr(
        "day03.main.run_assistant",
        lambda question: "Order 9999 was not found."
    )

    response = client.post(
        "/ask-order",
        json={
            "question": "What is the status of order 9999?"
        }
    )

    assert response.status_code == 200
    assert "9999" in response.json()["answer"]
    assert "not found" in response.json()["answer"]


# -----------------------------------
# Test 8: Invalid order question
# -----------------------------------
@pytest.mark.parametrize(
    "question",
    ["", "Hi"]
)
def test_ask_order_invalid_question(question):

    response = client.post(
        "/ask-order",
        json={"question": question}
    )

    assert response.status_code == 422


# -----------------------------------
# Test 9: Missing order question
# -----------------------------------
def test_ask_order_missing_question():

    response = client.post(
        "/ask-order",
        json={}
    )

    assert response.status_code == 422


# -----------------------------------
# Test 10: API documentation
# -----------------------------------
def test_swagger_docs():

    response = client.get("/docs")

    assert response.status_code == 200


# -----------------------------------
# Test 11: OpenAPI schema
# -----------------------------------
def test_openapi_schema():

    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert "/analyze-lead" in data["paths"]
    assert "/ask-order" in data["paths"]


# -----------------------------------
# Test 12: Unknown endpoint
# -----------------------------------
def test_unknown_endpoint():

    response = client.get("/invalid-endpoint")

    assert response.status_code == 404
