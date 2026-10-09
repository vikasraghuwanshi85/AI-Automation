from day04.woocommerce_client import (
    WooCommerceClient,
    WooCommerceAPIError,
)


def main():
    client = WooCommerceClient()

    order_id = int(input("Enter a WooCommerce test order ID: "))

    try:
        order = client.get_order(order_id)
        print("\nWooCommerce API Response:")
        print(order)

    except WooCommerceAPIError as error:
        print(f"\nAPI Error: {error}")


if __name__ == "__main__":
    main()
