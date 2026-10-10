import json
import logging
from urllib.parse import parse_qs

from fastapi import (
    BackgroundTasks,
    FastAPI,
    Header,
    HTTPException,
    Request,
)
from dotenv import load_dotenv

from day05.workflow import run_order_workflow

from day06.webhook_security import (
    verify_woocommerce_signature,
)

load_dotenv()

app = FastAPI(
    title="Day 6 - WooCommerce Webhook Automation"
)

logger = logging.getLogger(__name__)


def process_order_event(order_id: int):
    """
    Run Day 5 automation after the webhook is accepted.
    """

    try:
        result = run_order_workflow(order_id)

        if result.get("success"):
            logger.info(
                "Workflow completed for order %s",
                order_id
            )
        else:
            logger.error(
                "Workflow failed for order %s: %s",
                order_id,
                result.get("error")
            )

    except Exception:
        logger.exception(
            "Unexpected failure processing order %s",
            order_id
        )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhooks/woocommerce")
async def woocommerce_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_wc_webhook_signature: str | None = Header(
        default=None
    ),
    x_wc_webhook_topic: str | None = Header(
        default=None
    ),
):
    
    
    # Step 1: Read the original request body.
    payload = await request.body()

    # WooCommerce activation ping uses form-encoded data.
    content_type = request.headers.get(
        "content-type", ""
    ).split(";")[0].strip().lower()

    if content_type == "application/x-www-form-urlencoded":

        form_data = parse_qs(
            payload.decode("utf-8", errors="replace")
        )

        webhook_ids = form_data.get("webhook_id", [])

        if (
            len(form_data) == 1
            and len(webhook_ids) == 1
            and webhook_ids[0].isdigit()
            and int(webhook_ids[0]) > 0
            and not x_wc_webhook_topic
            and not x_wc_webhook_signature
        ):
            return {
                "success": True,
                "message": "WooCommerce activation ping received"
            }

        raise HTTPException(
            status_code=400,
            detail="Unsupported form payload"
        )

    # Step 2: Verify signatures for normal order events.
    if not verify_woocommerce_signature(
        payload,
        x_wc_webhook_signature
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )

    # Step 3: Accept only supported order events.
    allowed_topics = {
        "order.created",
        "order.updated",
    }

    if x_wc_webhook_topic not in allowed_topics:
        return {
            "success": True,
            "message": "Webhook topic ignored"
        }

    # Step 4: Decode the JSON payload.
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="Expected a JSON object"
        )

    # Step 5: Validate the order ID.
    order_id = data.get("id")

    if (
        isinstance(order_id, bool)
        or not isinstance(order_id, int)
        or order_id <= 0
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid order ID"
        )

    # Step 6: Schedule the workflow.
    background_tasks.add_task(
        process_order_event,
        order_id
    )

    return {
        "success": True,
        "message": "Webhook accepted",
        "order_id": order_id
    }
