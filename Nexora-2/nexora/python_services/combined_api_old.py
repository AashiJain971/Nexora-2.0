from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import shutil
import os
import json
import asyncio
import jwt
import bcrypt
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from invoice_2 import main as extract_invoice_main
from credit_score import main as calculate_credit_score_main
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Demo mode for development without database
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

if not DEMO_MODE:
    try:
        from supabase import create_client, Client
        
        # Supabase configuration
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
        
        if SUPABASE_URL and SUPABASE_ANON_KEY and SUPABASE_URL != "https://your-project-id.supabase.co":
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            print("Supabase client initialized successfully")
        else:
            print("Warning: Supabase credentials not found or not configured. Using demo mode.")
            supabase = None
            DEMO_MODE = True
    except ImportError:
        print("Warning: Supabase library not installed. Using demo mode.")
        supabase = None
        DEMO_MODE = True
else:
    print("Demo mode enabled - using in-memory storage")
    supabase = None

# In-memory storage for demo mode
# Demo data storage (replace with actual database)
demo_users = {}
demo_invoices = {}  # Store invoices with credit scores per user
demo_invoices = {}
user_counter = 1

app = FastAPI(title="Invoice Processing & Credit Score API", version="1.0.0")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5001", "http://127.0.0.1:5001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ----------------- Data Models ----------------- #
class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_data: Dict

class LineItem(BaseModel):
    description: str
    amount: float

class InvoiceDetails(BaseModel):
    invoice_number: str
    client: str
    date: str
    payment_terms: str
    industry: str
    total_amount: float
    currency: str
    line_items: List[LineItem]
    tax_amount: Optional[float] = None
    extra_charges: Optional[float] = None

class InvoiceResponse(BaseModel):
    invoice_details: InvoiceDetails
    total_line_items: int

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

class ProcessInvoiceResponse(BaseModel):
    invoice_details: InvoiceDetails
    total_line_items: int
    credit_score_analysis: CreditScoreAnalysis
    historical_summary: Dict

# ----------------- Helper Functions ----------------- #
def categorize_invoice_value(amount: float) -> str:
    """Categorize invoice value for credit analysis."""
    if amount >= 100000:
        return "high_value"
    elif amount >= 50000:
        return "medium_value"
    elif amount >= 10000:
        return "standard_value"
    else:
        return "low_value"

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jwt.PyJWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user_id

