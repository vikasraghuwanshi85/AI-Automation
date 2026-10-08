import os
import json
from pathlib import Path
from dotenv import load_dotenv
from ollama import Client
from day02.tools import get_order_status, get_order_total

# Load environment variables
load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)


# Functions the AI is allowed to request
AVAILABLE_TOOLS = {
    "get_order_status": get_order_status,
    "get_order_total": get_order_total
}


def run_assistant(user_message: str) -> str:

    messages = [
        {
            "role": "system",
            "content": (
                "You are a WooCommerce order assistant. "
                "Use the available tools to retrieve order "
                "information. Never invent order details. "
                "If an order is missing, explain that it "
                "could not be found."
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    # Step 1: Ask Llama which tool to use
    response = client.chat(
        model=MODEL,
        messages=messages,
        tools=[
            get_order_status,
            get_order_total
        ],
        options={"temperature": 0}
    )

    messages.append(response.message)

    # Step 2: Execute requested tools
    tool_calls = response.message.tool_calls or []

    if not tool_calls:
        return response.message.content or (
            "I couldn't determine which order "
            "information you need."
        )

    for tool_call in tool_calls:

        function_name = tool_call.function.name
        arguments = tool_call.function.arguments

        print(f"AI requested: {function_name}")
        print(f"Arguments: {arguments}")

        # Allowlist: only approved functions
        function = AVAILABLE_TOOLS.get(function_name)

        if function is None:
            result = {
                "success": False,
                "error": "Unknown tool"
            }
        else:
            try:
                arguments["order_id"] = int(arguments["order_id"])
                result = function(**arguments)
            except (TypeError, ValueError) as error:
                result = {
                    "success": False,
                    "error": f"Invalid tool arguments: {error}"
                }

        # Step 3: Return tool result to the LLM
        messages.append({
            "role": "tool",
            "tool_name": function_name,
            "content": json.dumps(result)
        })

    # Step 4: Ask Llama to generate final answer
    final_response = client.chat(
        model=MODEL,
        messages=messages,
        options={"temperature": 0}
    )

    return final_response.message.content or (
        "No final response was generated."
    )


if __name__ == "__main__":

    question = input("Ask the WooCommerce order assistant a question( like What is the status of WooCommerce order 1003?): ")

    answer = run_assistant(question)

    print("\nFinal AI Answer:")
    print(answer)
