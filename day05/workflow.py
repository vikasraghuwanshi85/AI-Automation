import logging
from decimal import Decimal, InvalidOperation
from pathlib import Path

from day04.woocommerce_client import (
    WooCommerceClient,
    WooCommerceAPIError,
)
from day05.business_rules import decide_order_action
from day05.message_generator import generate_order_message


# Create the logs directory.
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "workflow.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def run_order_workflow(order_id: int) -> dict:
    """
    Execute the WooCommerce order automation.
    """

    logger.info("Workflow started for order %s", order_id)

    try:
        # STEP 1: Retrieve the real order.
        woo_client = WooCommerceClient()
        order = woo_client.get_order(order_id)

        # STEP 2: Validate the returned data.
        if not order.get("success"):
            raise ValueError("Order retrieval was unsuccessful.")

        required_fields = [
            "order_id",
            "status",
            "total",
            "currency",
        ]

        for field in required_fields:
            if field not in order:
                raise ValueError(
                    f"Missing required order field: {field}"
                )

        if isinstance(order["order_id"], bool) or (
            not isinstance(order["order_id"], int)
        ):
            raise ValueError("Invalid returned order ID.")

        if order["order_id"] != order_id:
            raise ValueError("Returned order ID does not match request.")

        if not isinstance(order["status"], str) or (
            not order["status"].strip()
        ):
            raise ValueError("Invalid order status.")

        if not isinstance(order["currency"], str) or (
            not order["currency"].strip()
        ):
            raise ValueError("Invalid currency.")

        try:
            total = Decimal(str(order["total"]))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("Invalid order total.")

        if not total.is_finite() or total < 0:
            raise ValueError("Invalid order total.")

        # STEP 3: Apply business rules.
        decision = decide_order_action(
            status=order["status"],
            total=total
        )

        logger.info(
            "Order %s action: %s",
            order_id,
            decision["action"]
        )

        # STEP 4: Generate a message using Ollama.
        message = generate_order_message(
            order=order,
            decision=decision
        )

        # STEP 5: Return the result.
        result = {
            "success": True,
            "order": order,
            "decision": decision,
            "message_draft": message
        }

        logger.info(
            "Workflow completed for order %s",
            order_id
        )

        return result

    except (
        WooCommerceAPIError,
        ValueError,
        KeyError,
    ) as error:

        logger.error(
            "Workflow failed for order %s: %s",
            order_id,
            error
        )

        return {
            "success": False,
            "order_id": order_id,
            "error": str(error)
        }

    except Exception:
        # Log the unexpected error internally.
        logger.exception(
            "Unexpected workflow failure for order %s",
            order_id
        )

        return {
            "success": False,
            "order_id": order_id,
            "error": "An unexpected workflow error occurred."
        }
