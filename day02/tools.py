
# day02/tools.py

ORDERS = {
    1001: {
        "status": "processing",
        "customer": "Rahul",
        "total": 2500,
        "currency": "INR"
    },
    1002: {
        "status": "shipped",
        "customer": "Amit",
        "total": 4500,
        "currency": "INR"
    },
    1003: {
        "status": "delivered",
        "customer": "Priya",
        "total": 1800,
        "currency": "INR"
    }
}


def get_order_status(order_id: int) -> dict:
    """
    Get the status of a WooCommerce order.

    Args:
        order_id: The numeric order ID.

    Returns:
        A dictionary containing the order details
        or an error if the order is not found.
    """

    if order_id not in ORDERS:
        return {
            "success": False,
            "error": "Order not found"
        }

    return {
        "success": True,
        "order_id": order_id,
        **ORDERS[order_id]
    }


def get_order_total(order_id: int) -> dict:
    """
    Get the total amount of a WooCommerce order.

    Args:
        order_id: The numeric order ID.
    """

    if order_id not in ORDERS:
        return {
            "success": False,
            "error": "Order not found"
        }

    order = ORDERS[order_id]

    return {
        "success": True,
        "order_id": order_id,
        "total": order["total"],
        "currency": order["currency"]
    }