async def process_single_invoice(image: UploadFile, groq_api_key: str) -> dict:
    """Process a single invoice image."""
    if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail=f"File {image.filename} must be a PNG or JPG image")

    temp_image_path = f"temp_{image.filename}"
    try:
        with open(temp_image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        print("Extracting invoice...")
        result_json = extract_invoice_main(temp_image_path, groq_api_key)
        print(f"Processed {image.filename}: {result_json}")
        return json.loads(result_json)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process {image.filename}: {str(e)}")
    finally:
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

async def store_invoice_data(invoice_details: dict, user_id: str) -> bool:
    """Store invoice data in database for specific user."""
    if DEMO_MODE:
        # Demo mode - use in-memory storage
        if user_id not in demo_invoices:
            demo_invoices[user_id] = []
        
        # Calculate tax and extra charges from line items if not provided
        line_items = invoice_details.get("line_items", [])
        total_line_amount = sum(float(item.get("amount", 0)) for item in line_items)
        total_amount = float(invoice_details.get("total_amount", 0))
        
        # Estimate tax and extra charges if not explicitly provided
        tax_amount = float(invoice_details.get("tax_amount", 0))
        extra_charges = float(invoice_details.get("extra_charges", 0))
        
        # If tax/extra charges not provided, estimate based on total vs line items
        if tax_amount == 0 and extra_charges == 0 and total_amount > total_line_amount:
            difference = total_amount - total_line_amount
            # Assume 80% of difference is tax, 20% is extra charges
            tax_amount = difference * 0.8
            extra_charges = difference * 0.2
        
        invoice_data = {
            "id": len(demo_invoices[user_id]) + 1,
            "user_id": user_id,
            "invoice_number": invoice_details.get("invoice_number"),
            "client": invoice_details.get("client"),
            "date": invoice_details.get("date"),
            "payment_terms": invoice_details.get("payment_terms"),
            "industry": invoice_details.get("industry"),
            "total_amount": total_amount,
            "currency": invoice_details.get("currency"),
            "tax_amount": tax_amount,
            "extra_charges": extra_charges,
            "line_items": line_items,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",  # Initially all invoices are pending
            # Additional fields for credit score calculation
            "payment_completion_rate_factor": total_amount,  # Contributes to total volume
            "tax_compliance_ratio": tax_amount / total_amount if total_amount > 0 else 0,
            "extra_charges_ratio": extra_charges / total_amount if total_amount > 0 else 0,
            "invoice_value_category": categorize_invoice_value(total_amount)
        }
        
        demo_invoices[user_id].append(invoice_data)
        print(f"Stored invoice in demo mode for user {user_id}: #{invoice_data['invoice_number']} - ${total_amount}")
        return True
    
    # Database mode
    if not supabase:
        print("Supabase not configured, skipping database storage")
        return False
    
    try:
        # Prepare data for database storage
        invoice_data = {
            "user_id": user_id,
            "invoice_number": invoice_details.get("invoice_number"),
            "client": invoice_details.get("client"),
            "date": invoice_details.get("date"),
            "payment_terms": invoice_details.get("payment_terms"),
            "industry": invoice_details.get("industry"),
            "total_amount": float(invoice_details.get("total_amount", 0)),
            "currency": invoice_details.get("currency"),
            "tax_amount": float(invoice_details.get("tax_amount", 0)),
            "extra_charges": float(invoice_details.get("extra_charges", 0)),
            "line_items": invoice_details.get("line_items", []),
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending"  # Initially all invoices are pending
        }
        
        result = supabase.table("invoices").insert(invoice_data).execute()
        return True
    except Exception as e:
        print(f"Error storing invoice data: {str(e)}")
        return False

async def get_historical_financial_data(user_id: str) -> dict:
    """Get historical financial data from database for specific user to calculate credit score."""
    if DEMO_MODE:
        # Demo mode - use in-memory storage
        if user_id not in demo_invoices:
            demo_invoices[user_id] = []
        
        invoices = demo_invoices[user_id]
        
        if not invoices:
            # No historical data, return default values for first invoice
            return {
                "no_of_invoices": 0,
                "total_amount": 0,
                "total_amount_pending": 0,
                "total_amount_paid": 0,
                "tax": 0,
                "extra_charges": 0,
                "payment_completion_rate": 0.7,  # Default reasonable rate
                "paid_to_pending_ratio": 2.33   # Default reasonable ratio
            }
        
        # Calculate aggregated financial metrics from actual stored invoices
        total_invoices = len(invoices)
        total_amount = sum(float(inv.get("total_amount", 0)) for inv in invoices)
        total_tax = sum(float(inv.get("tax_amount", 0)) for inv in invoices)
        total_extra_charges = sum(float(inv.get("extra_charges", 0)) for inv in invoices)
        
        # Use consistent payment simulation based on user ID (deterministic)
        # This ensures same user gets same results each time
        user_hash = hash(user_id) % 100
        base_payment_rate = 0.6 + (user_hash / 100) * 0.3  # Between 0.6 and 0.9
        
        total_paid = total_amount * base_payment_rate if total_amount > 0 else 0
        total_pending = total_amount - total_paid
        
        payment_completion_rate = base_payment_rate
        paid_to_pending_ratio = total_paid / total_pending if total_pending > 0 else 4.0
        
        print(f"Historical data for user {user_id}: {total_invoices} invoices, payment_rate: {payment_completion_rate:.3f}")
        
        return {
            "no_of_invoices": total_invoices,
            "total_amount": total_amount,
            "total_amount_pending": total_pending,
            "total_amount_paid": total_paid,
            "tax": total_tax,
            "extra_charges": total_extra_charges,
            "payment_completion_rate": payment_completion_rate,
            "paid_to_pending_ratio": paid_to_pending_ratio
        }
    
    # Database mode
    if not supabase:
        print("Supabase not configured, using default values")
        return {
            "no_of_invoices": 1,
            "total_amount": 0,
            "total_amount_pending": 0,
            "total_amount_paid": 0,
            "tax": 0,
            "extra_charges": 0,
            "payment_completion_rate": 0.8,  # Default good score
            "paid_to_pending_ratio": 4.0
        }
    
    try:
        # Query invoices from database for specific user
        result = supabase.table("invoices").select("*").eq("user_id", user_id).execute()
        
        invoices = result.data if result.data else []
        
        if not invoices:
            # No historical data, return default values with good assumptions for new user
            return {
                "no_of_invoices": 1,
                "total_amount": 0,
                "total_amount_pending": 0,
                "total_amount_paid": 0,
                "tax": 0,
                "extra_charges": 0,
                "payment_completion_rate": 0.8,  # Assume good payment history for new users
                "paid_to_pending_ratio": 4.0
            }
        
        # Calculate aggregated financial metrics
        total_invoices = len(invoices)
        total_amount = sum(float(inv.get("total_amount", 0)) for inv in invoices)
        total_tax = sum(float(inv.get("tax_amount", 0)) for inv in invoices)
        total_extra_charges = sum(float(inv.get("extra_charges", 0)) for inv in invoices)
        
        # Calculate paid vs pending amounts
        paid_invoices = [inv for inv in invoices if inv.get("status") == "paid"]
        pending_invoices = [inv for inv in invoices if inv.get("status") == "pending"]
        
        total_paid = sum(float(inv.get("total_amount", 0)) for inv in paid_invoices)
        total_pending = sum(float(inv.get("total_amount", 0)) for inv in pending_invoices)
        
        # Calculate ratios
        payment_completion_rate = len(paid_invoices) / total_invoices if total_invoices > 0 else 0.8
        paid_to_pending_ratio = total_paid / total_pending if total_pending > 0 else (4.0 if total_paid > 0 else 2.0)
        
        return {
            "no_of_invoices": total_invoices,
            "total_amount": total_amount,
            "total_amount_pending": total_pending,
            "total_amount_paid": total_paid,
            "tax": total_tax,
            "extra_charges": total_extra_charges,
            "payment_completion_rate": payment_completion_rate,
            "paid_to_pending_ratio": paid_to_pending_ratio
        }
        
    except Exception as e:
        print(f"Error retrieving historical data: {str(e)}")
        # Return good default values on error
        return {
            "no_of_invoices": 1,
            "total_amount": 0,
            "total_amount_pending": 0,
            "total_amount_paid": 0,
            "tax": 0,
            "extra_charges": 0,
            "payment_completion_rate": 0.8,
            "paid_to_pending_ratio": 4.0
        }

# ----------------- API Endpoints ----------------- #
@app.post("/register", response_model=Token)
async def register_user(user: UserRegistration):
    """Register a new user"""
    global user_counter
    
    if DEMO_MODE:
        # Demo mode - use in-memory storage
        if user.email in demo_users:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user
        hashed_password = hash_password(user.password)
        user_id = str(user_counter)
        user_counter += 1
        
        demo_users[user.email] = {
            "id": user_id,
            "email": user.email,
            "full_name": user.full_name,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Initialize empty invoice list for user
        demo_invoices[user_id] = []
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_data": {
                "id": user_id,
                "email": user.email,
                "full_name": user.full_name
            }
        }
    
    # Database mode
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        # Check if user already exists
        existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user
        hashed_password = hash_password(user.password)
        user_data = {
            "email": user.email,
            "full_name": user.full_name,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("users").insert(user_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(result.data[0]["id"])}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_data": {
                "id": result.data[0]["id"],
                "email": user.email,
                "full_name": user.full_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login", response_model=Token)
async def login_user(user: UserLogin):
    """Login user"""
    if DEMO_MODE:
        # Demo mode - use in-memory storage
        if user.email not in demo_users:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        db_user = demo_users[user.email]
        
        # Verify password
        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user["id"]}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_data": {
                "id": db_user["id"],
                "email": db_user["email"],
                "full_name": db_user["full_name"]
            }
        }
    
    # Database mode
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        # Get user from database
        result = supabase.table("users").select("*").eq("email", user.email).execute()
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        db_user = result.data[0]
        
        # Verify password
        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user["id"])}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_data": {
                "id": db_user["id"],
                "email": db_user["email"],
                "full_name": db_user["full_name"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/add-sample-invoices")
async def add_sample_invoices(current_user: str = Depends(get_current_user)):
    """Add sample invoices for demo purposes"""
    if not DEMO_MODE:
        raise HTTPException(status_code=400, detail="Only available in demo mode")
    
    sample_invoices = [
        {
            "invoice_number": "INV-2024-001",
            "client": "ABC Electronics Ltd",
            "date": "2024-01-15",
            "payment_terms": "Net 30",
            "industry": "Electronics",
            "total_amount": 25000,
            "currency": "USD",
            "tax_amount": 3750,
            "extra_charges": 250,
            "line_items": [
                {"description": "Product Development Services", "amount": 20000},
                {"description": "Consulting Hours", "amount": 5000}
            ]
        },
        {
            "invoice_number": "INV-2024-002",
            "client": "XYZ Manufacturing",
            "date": "2024-02-20",
            "payment_terms": "Net 15",
            "industry": "Manufacturing",
            "total_amount": 45000,
            "currency": "USD",
            "tax_amount": 6750,
            "extra_charges": 450,
            "line_items": [
                {"description": "Equipment Setup", "amount": 30000},
                {"description": "Training Services", "amount": 15000}
            ]
        },
        {
            "invoice_number": "INV-2024-003",
            "client": "Tech Solutions Inc",
            "date": "2024-03-10",
            "payment_terms": "Net 45",
            "industry": "Technology",
            "total_amount": 15000,
            "currency": "USD",
            "tax_amount": 2250,
            "extra_charges": 150,
            "line_items": [
                {"description": "Software Development", "amount": 12000},
                {"description": "Testing Services", "amount": 3000}
            ]
        }
    ]
    
    # Store sample invoices
    for invoice_data in sample_invoices:
        await store_invoice_data(invoice_data, current_user)
    
    return {"message": f"Added {len(sample_invoices)} sample invoices for user {current_user}"}

@app.get("/user/invoices")
async def get_user_invoices(current_user: str = Depends(get_current_user)):
    """Get all invoices for the current user"""
    if DEMO_MODE:
        # Demo mode - use in-memory storage
        if current_user not in demo_invoices:
            demo_invoices[current_user] = []
        
        # Return invoices sorted by creation date (most recent first)
        invoices = sorted(demo_invoices[current_user], 
                         key=lambda x: x.get('created_at', ''), 
                         reverse=True)
        
        return {
            "invoices": invoices,
            "total_count": len(invoices)
        }
    
    # Database mode
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        result = supabase.table("invoices").select("*").eq("user_id", current_user).order("created_at", desc=True).execute()
        return {
            "invoices": result.data or [],
            "total_count": len(result.data or [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@app.post("/extract-invoice", response_model=InvoiceResponse)
async def extract_invoice(image: UploadFile = File(...)):
    """Extract invoice details from an invoice image."""
    if not image:
        raise HTTPException(status_code=400, detail="No image provided")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment.")

    try:
        print("Starting extraction...")
        extraction = await process_single_invoice(image, GROQ_API_KEY)
        print(f"Extraction result: {extraction}")
        return InvoiceResponse(**extraction)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invoice extraction failed: {str(e)}")

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
    print("📊 Received financial data for credit score calculation:", financial_dict)

    # More lenient validation - allow for pending amounts that might not equal total
    total_reported = financial_dict["total_amount_pending"] + financial_dict["total_amount_paid"]
    total_expected = financial_dict["total_amount"]
    
    if abs(total_reported - total_expected) > total_expected * 0.1:  # Allow 10% variance
        print(f"⚠️ Warning: Total amount mismatch - Expected: {total_expected}, Got: {total_reported}")
        # Adjust rather than fail
        if financial_dict["total_amount_pending"] == 0:
            financial_dict["total_amount_pending"] = total_expected - financial_dict["total_amount_paid"]
        elif financial_dict["total_amount_paid"] == 0:
            financial_dict["total_amount_paid"] = max(0, total_expected - financial_dict["total_amount_pending"])

    try:
        print("🚀 Starting credit score calculation...")
        print(f"📈 Final financial data being sent:", financial_dict)
        
        result_json = calculate_credit_score_main(financial_dict, GROQ_API_KEY)

        if not result_json:
            print("❌ Credit score calculation returned empty result")
            raise HTTPException(status_code=500, detail="Credit score calculation returned empty result")

        print("✅ Raw result from calculate_credit_score_main:", result_json)

        # Ensure valid JSON
        try:
            result_dict = json.loads(result_json)
            print("✅ Successfully parsed JSON result:", result_dict)
        except json.JSONDecodeError as e:
            print("❌ JSON parsing failed:", repr(e))
            print("❌ Raw result that failed to parse:", result_json)
            raise HTTPException(status_code=500, detail=f"Failed to parse credit score response: {str(e)}")

        return CreditScoreResponse(**result_dict)

    except HTTPException:
        # Propagate HTTPExceptions
        raise
    except Exception as e:
        print("❌ Exception during credit score calculation:", repr(e))
        import traceback
        print("❌ Full traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal calculation error: {str(e)}")

@app.post("/calculate-single-invoice-credit-score", response_model=CreditScoreResponse)
async def calculate_single_invoice_credit_score_api(financial_data: FinancialData):
    """
    Calculate credit score for a single invoice only (not cumulative).
    This is used for individual invoice analysis on the homepage.
    """
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment.")

    # Convert Pydantic model to dict
    financial_dict = financial_data.model_dump()
    print("Received single invoice financial data:", financial_dict)

    # For single invoice, create isolated financial data
    single_invoice_data = {
        "no_of_invoices": 1,  # Always 1 for single invoice analysis
        "total_amount": financial_dict["total_amount"],
        "total_amount_pending": financial_dict["total_amount"],  # New invoice is always pending initially
        "total_amount_paid": 0,  # New invoice hasn't been paid yet
        "tax": financial_dict.get("tax", 0),
        "extra_charges": financial_dict.get("extra_charges", 0),
        "payment_completion_rate": 0.7,  # Default reasonable rate for new invoice
        "paid_to_pending_ratio": 0.5   # Default reasonable ratio for new invoice
    }

    try:
        print("Starting single invoice credit score calculation...")
        result_json = calculate_credit_score_main(single_invoice_data, GROQ_API_KEY)

        if not result_json:
            raise HTTPException(status_code=500, detail="Single invoice credit score calculation returned empty result")

        print("Raw result from single invoice calculate_credit_score_main:", result_json)

        # Ensure valid JSON
        try:
            result_dict = json.loads(result_json)
        except json.JSONDecodeError as e:
            print("JSON parsing failed:", repr(e))
            raise HTTPException(status_code=500, detail=f"Failed to parse single invoice credit score response: {str(e)}")

        return CreditScoreResponse(**result_dict)

    except HTTPException:
        # Propagate HTTPExceptions
        raise
    except Exception as e:
        print("Exception during single invoice credit score calculation:", repr(e))
        raise HTTPException(status_code=500, detail=f"Single invoice calculation error: {str(e)}")

@app.post("/process-invoice", response_model=ProcessInvoiceResponse)
async def process_invoice_with_credit_score(image: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    """
    Process invoice: extract details, store in database, and calculate credit score based on historical data.
    Requires authentication.
    """
    if not image:
        raise HTTPException(status_code=400, detail="No image provided")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment.")

    try:
        # Step 1: Extract invoice details
        print("Starting invoice extraction...")
        extraction = await process_single_invoice(image, GROQ_API_KEY)
        invoice_details = extraction["invoice_details"]
        
        print(f"Extracted invoice details: {invoice_details}")
        
        # Step 2: Store invoice data in database for current user
        await store_invoice_data(invoice_details, current_user)
        
        # Step 3: Get historical financial data for current user
        historical_data = await get_historical_financial_data(current_user)
        
        # Include current invoice in the totals
        current_amount = float(invoice_details.get("total_amount", 0))
        current_tax = float(invoice_details.get("tax_amount", 0))
        current_extra_charges = float(invoice_details.get("extra_charges", 0))
        
        # Update historical data with current invoice
        total_amount_with_current = historical_data["total_amount"] + current_amount
        total_pending_with_current = historical_data["total_amount_pending"] + current_amount
        
        financial_data = {
            "no_of_invoices": historical_data["no_of_invoices"] + 1,
            "total_amount": total_amount_with_current,
            "total_amount_pending": total_pending_with_current,
            "total_amount_paid": historical_data["total_amount_paid"],
            "tax": historical_data["tax"] + current_tax,
            "extra_charges": historical_data["extra_charges"] + current_extra_charges,
            "payment_completion_rate": historical_data["total_amount_paid"] / total_amount_with_current if total_amount_with_current > 0 else historical_data["payment_completion_rate"],
            "paid_to_pending_ratio": historical_data["total_amount_paid"] / total_pending_with_current if total_pending_with_current > 0 else historical_data["paid_to_pending_ratio"]
        }
        
        print(f"Financial data for credit score: {financial_data}")
        
        # Step 4: Calculate credit score
        print("Starting credit score calculation...")
        result_json = calculate_credit_score_main(financial_data, GROQ_API_KEY)
        
        if not result_json:
            raise HTTPException(status_code=500, detail="Credit score calculation returned empty result")
        
        try:
            credit_score_result = json.loads(result_json)
        except json.JSONDecodeError as e:
            print("JSON parsing failed:", repr(e))
            raise HTTPException(status_code=500, detail=f"Failed to parse credit score response: {str(e)}")
        
        # Step 4.5: Store invoice with credit score
        if current_user not in demo_invoices:
            demo_invoices[current_user] = []
        
        # Calculate individual invoice credit score
        single_invoice_financial = {
            "no_of_invoices": 1,
            "total_amount": invoice_details["total_amount"],
            "total_amount_pending": invoice_details["total_amount"],
            "total_amount_paid": 0,
            "tax": invoice_details["tax_amount"],
            "extra_charges": invoice_details["extra_charges"],
            "payment_completion_rate": 0.7,
            "paid_to_pending_ratio": 0.5
        }
        
        single_result_json = calculate_credit_score_main(single_invoice_financial, GROQ_API_KEY)
        single_credit_score = 0
        if single_result_json:
            try:
                single_result = json.loads(single_result_json)
                single_credit_score = single_result["credit_score_analysis"]["final_weighted_credit_score"]
            except:
                single_credit_score = 0
        
        # Store invoice with individual credit score
        invoice_record = {
            "id": len(demo_invoices[current_user]) + 1,
            "invoice_number": invoice_details["invoice_number"],
            "client": invoice_details["client"],
            "total_amount": invoice_details["total_amount"],
            "tax_amount": invoice_details["tax_amount"],
            "extra_charges": invoice_details["extra_charges"],
            "status": "pending",
            "credit_score": single_credit_score,
            "created_at": datetime.utcnow().isoformat()
        }
        
        demo_invoices[current_user].append(invoice_record)
        print(f"✅ Stored invoice with credit score {single_credit_score}")
        
        # Step 5: Return combined response
        return ProcessInvoiceResponse(
            invoice_details=InvoiceDetails(**invoice_details),
            total_line_items=len(invoice_details.get("line_items", [])),
            credit_score_analysis=CreditScoreAnalysis(**credit_score_result["credit_score_analysis"]),
            historical_summary={
                "total_historical_invoices": historical_data["no_of_invoices"],
                "historical_payment_rate": historical_data["payment_completion_rate"],
                "user_id": current_user,
                "financial_data_used": financial_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Exception during invoice processing: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Invoice processing failed: {str(e)}")

@app.get("/user/invoices")
async def get_user_invoices(current_user: str = Depends(get_current_user)):
    """Get all invoices for the current user"""
    if current_user not in demo_invoices:
        return {"invoices": [], "total_count": 0}
    
    user_invoices = demo_invoices[current_user]
    return {
        "invoices": user_invoices,
        "total_count": len(user_invoices)
    }

@app.get("/dashboard/credit-score")
async def get_dashboard_credit_score(current_user: str = Depends(get_current_user)):
    """Get dashboard credit score calculated as mean of all invoice credit scores"""
    try:
        print(f"📊 Fetching dashboard credit score for user: {current_user}")
        
        if current_user not in demo_invoices or not demo_invoices[current_user]:
            return {
                "credit_score": 0,
                "category": "No Data",
                "total_invoices": 0,
                "last_updated": "No invoices uploaded yet",
                "loading": False,
                "error": None
            }
        
        invoices = demo_invoices[current_user]
        credit_scores = [inv.get("credit_score", 0) for inv in invoices if inv.get("credit_score") is not None]
        
        if not credit_scores:
            mean_credit_score = 0
            category = "No Data"
        else:
            mean_credit_score = sum(credit_scores) / len(credit_scores)
            # Determine category based on mean score
            if mean_credit_score >= 80:
                category = "Excellent"
            elif mean_credit_score >= 70:
                category = "Good"
            elif mean_credit_score >= 60:
                category = "Fair"
            else:
                category = "Poor"
        
        print(f"✅ Dashboard credit score calculated: {mean_credit_score:.1f} ({category})")
        
        return {
            "credit_score": round(mean_credit_score, 1),
            "category": category,
            "total_invoices": len(invoices),
            "last_updated": datetime.now().strftime("%m/%d/%Y"),
            "loading": False,
            "error": None,
            "debug_info": {
                "individual_scores": credit_scores,
                "mean_calculation": f"{sum(credit_scores)}/{len(credit_scores)}" if credit_scores else "0/0",
                "invoice_count": len(invoices)
            }
        }
        
    except Exception as e:
        print(f"❌ Dashboard credit score error: {e}")
        return {
            "credit_score": 0,
            "category": "Error", 
            "total_invoices": 0,
            "last_updated": "Error occurred",
            "loading": False,
            "error": str(e)
        }

@app.get("/")
def root():
    return {
        "message": "Combined Invoice Processing & Credit Score API with Authentication",
        "version": "1.0.0",
        "endpoints": {
            "register": {
                "path": "/register",
                "method": "POST",
                "description": "Register a new user",
                "request": {
                    "email": "string",
                    "password": "string",
                    "full_name": "string"
                }
            },
            "login": {
                "path": "/login",
                "method": "POST",
                "description": "Login user",
                "request": {
                    "email": "string",
                    "password": "string"
                }
            },
            "user_invoices": {
                "path": "/user/invoices",
                "method": "GET",
                "description": "Get all invoices for authenticated user",
                "headers": {
                    "Authorization": "Bearer <token>"
                }
            },
            "extract_invoice": {
                "path": "/extract-invoice",
                "method": "POST",
                "description": "Upload an invoice image to extract structured details",
                "request": {
                    "image": "file (PNG, JPG, JPEG)"
                }
            },
            "process_invoice": {
                "path": "/process-invoice",
                "method": "POST",
                "description": "Process invoice: extract details, store in database, and calculate credit score (requires authentication)",
                "headers": {
                    "Authorization": "Bearer <token>"
                },
                "request": {
                    "image": "file (PNG, JPG, JPEG)"
                }
            },
            "calculate_credit_score": {
                "path": "/calculate-credit-score", 
                "method": "POST",
                "description": "Calculate credit score from financial data",
                "request": {
                    "no_of_invoices": "integer (>= 1)",
                    "total_amount": "number (>= 0)",
                    "total_amount_pending": "number (>= 0)",
                    "total_amount_paid": "number (>= 0)",
                    "tax": "number (>= 0)",
                    "extra_charges": "number (>= 0)",
                    "payment_completion_rate": "number (0-1)",
                    "paid_to_pending_ratio": "number (>= 0)"
                }
            }
        }
    }

@app.get("/debug/demo-invoices")
async def get_demo_invoices_debug(current_user: str = Depends(get_current_user)):
    """Debug endpoint to check current state of demo_invoices"""
    return {
        "demo_mode": DEMO_MODE,
        "current_user": current_user,
        "all_users": list(demo_invoices.keys()),
        "user_invoice_count": len(demo_invoices.get(current_user, [])),
        "user_invoices": demo_invoices.get(current_user, [])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
