import os
import re
import json
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from ollama import Client
from pydantic import BaseModel, Field

# Load project configuration
load_dotenv()

client = Client(
    host=os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434"
    )
)

MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:latest"
)


# Define structured output
class LeadAnalysis(BaseModel):
    service: Literal[
        "wordpress",
        "woocommerce",
        "shopify",
        "custom_development",
        "other",
        "unknown"
    ]

    budget: float | None = Field(
        description="Budget amount, or null if missing"
    )

    currency: str | None = Field(
        description="ISO currency code, or null if unknown"
    )

    urgency: Literal[
        "low", "medium", "high", "unknown"
    ]

    intent: Literal[
        "hire_developer",
        "request_quote",
        "support",
        "general_inquiry",
        "spam"
    ]

    summary: str

def validate_urgency(message: str, lead: LeadAnalysis) -> LeadAnalysis:
    """Prevent unsupported urgency classifications."""

    text = message.lower()

    high_patterns = [
        r"\burgent(?:ly)?\b",
        r"\basap\b",
        r"\bimmediately\b",
        r"\bright away\b",
        r"\bwithin\s+(?:\d+|one|two)\s+(?:days?|weeks?)\b",
    ]

    has_high_urgency = any(
        re.search(pattern, text)
        for pattern in high_patterns
    )

    if lead.urgency == "high" and not has_high_urgency:
        # Conservative fallback until timeline extraction
        # and validation are implemented.
        lead.urgency = "unknown"

    return lead

def calculate_lead_score(lead: LeadAnalysis) -> int:
    if lead.intent == "spam":
        return 0

    score = 0

    # Customer intent
    if lead.intent == "hire_developer":
        score += 30
    elif lead.intent == "request_quote":
        score += 20

    # Requested service
    if lead.service in [
        "wordpress",
        "woocommerce",
        "custom_development"
    ]:
        score += 20

    # Budget (USD only)
    if lead.currency == "USD":
        if lead.budget is not None:
            if lead.budget >= 10000:
                score += 30
            elif lead.budget >= 5000:
                score += 15

    # Urgency
    if lead.urgency == "high":
        score += 20
    elif lead.urgency == "medium":
        score += 10

    return min(score, 100)


def classify_lead(score: int) -> str:
    if score >= 80:
        return "hot"
    elif score >= 50:
        return "warm"
    return "cold"


def recommend_action(score: int) -> str:
    if score >= 80:
        return "contact_immediately"
    elif score >= 50:
        return "send_followup_email"
    return "manual_review"


def analyze_lead(message: str) -> LeadAnalysis:
    
    SYSTEM_PROMPT = """
        You are a lead classification system for a
        WordPress and WooCommerce development agency.

        Extract accurate structured information.

        SERVICE RULES:
        - WooCommerce store or checkout = woocommerce
        - WordPress website = wordpress
        - Shopify store = shopify
        - Other software development = custom_development
        - If unclear = unknown

        INTENT RULES:
        - support:
        Customer reports an existing website problem,
        bug, error, broken feature, or requests a fix.

        - request_quote:
        Customer explicitly asks about pricing,
        estimates, quotations, or project costs.

        - hire_developer:
        Customer wants to build a new website,
        store, plugin, or software project.

        - general_inquiry:
        Customer asks a general question without
        requesting development, pricing, or support.

        - spam:
        Unsolicited advertising or irrelevant promotion.

        IMPORTANT:
        A customer asking "Can you fix this issue?"
        is SUPPORT, not REQUEST_QUOTE.

        URGENCY RULES:
        - high: Explicitly urgent, ASAP, immediately,
        or a deadline within 14 days.
        - medium: Deadline within 30 days.
        - low: Flexible timeline or beyond 30 days.
        - unknown: No explicit urgency or deadline.

        IMPORTANT:
        A broken checkout does NOT automatically
        mean high urgency. Do not infer urgency
        from the severity of the problem.

        BUDGET RULES:
        - Extract only explicitly stated amounts.
        - Missing budget = null.
        - Missing currency = null.
        - Never invent information.

        Return JSON matching the provided schema.
    """

    response = client.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ],
        format=LeadAnalysis.model_json_schema(),
        options={"temperature": 0}
    )

    return LeadAnalysis.model_validate_json(
        response.message.content
    )


if __name__ == "__main__":

    message = """
            Hello, my WooCommerce checkout page is not working.
            Customers cannot complete their orders.
            Can you help me fix this issue?
            """

    lead = analyze_lead(message)
    lead = validate_urgency(message, lead)
    score = calculate_lead_score(lead)

    result = lead.model_dump()

    result["lead_score"] = score
    result["lead_quality"] = classify_lead(score)
    result["recommended_action"] = recommend_action(score)
    print(json.dumps(result, indent=2))