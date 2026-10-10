
import json
from day05.workflow import run_order_workflow

def main():
    print("\nDay 5 - WooCommerce AI Automation")
    print("--------------------------------")

    order_input = input(
        "Enter WooCommerce order ID: "
    ).strip()

    try:
        order_id = int(order_input)

        if order_id <= 0:
            raise ValueError

    except ValueError:
        print("Please enter a valid positive order ID.")
        return

    result = run_order_workflow(order_id)

    print("\nWorkflow Result:")
    print(
        json.dumps(
            result,
            indent=4
        )
    )


if __name__ == "__main__":
    main()
