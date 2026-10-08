
from fastapi import FastAPI
from pydantic import BaseModel, Field
from day02.order_assistant import run_assistant

from day01.lead_analyzer import (
    analyze_lead,
    validate_urgency,
    calculate_lead_score,
    classify_lead,
    recommend_action,
)

app = FastAPI(
    title="AI Automation API",
    description="AI-powered automation using Python and Ollama",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to AI Automation API"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "AI Automation API"
    }

# Request model
class LeadRequest(BaseModel):
    message: str = Field(min_length=10)



# Request model
class OrderQuestionRequest(BaseModel):
    question: str = Field(min_length=3)


# Response model
class OrderQuestionResponse(BaseModel):
    answer: str


# AI Order Assistant API
@app.post(
    "/ask-order",
    response_model=OrderQuestionResponse
)
def ask_order_endpoint(request: OrderQuestionRequest):

    answer = run_assistant(request.question)

    return {
        "answer": answer
    }


# AI Lead Analyzer endpoint
@app.post("/analyze-lead")
def analyze_lead_endpoint(request: LeadRequest):

    # Step 1: Analyze customer message using Ollama
    lead = analyze_lead(request.message)

    # Step 2: Validate AI-generated urgency
    lead = validate_urgency(request.message, lead)

    # Step 3: Calculate lead score
    score = calculate_lead_score(lead)

    # Step 4: Convert Pydantic object to dictionary
    result = lead.model_dump()

    # Step 5: Add calculated fields
    result["lead_score"] = score
    result["lead_quality"] = classify_lead(score)
    result["recommended_action"] = recommend_action(score)

    return result
