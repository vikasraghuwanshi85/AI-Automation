from decimal import Decimal

def decide_order_action(
    status: str,
    total: Decimal
) -> dict:
    """
    Decide what should happen next based on
    the WooCommerce order status and total.
    """

    if status == "pending":
        return {
            "action": "await_payment",
            "priority": "high",
            "reason": "Order is awaiting payment."
        }

    if status == "failed":
        return {
            "action": "review_failed_payment",
            "priority": "high",
            "reason": "Order payment has failed."
        }

    if status == "on-hold":
        return {
            "action": "manual_review",
            "priority": "medium",
            "reason": "Order is currently on hold."
        }

    if status == "processing":
        if total >= Decimal("1000"):
            return {
                "action": "priority_fulfillment_review",
                "priority": "high",
                "reason": "High-value order requires fulfillment review."
            }

        return {
            "action": "prepare_fulfillment",
            "priority": "normal",
            "reason": "Order is ready for fulfillment processing."
        }

    if status == "completed":
        return {
            "action": "no_action",
            "priority": "low",
            "reason": "Order is already completed."
        }

    if status in ("cancelled", "refunded"):
        return {
            "action": "no_action",
            "priority": "low",
            "reason": "Order is cancelled or refunded."
        }

    return {
        "action": "manual_review",
        "priority": "medium",
        "reason": "Order status requires manual review."
    }
