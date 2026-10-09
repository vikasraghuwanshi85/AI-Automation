
import json
import os

from dotenv import load_dotenv
from ollama import Client

from day04.woocommerce_client import (
    WooCommerceClient,
    WooCommerceAPIError,
)

load_dotenv()

# Connect to local Ollama.
ollama_client = Client(
    host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
)

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

# Connect to WooCommerce.
woo_client = WooCommerceClient()


def get_real_order(order_id: int) -> dict:
    """
    Retrieve an order from the real WooCommerce store.
    """
    try:
        return woo_client.get_order(int(order_id))

    except (ValueError, TypeError):
        return {
            "success": False,
            "error": "Invalid order ID",
        }

    except WooCommerceAPIError:
        return {
            "success": False,
            "error": "Unable to retrieve the order",
        }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_real_order",
            "description": (
                "Retrieve the current status, total, "
                "and currency of a WooCommerce order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "WooCommerce order ID",
                    }
                },
                "required": ["order_id"],
            },
        },
    }
]


def ask_real_order_assistant(question: str) -> str:
    """
    Ask Ollama about a real WooCommerce order.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a WooCommerce order support assistant. "
                "Use the get_real_order tool to retrieve order details. "
                "Never invent order status, total, or currency. "
                "If an order cannot be retrieved, explain that "
                "the information is unavailable."
            ),
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    response = ollama_client.chat(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )

    messages.append(response.message)

    tool_calls = response.message.tool_calls or []

    if not tool_calls:
        return response.message.content or (
            "Please provide a WooCommerce order ID."
        )

    for tool_call in tool_calls:

        if tool_call.function.name != "get_real_order":
            continue

        arguments = tool_call.function.arguments

        result = get_real_order(
            arguments.get("order_id")
        )

        messages.append(
            {
                "role": "tool",
                "tool_name": "get_real_order",
                "content": json.dumps(result),
            }
        )

    final_response = ollama_client.chat(
        model=MODEL,
        messages=messages,
    )

    return final_response.message.content or (
        "Unable to generate a response."
    )


if __name__ == "__main__":

    print("Real WooCommerce AI Order Assistant")
    print("Type 'exit' to quit.\n")

    while True:

        question = input("You: ").strip()

        if question.lower() in ("exit", "quit"):
            break

        if not question:
            continue

        try:
            answer = ask_real_order_assistant(question)
            print(f"\nAI: {answer}\n")

        except Exception as error:
            print(
                f"\nAssistant error: "
                f"{type(error).__name__}\n"
            )
