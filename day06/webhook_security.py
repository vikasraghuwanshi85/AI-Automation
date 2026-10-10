import base64
import hashlib
import hmac
import os

def verify_woocommerce_signature(
    payload: bytes,
    received_signature: str | None
) -> bool:
    """
    Verify a WooCommerce webhook HMAC-SHA256 signature.

    payload: Raw HTTP request body.
    received_signature: X-WC-Webhook-Signature header.
    """

    secret = os.getenv("WOOCOMMERCE_WEBHOOK_SECRET")

    if not secret or not received_signature:
        return False

    digest = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).digest()

    expected_signature = base64.b64encode(
        digest
    ).decode("utf-8")

    return hmac.compare_digest(
        expected_signature,
        received_signature
    )
