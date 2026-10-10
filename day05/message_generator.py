import os
from dotenv import load_dotenv
from ollama import Client

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

client = Client(
    host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
)


def generate_order_message(
    order: dict,
    decision: dict
) -> str:
    """
    Generate a customer-friendly order message.

    This function only creates a draft.
    It does not send any messages.
    """

    prompt = f"""
You are a professional WooCommerce support assistant.

Write a short customer-friendly order update.

Order details:
Order ID: {order['order_id']}
Status: {order['status']}
Total: {order['total']}
Currency: {order['currency']}

Internal recommendation:
{decision['reason']}

Rules:
- Use only the supplied order facts.
- Do not invent delivery dates or payment links.
- Do not promise that an action has been completed.
- Do not mention internal priorities or review thresholds.
- Do not request sensitive payment information.
- Keep the message under 80 words.
- Return only the customer message.
- Do not wrap the message in quotation marks.
- Do not use placeholders such as [Your Name].
- Do not promise shipping updates unless explicitly confirmed.
"""

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={"temperature": 0}
    )

    message = (response.message.content or "").strip()

    if (
        len(message) >= 2
        and message.startswith('"')
        and message.endswith('"')
    ):
        message = message[1:-1].strip()

    if not message:
        raise ValueError("Ollama returned an empty message.")

    return message
