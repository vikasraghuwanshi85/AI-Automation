import pytest
from tools import get_order_status, get_order_total


def test_existing_order_status():
    result = get_order_status(1003)

    assert result["success"] is True
    assert result["status"] == "delivered"
    assert result["order_id"] == 1003


def test_existing_order_total():
    result = get_order_total(1002)

    assert result["success"] is True
    assert result["total"] == 4500
    assert result["currency"] == "INR"


def test_nonexistent_order():
    result = get_order_status(9999)

    assert result["success"] is False
    assert result["error"] == "Order not found"


def test_nonexistent_order_total():
    result = get_order_total(9999)

    assert result["success"] is False
    assert result["error"] == "Order not found"


@pytest.mark.parametrize(
    "order_id, expected_status",
    [
        (1001, "processing"),
        (1002, "shipped"),
        (1003, "delivered"),
    ]
)
def test_multiple_order_statuses(order_id, expected_status):
    result = get_order_status(order_id)

    assert result["success"] is True
    assert result["status"] == expected_status
