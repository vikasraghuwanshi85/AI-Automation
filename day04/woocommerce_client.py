
import os
from pathlib import Path
from urllib.parse import urlparse
import httpx
from dotenv import load_dotenv


# Load environment variables from the project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class WooCommerceAPIError(Exception):
    """Raised when a WooCommerce API request fails."""


class WooCommerceClient:
    """Read-only client for the WooCommerce REST API."""

    def __init__(
        self,
        base_url=None,
        consumer_key=None,
        consumer_secret=None,
    ):
        self.base_url = (
            base_url
            or os.getenv("WOOCOMMERCE_URL", "")
        ).rstrip("/")

        self.consumer_key = (
            consumer_key
            or os.getenv("WOOCOMMERCE_CONSUMER_KEY")
        )

        self.consumer_secret = (
            consumer_secret
            or os.getenv("WOOCOMMERCE_CONSUMER_SECRET")
        )

        # Validate required configuration
        if not all([
            self.base_url,
            self.consumer_key,
            self.consumer_secret,
        ]):
            raise ValueError(
                "WooCommerce API credentials are missing. "
                "Check your .env file."
            )
        
        parsed_url = urlparse(self.base_url)

        is_https = parsed_url.scheme == "https"

        is_local_http = (
            parsed_url.scheme == "http"
            and parsed_url.hostname in ("localhost", "127.0.0.1")
            and parsed_url.username is None
            and parsed_url.password is None
        )

        if not (is_https or is_local_http):
            raise ValueError(
                "WooCommerce URL must use HTTPS, "
                "except for local development."
            )

    def get_order(self, order_id: int) -> dict:
        """Retrieve an order from WooCommerce."""

        # Validate the order ID
        if type(order_id) is not int or order_id <= 0:
            raise ValueError(
                "Order ID must be a positive integer"
            )

        url = (
            f"{self.base_url}"
            f"/wp-json/wc/v3/orders/{order_id}"
        )

        try:
            response = httpx.get(
                url,
                auth=(
                    self.consumer_key,
                    self.consumer_secret,
                ),
                timeout=35.0,
                follow_redirects=False,
                verify=False,
            )

            # Handle missing orders
            # Only treat a WooCommerce order-not-found
            # response as a missing order.
            if response.status_code == 404:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {}

                if (
                    isinstance(error_data, dict)
                    and error_data.get("code")
                    == "woocommerce_rest_shop_order_invalid_id"
                ):
                    return {
                        "success": False,
                        "error": "Order not found",
                    }

            # Raise an exception for other HTTP errors
            response.raise_for_status()

            # Parse JSON response
            order = response.json()

            if not isinstance(order, dict):
                raise ValueError(
                    "Expected a JSON object"
                )

            # Validate required order fields
            required_fields = (
                "id",
                "status",
                "total",
                "currency",
            )

            for field in required_fields:
                if field not in order:
                    raise KeyError(field)

            # Return only necessary information
            return {
                "success": True,
                "order_id": order["id"],
                "status": order["status"],
                "total": order["total"],
                "currency": order["currency"],
            }

        except httpx.TimeoutException as error:
            raise WooCommerceAPIError(
                "WooCommerce API request timed out"
            ) from error

        except httpx.HTTPStatusError as error:
            status_code = error.response.status_code

            try:
                error_data = error.response.json()

                if isinstance(error_data, dict):
                    error_code = error_data.get(
                        "code",
                        "unknown"
                    )
                    error_message = error_data.get(
                        "message",
                        "Unknown API error"
                    )
                else:
                    error_code = "unknown"
                    error_message = (
                        "Unexpected API error format"
                    )

            except ValueError:
                error_code = "unknown"
                error_message = (
                    "Non-JSON API error response"
                )

            raise WooCommerceAPIError(
                f"WooCommerce API returned HTTP "
                f"{status_code}: "
                f"{error_code} - {error_message}"
            ) from error

        except httpx.RequestError as error:
            raise WooCommerceAPIError(
                "Unable to connect to WooCommerce"
            ) from error

        except (ValueError, KeyError, TypeError) as error:
            raise WooCommerceAPIError(
                "Invalid WooCommerce API response"
            ) from error
