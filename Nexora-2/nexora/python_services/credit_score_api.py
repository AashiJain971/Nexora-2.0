from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
from typing import List, Dict
from credit_score import main as calculate_credit_score_main
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Allow CORS for all origins (can restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Data Models ----------------- #
class FinancialData(BaseModel):
    no_of_invoices: int = Field(..., ge=1, description="Number of invoices (>=1)")
    total_amount: float = Field(..., ge=0, description="Total invoice amount")
    total_amount_pending: float = Field(..., ge=0, description="Total pending amount")
    total_amount_paid: float = Field(..., ge=0, description="Total paid amount")
    tax: float = Field(..., ge=0, description="Total tax amount")
    extra_charges: float = Field(..., ge=0, description="Total extra charges")
    payment_completion_rate: float = Field(..., ge=0, le=1, description="Payment completion rate (0-1)")
    paid_to_pending_ratio: float = Field(..., ge=0, description="Paid to pending ratio")

class FactorBreakdown(BaseModel):
    actual_value: float
    individual_score: float
    weighted_score: float
    weight_percentage: int
    comment: str

class DetailedAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    risk_assessment: str
    creditworthiness_summary: List[str]

class Recommendations(BaseModel):
    immediate_actions: List[str]
    long_term_improvements: List[str]
    priority_focus_areas: List[str]

class CreditScoreAnalysis(BaseModel):
    final_weighted_credit_score: float
    score_category: str
    factor_breakdown: Dict[str, FactorBreakdown]
    detailed_analysis: DetailedAnalysis
    recommendations: Recommendations

class CreditScoreResponse(BaseModel):
    credit_score_analysis: CreditScoreAnalysis
    timestamp: str
    api_model: str

# ----------------- API Endpoints ----------------- #
@app.post("/calculate-credit-score", response_model=CreditScoreResponse)
async def calculate_credit_score_api(financial_data: FinancialData):
    """
    Calculate weighted credit score based on financial metrics.
    """
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment.")

    # Convert Pydantic model to dict
    financial_dict = financial_data.model_dump()
    print("Received financial data:", financial_dict)

    # Validate business logic
    if abs(financial_dict["total_amount_pending"] + financial_dict["total_amount_paid"] - financial_dict["total_amount"]) > 0.01:
        raise HTTPException(
            status_code=400, 
            detail="Total amount should equal sum of pending and paid amounts"
        )

    try:
        print("Starting credit score calculation...")
        result_json = calculate_credit_score_main(financial_dict, GROQ_API_KEY)

        if not result_json:
            raise HTTPException(status_code=500, detail="Credit score calculation returned empty result")

        print("Raw result from calculate_credit_score_main:", result_json)

        # Ensure valid JSON
        try:
            result_dict = json.loads(result_json)
        except json.JSONDecodeError as e:
            print("JSON parsing failed:", repr(e))
            raise HTTPException(status_code=500, detail=f"Failed to parse credit score response: {str(e)}")

        return CreditScoreResponse(**result_dict)

    except HTTPException:
        # Propagate HTTPExceptions
        raise
    except Exception as e:
        print("Exception during credit score calculation:", repr(e))
        raise HTTPException(status_code=500, detail=f"Internal calculation error: {str(e)}")


@app.get("/")
def root():
    return {
        "message": "Credit Score Analysis API. Submit financial data to get weighted credit score analysis.",
        "endpoints": {
            "calculate_credit_score": {
                "path": "/calculate-credit-score",
                "method": "POST",
                "description": "Calculate weighted credit score from financial metrics",
                "request": {
                    "no_of_invoices": "integer (>= 1)",
                    "total_amount": "number (>= 0)",
                    "total_amount_pending": "number (>= 0)",
                    "total_amount_paid": "number (>= 0)",
                    "tax": "number (>= 0)",
                    "extra_charges": "number (>= 0)",
                    "payment_completion_rate": "number (0-1)",
                    "paid_to_pending_ratio": "number (>= 0)"
                },
                "response": {
                    "credit_score_analysis": {
                        "final_weighted_credit_score": "number (0-100)",
                        "score_category": "string",
                        "factor_breakdown": {
                            "payment_completion_rate": "object",
                            "paid_to_pending_ratio": "object",
                            "tax_compliance": "object",
                            "extra_charges_management": "object"
                        },
                        "detailed_analysis": "object",
                        "recommendations": "object"
                    },
                    "timestamp": "string",
                    "api_model": "string"
                }
            }
        }
    }


@app.post("/upload-invoice/")
async def upload_invoice(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # Assuming you have a function to parse invoice image and calculate credit score
        # Example: parse_image_invoice -> returns financial_dict
        financial_dict = parse_image_invoice(contents)

        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

        # Call your existing main function with parsed data
        result_json = calculate_credit_score_main(financial_dict, GROQ_API_KEY)
        result_dict = json.loads(result_json)

        return result_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing invoice: {str(e)}")

