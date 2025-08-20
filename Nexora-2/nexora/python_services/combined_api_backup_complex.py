#!/usr/bin/env python3
"""
Nexora Credit Score API - Supabase Database Only
This version uses only Supabase database, no in-memory storage
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header, Form
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
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from invoice_2 import main as extract_invoice_main
from credit_score import main as calculate_credit_score_main
from dotenv import load_dotenv
from supabase import create_client, Client
import uvicorn
from pathlib import Path
from uuid import uuid4

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://eecbqzvcnwrkcxgwjxlt.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVlY2JxenZjbndya2N4Z3dqeGx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0Mjk1NjEsImV4cCI6MjA3MTAwNTU2MX0.CkhFT-6LKFg6NCc9WIiZRjNQ7VGVX6nJmoOxjMVHDKs")

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Supabase client initialized successfully")
    print(f"📊 Connected to: {SUPABASE_URL}")
except Exception as e:
    print(f"❌ Failed to initialize Supabase: {e}")
    raise

app = FastAPI(title="Nexora Credit Score API - Supabase", version="2.0.0")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_secret_key_please_change_in_production_12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5001", "http://127.0.0.1:5001","https://nexora-2-0-5.onrender.com"],
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

# ----------------- Insurance Hub Data Models ----------------- #
class InsuranceAssessmentRequest(BaseModel):
    business_type: str
    assets: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs of asset categories to their estimated values")
    workforce_size: Optional[int] = 0
    risk_concerns: List[str] = Field(default_factory=list)
    region: Optional[str] = "India"
    annual_revenue: Optional[float] = None
    preferences: Optional[Dict[str, Any]] = None  # e.g. {"focus": "employee_welfare", "budget_level": "medium"}

class InsurancePolicyCreate(BaseModel):
    business_id: int
    policy_name: str
    policy_type: str
    provider_name: Optional[str] = None
    coverage_amount: float
    premium_amount: float
    premium_range: Optional[str] = None
    legal_compliance: Optional[bool] = True
    compliance_authority: Optional[str] = "IRDAI"
    start_date: datetime
    expiry_date: datetime
    policy_number: Optional[str] = None
    coverage_details: Optional[Dict[str, Any]] = None
    exclusions: Optional[Dict[str, Any]] = None
    optional_addons: Optional[Dict[str, Any]] = None

class InsurancePolicyUpdate(BaseModel):
    coverage_amount: Optional[float] = None
    premium_amount: Optional[float] = None
    premium_range: Optional[str] = None
    status: Optional[str] = None
    expiry_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    policy_number: Optional[str] = None
    document_url: Optional[str] = None
    coverage_details: Optional[Dict[str, Any]] = None
    exclusions: Optional[Dict[str, Any]] = None
    optional_addons: Optional[Dict[str, Any]] = None

class AdvisorConnectRequest(BaseModel):
    topic: str
    details: Optional[str] = None
    urgency: Optional[str] = "normal"  # 'low', 'normal', 'high'
    preferred_contact: Optional[str] = "email"

# ----------------- Helper Functions ----------------- #
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# ----------------- Database Initialization ----------------- #
def init_database_tables():
    """Initialize database tables using raw SQL"""
    try:
        print("🔧 Initializing Supabase database tables...")
        
        # Check if tables exist by querying them
        try:
            # Try to select from users table
            result = supabase.table('users').select('id').limit(1).execute()
            print("✅ Users table already exists")
        except:
            print("📋 Creating users table...")
            # Table doesn't exist, it will be created via SQL schema
        
        try:
            # Try to select from invoices table  
            result = supabase.table('invoices').select('id').limit(1).execute()
            print("✅ Invoices table already exists")
        except:
            print("📋 Creating invoices table...")
            # Table doesn't exist, it will be created via SQL schema
        # Optional: probe insurance tables (do not fail if missing yet)
        for tbl in ["insurance_policies", "insurance_templates", "business_risk_assessments", "policy_reminders"]:
            try:
                supabase.table(tbl).select('count').limit(1).execute()
                print(f"✅ {tbl} table available")
            except Exception:
                print(f"ℹ️ {tbl} table not found yet (run insurance_policies_schema.sql if you need Insurance Hub)")
            
        print("✅ Database initialization completed!")
        
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        print("💡 Please run the SQL schema in your Supabase SQL editor if tables don't exist")

# Initialize database on startup
init_database_tables()

# ----------------- API Endpoints ----------------- #

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Nexora Credit Score API - Supabase Database",
        "version": "2.0.0",
        "database": "Supabase",
        "status": "operational",
        "endpoints": {
            "register": "/register",
            "login": "/login", 
            "upload": "/upload-invoice",
            "dashboard": "/dashboard/credit-score",
            "invoices": "/user/invoices"
        }
    }

@app.post("/register", response_model=Token)
async def register_user(user: UserRegistration):
    """Register a new user in Supabase"""
    try:
        print(f"📝 Attempting to register user: {user.email}")
        
        # Check if user already exists
        existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user
        hashed_password = hash_password(user.password)
        user_data = {
            "email": user.email,
            "full_name": user.full_name,
            "password_hash": hashed_password
        }
        
        # Insert user into database
        result = supabase.table("users").insert(user_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        created_user = result.data[0]
        print(f"✅ User registered successfully: {created_user['email']} (ID: {created_user['id']})")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(created_user["id"])}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_data": {
                "id": str(created_user["id"]),
                "email": created_user["email"],
                "full_name": created_user["full_name"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login", response_model=Token)
async def login_user(user: UserLogin):
    """Login user with Supabase database"""
    try:
        print(f"🔐 Attempting login for user: {user.email}")
        
        # Get user from database
        result = supabase.table("users").select("*").eq("email", user.email).execute()
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        db_user = result.data[0]
        
        # Verify password
        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        print(f"✅ Login successful for user: {db_user['email']} (ID: {db_user['id']})")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user["id"])}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_data": {
                "id": str(db_user["id"]),
                "email": db_user["email"],
                "full_name": db_user["full_name"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/upload-invoice")
async def process_invoice(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Process uploaded invoice and store in Supabase with credit score"""
    try:
        print(f"📄 Processing invoice upload for user: {current_user}")
        
        # Save uploaded file temporarily
        temp_file_path = f"temp_invoice_{current_user}_{datetime.now().timestamp()}.{file.filename.split('.')[-1]}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract invoice details
        print("🔍 Extracting invoice details...")
        invoice_result_raw = await asyncio.to_thread(extract_invoice_main, temp_file_path, GROQ_API_KEY)
        
        # The invoice_2.py returns a JSON string, so we need to parse it
        try:
            if isinstance(invoice_result_raw, str):
                invoice_result = json.loads(invoice_result_raw)
            else:
                invoice_result = invoice_result_raw
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing invoice result JSON: {e}")
            raise HTTPException(status_code=400, detail="Invoice extraction returned invalid JSON")
        
        if not invoice_result.get("invoice_details"):
            raise HTTPException(status_code=400, detail=f"Invoice extraction failed: No invoice details found")
        
        invoice_details = invoice_result["invoice_details"]
        print(f"✅ Invoice extracted: {invoice_details.get('invoice_number', 'Unknown')}")

        # --- Sanitize and truncate string fields to fit DB constraints ---
        def _truncate(val, max_len):
            if val is None:
                return None
            s = str(val)
            return s[:max_len]

        # Log original lengths for debugging
        debug_lengths = {
            'invoice_number_len': len(str(invoice_details.get('invoice_number', ''))),
            'client_len': len(str(invoice_details.get('client', ''))),
            'payment_terms_len': len(str(invoice_details.get('payment_terms', ''))),
            'industry_len': len(str(invoice_details.get('industry', ''))),
            'currency_len': len(str(invoice_details.get('currency', '')))
        }
        print(f"🔎 Field lengths before truncation: {debug_lengths}")

        # Apply truncation according to supabase_schema.sql
        invoice_number = _truncate(invoice_details.get('invoice_number', 'INV-UNKNOWN'), 255)
        client = _truncate(invoice_details.get('client', 'Unknown Client'), 255)
        payment_terms = _truncate(invoice_details.get('payment_terms', 'Not specified'), 255)
        industry = _truncate(invoice_details.get('industry', 'General'), 255)
        # Currency limited to 20 chars; keep only first 10 non-space chars typical codes
        raw_currency = _truncate(invoice_details.get('currency', 'INR'), 20)
        # Normalize currency to uppercase short code if it's long descriptive text
        if len(raw_currency) > 10:
            # Extract potential code (letters only) from beginning
            import re as _re
            match = _re.search(r"[A-Za-z]{3,5}", raw_currency.upper())
            currency = match.group(0) if match else raw_currency[:10].upper()
        else:
            currency = raw_currency.upper()
        print(f"💱 Normalized currency: '{raw_currency}' -> '{currency}'")
        
        # Get all existing invoices for user to calculate historical data & detect duplicates
        existing_invoices = supabase.table('invoices').select('*').eq('user_id', int(current_user)).execute()
        total_invoices = len(existing_invoices.data) if existing_invoices.data else 0

        # Duplicate detection (idempotent behavior)
        # We'll sanitize the invoice number first (same logic used later) to compare apples-to-apples
        raw_invoice_number = invoice_details.get("invoice_number", "INV-UNKNOWN")
        sanitized_invoice_number = str(raw_invoice_number)[:255]
        duplicate_invoice = None
        if existing_invoices.data:
            for inv in existing_invoices.data:
                if inv.get('invoice_number') == sanitized_invoice_number:
                    duplicate_invoice = inv
                    break

        if duplicate_invoice:
            print("⚠️ Duplicate invoice upload detected; returning existing record without re-processing credit score")
            # Clean up temp file early
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return {
                "success": True,
                "message": "Invoice already processed previously; returning existing record",
                "invoice_details": {
                    "id": duplicate_invoice["id"],
                    "invoice_number": duplicate_invoice["invoice_number"],
                    "client": duplicate_invoice["client"],
                    "total_amount": duplicate_invoice["total_amount"],
                    "credit_score": duplicate_invoice.get("credit_score")
                },
                "credit_score_analysis": duplicate_invoice.get("credit_score_data", {}),
                "historical_summary": {
                    "total_historical_invoices": total_invoices,
                    "total_amount_all_invoices": sum([inv['total_amount'] for inv in existing_invoices.data]) if existing_invoices.data else 0
                },
                "duplicate": True
            }
        
        # Calculate total amounts for credit score calculation
        total_amount = sum([inv['total_amount'] for inv in existing_invoices.data]) if existing_invoices.data else 0
        invoice_total = float(invoice_details.get('total_amount', 0))
        total_amount += invoice_total
        
        # Calculate credit score for this invoice
        print("📊 Calculating credit score...")
        credit_score_data = {
            "no_of_invoices": total_invoices + 1,
            "total_amount": total_amount,
            "total_amount_pending": invoice_total,  # New invoice is pending
            "total_amount_paid": total_amount - invoice_total,
            "tax": float(invoice_details.get('tax_amount', 0)),
            "extra_charges": float(invoice_details.get('extra_charges', 0)),
            "payment_completion_rate": 0.8,  # Default assumption
            "paid_to_pending_ratio": 0.6     # Default assumption
        }
        
        credit_score_result = await asyncio.to_thread(calculate_credit_score_main, credit_score_data, GROQ_API_KEY)
        # The credit_score_main returns a JSON string; parse if needed
        try:
            if isinstance(credit_score_result, str):
                credit_score_result_parsed = json.loads(credit_score_result)
            else:
                credit_score_result_parsed = credit_score_result
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing credit score JSON: {e}")
            credit_score_result_parsed = {"credit_score_analysis": {}}

        individual_credit_score = (
            credit_score_result_parsed
                .get('credit_score_analysis', {})
                .get('final_weighted_credit_score', 0)
        )
        
        print(f"✅ Individual credit score calculated: {individual_credit_score}")
        
        # Prepare invoice data for database
        invoice_db_data = {
            "user_id": int(current_user),
            "invoice_number": invoice_number,
            "client": client,
            "date": invoice_details.get("date"),
            "payment_terms": payment_terms,
            "industry": industry,
            "total_amount": invoice_total,
            "currency": currency,
            "tax_amount": float(invoice_details.get("tax_amount", 0)),
            "extra_charges": float(invoice_details.get("extra_charges", 0)),
            "line_items": invoice_details.get("line_items", []),
            "status": "pending",
            "credit_score": individual_credit_score,
            "credit_score_data": credit_score_result_parsed.get('credit_score_analysis', {})
        }
        print("🧹 Sanitized invoice payload prepared for DB insert")
        
        # Insert invoice into database
        print("💾 Saving invoice to Supabase...")
        try:
            result = supabase.table("invoices").insert(invoice_db_data).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to save invoice to database")
        except Exception as insert_error:
            # Handle duplicate race condition (if another request inserted same invoice between detection & insert)
            if 'duplicate key value' in str(insert_error) or '23505' in str(insert_error):
                print("⚠️ Duplicate detected at insert time (race). Fetching existing record.")
                existing = supabase.table('invoices').select('*').eq('user_id', int(current_user)).eq('invoice_number', invoice_db_data['invoice_number']).limit(1).execute()
                if existing.data:
                    saved_invoice = existing.data[0]
                    # Clean up temp
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                    return {
                        "success": True,
                        "message": "Invoice already existed; returning existing record",
                        "invoice_details": {
                            "id": saved_invoice["id"],
                            "invoice_number": saved_invoice["invoice_number"],
                            "client": saved_invoice["client"],
                            "total_amount": saved_invoice["total_amount"],
                            "credit_score": saved_invoice.get("credit_score")
                        },
                        "credit_score_analysis": saved_invoice.get("credit_score_data", {}),
                        "historical_summary": {
                            "total_historical_invoices": total_invoices,
                            "total_amount_all_invoices": sum([inv['total_amount'] for inv in existing_invoices.data]) if existing_invoices.data else 0
                        },
                        "duplicate": True
                    }
            # Re-raise if not handled duplicate
            raise
        
        saved_invoice = result.data[0]
        print(f"✅ Invoice saved to database with ID: {saved_invoice['id']}")
        
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        return {
            "success": True,
            "message": "Invoice processed and saved successfully",
            "invoice_details": {
                "id": saved_invoice["id"],
                "invoice_number": saved_invoice["invoice_number"],
                "client": saved_invoice["client"],
                "total_amount": saved_invoice["total_amount"],
                "credit_score": saved_invoice["credit_score"]
            },
            "credit_score_analysis": credit_score_result_parsed.get('credit_score_analysis', {}),
            "historical_summary": {
                "total_historical_invoices": total_invoices + 1,
                "total_amount_all_invoices": total_amount
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file in case of error
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        print(f"❌ Invoice processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Invoice processing failed: {str(e)}")

@app.post("/process-invoice")
async def upload_invoice_alias(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Alias endpoint for frontend compatibility - same as /upload-invoice"""
    return await process_invoice(file, current_user)

@app.post("/calculate-credit-score")
async def calculate_credit_score_alias(credit_data: dict):
    """Alias endpoint for frontend compatibility - calculate credit score (no auth required for testing)"""
    try:
        print("📊 Calculating credit score...")
        result = await asyncio.to_thread(calculate_credit_score_main, credit_data, GROQ_API_KEY)
        print("✅ Credit score calculated")
        return result
    except Exception as e:
        print(f"❌ Credit score calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Credit score calculation failed: {str(e)}")

@app.get("/dashboard/credit-score")
async def get_dashboard_credit_score(current_user: str = Depends(get_current_user)):
    """Get dashboard credit score calculated as mean of all invoice credit scores from Supabase"""
    try:
        print(f"📊 Fetching dashboard credit score for user: {current_user}")
        
        # Get all invoices with credit scores for the user
        result = supabase.table('invoices').select('*').eq('user_id', int(current_user)).execute()
        invoices = result.data or []
        
        if not invoices:
            return {
                "credit_score": 0,
                "category": "No Data",
                "total_invoices": 0,
                "last_updated": "No invoices uploaded yet",
                "loading": False,
                "error": None
            }
        
        # Calculate mean credit score from all invoices
        credit_scores = [inv['credit_score'] for inv in invoices if inv['credit_score'] is not None]
        
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
        
        print(f"✅ Dashboard credit score calculated from Supabase: {mean_credit_score:.1f} ({category})")
        
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
                "invoice_count": len(invoices),
                "database": "Supabase"
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

@app.get("/user/invoices")
async def get_user_invoices(current_user: str = Depends(get_current_user)):
    """Get all invoices for the current user from Supabase"""
    try:
        print(f"📋 Fetching invoices for user: {current_user}")
        
        # Get all invoices for the user, ordered by creation date
        result = supabase.table('invoices').select('*').eq('user_id', int(current_user)).order('created_at', desc=True).execute()
        invoices = result.data or []
        
        print(f"✅ Retrieved {len(invoices)} invoices from Supabase")
        
        return {
            "success": True,
            "invoices": invoices,
            "total_count": len(invoices)
        }
        
    except Exception as e:
        print(f"❌ Error fetching user invoices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@app.post("/calculate-single-invoice-credit-score")
async def calculate_single_invoice_credit_score(credit_data: dict):
    """Calculate credit score for a single invoice (utility endpoint)"""
    try:
        print("📊 Calculating single invoice credit score...")
        result = await asyncio.to_thread(calculate_credit_score_main, credit_data, GROQ_API_KEY)
        print("✅ Single invoice credit score calculated")
        return result
    except Exception as e:
        print(f"❌ Single invoice credit score calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Credit score calculation failed: {str(e)}")

@app.get("/get-business")
async def get_business(current_user: str = Depends(get_current_user)):
    """Get business information for the current user"""
    try:
        print(f"🏢 Fetching business info for user: {current_user}")
        
        # Get user data which might include business info
        result = supabase.table('users').select('*').eq('id', int(current_user)).execute()
        user_data = result.data[0] if result.data else {}
        
        # Mock business data structure - in production this would be a separate businesses table
        business_data = {
            "business_name": user_data.get("full_name", "Business Name"),
            "industry": "Technology",
            "revenue": 1000000,
            "employees": 50,
            "location": "Mumbai, India",
            "established_year": 2020
        }
        
        return {"success": True, "business": business_data}
    except Exception as e:
        print(f"❌ Error fetching business info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch business info: {str(e)}")

@app.post("/register-business")
async def register_business(business: dict, current_user: str = Depends(get_current_user)):
    """Register or update business details for the current user.
    Currently stores data inside the users table (mock) until a dedicated businesses table usage is added.
    """
    try:
        print(f"🏢 Saving business info for user: {current_user}")
        # Basic validation
        if not business.get("business_name"):
            raise HTTPException(status_code=400, detail="Business name is required")

        # Upsert strategy: store limited business fields in users table's full_name (or later extend schema)
        # Placeholder: we just acknowledge receipt
        return {"success": True, "message": "Business details received", "business": business}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error registering business: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register business: {str(e)}")

def generate_policy_content(policy_type: str, business: dict, language: str = "en") -> str:
    """
    Generate realistic policy content based on business details and policy type.
    This creates comprehensive, legally-informed policies tailored to the specific business.
    Supports multiple languages: en, hi, es, fr
    """
    business_name = business.get('business_name', 'Your Business')
    business_type = business.get('business_type', 'business')
    industry = business.get('industry', 'general')
    location_country = business.get('location_country', 'India')
    website_url = business.get('website_url', f'www.{business_name.lower().replace(" ", "")}.com')
    has_online_presence = business.get('has_online_presence', False)
    processes_payments = business.get('processes_payments', False)
    uses_cookies = business.get('uses_cookies', False)
    collects_personal_data = business.get('collects_personal_data', True)
    target_audience = business.get('target_audience', 'B2C')
    data_retention_period = business.get('data_retention_period', 365)
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Language-specific translations
    translations = {
        'en': {
            'privacy_policy': 'PRIVACY POLICY',
            'effective_date': 'Effective Date',
            'last_updated': 'Last Updated',
            'introduction': 'INTRODUCTION',
            'welcome_text': f'Welcome to **{business_name}**',
            'info_we_collect': 'INFORMATION WE COLLECT',
            'personal_info': 'Personal Information',
            'how_we_use': 'HOW WE USE YOUR INFORMATION',
            'data_security': 'DATA SECURITY',
            'contact_info': 'CONTACT INFORMATION'
        },
        'hi': {
            'privacy_policy': 'गोपनीयता नीति',
            'effective_date': 'प्रभावी तिथि',
            'last_updated': 'अंतिम बार अपडेट',
            'introduction': 'परिचय',
            'welcome_text': f'**{business_name}** में आपका स्वागत है',
            'info_we_collect': 'हम जो जानकारी एकत्र करते हैं',
            'personal_info': 'व्यक्तिगत जानकारी',
            'how_we_use': 'हम आपकी जानकारी का उपयोग कैसे करते हैं',
            'data_security': 'डेटा सुरक्षा',
            'contact_info': 'संपर्क जानकारी'
        },
        'es': {
            'privacy_policy': 'POLÍTICA DE PRIVACIDAD',
            'effective_date': 'Fecha de vigencia',
            'last_updated': 'Última actualización',
            'introduction': 'INTRODUCCIÓN',
            'welcome_text': f'Bienvenido a **{business_name}**',
            'info_we_collect': 'INFORMACIÓN QUE RECOPILAMOS',
            'personal_info': 'Información Personal',
            'how_we_use': 'CÓMO USAMOS SU INFORMACIÓN',
            'data_security': 'SEGURIDAD DE DATOS',
            'contact_info': 'INFORMACIÓN DE CONTACTO'
        },
        'fr': {
            'privacy_policy': 'POLITIQUE DE CONFIDENTIALITÉ',
            'effective_date': 'Date d\'entrée en vigueur',
            'last_updated': 'Dernière mise à jour',
            'introduction': 'INTRODUCTION',
            'welcome_text': f'Bienvenue chez **{business_name}**',
            'info_we_collect': 'INFORMATIONS QUE NOUS COLLECTONS',
            'personal_info': 'Informations Personnelles',
            'how_we_use': 'COMMENT NOUS UTILISONS VOS INFORMATIONS',
            'data_security': 'SÉCURITÉ DES DONNÉES',
            'contact_info': 'INFORMATIONS DE CONTACT'
        }
    }
    
    # Get translations for the selected language, fallback to English
    t = translations.get(language, translations['en'])
    
    if policy_type == 'privacy_policy':
        if language == 'hi':  # Hindi
            return f"""# {t['privacy_policy']}

**{t['effective_date']}:** {current_date}  
**{t['last_updated']}:** {current_date}

---

## {t['introduction']}

{t['welcome_text']} ("{business_name.lower()}", "हम", "हमारा", या "हमारे"). यह गोपनीयता नीति बताती है कि हम कैसे आपकी जानकारी एकत्र, उपयोग, प्रकटीकरण और सुरक्षा करते हैं जब आप {"हमारी वेबसाइट " + website_url + " पर जाते हैं या " if has_online_presence else ""}हमारी सेवाओं का उपयोग करते हैं.

**{business_name}** एक {business_type} व्यवसाय है जो {industry} उद्योग में काम कर रहा है, मुख्य रूप से {target_audience.lower()} ग्राहकों की सेवा कर रहा है{"" if location_country == "India" else f" और {location_country} में संचालन के साथ"}.

कृपया इस गोपनीयता नीति को ध्यान से पढ़ें. हमारी सेवाओं का उपयोग या पहुंच करके, आप स्वीकार करते हैं कि आपने इस गोपनीयता नीति की शर्तों को पढ़ा, समझा और सहमति दी है.

---

## {t['info_we_collect']}

### {t['personal_info']}
हम व्यक्तिगत रूप से पहचान योग्य जानकारी एकत्र कर सकते हैं जो आप स्वेच्छा से हमें प्रदान करते हैं जब आप:
- {"खाता पंजीकरण करते हैं या हमारी सेवाओं का उपयोग करते हैं" if has_online_presence else "हमारी सेवाओं के साथ जुड़ते हैं"}
- हमसे पूछताछ के लिए संपर्क करते हैं
- {"खरीदारी करते हैं या लेन-देन प्रक्रिया करते हैं" if processes_payments else "हमारी सेवाओं के बारे में जानकारी का अनुरोध करते हैं"}
- हमारे न्यूज़लेटर या संचार की सदस्यता लेते हैं
- सर्वेक्षण या प्रचार में भाग लेते हैं

**व्यक्तिगत जानकारी के प्रकार:**
- नाम और संपर्क जानकारी (ईमेल, फोन, पता)
- {"भुगतान और बिलिंग जानकारी" if processes_payments else "व्यावसायिक संपर्क विवरण"}
- {"खाता प्रमाण-पत्र और प्राथमिकताएं" if has_online_presence else "सेवा प्राथमिकताएं"}
- संचार रिकॉर्ड और पत्राचार
- {"जनसांख्यिकीय और रुचि डेटा" if target_audience == "B2C" else "व्यावसायिक जानकारी और आवश्यकताएं"}

### गैर-व्यक्तिगत जानकारी
जब आप हमारी सेवाओं के साथ बातचीत करते हैं तो हम स्वचालित रूप से कुछ गैर-व्यक्तिगत जानकारी एकत्र करते हैं:
- {"ब्राउज़र प्रकार, डिवाइस जानकारी, और ऑपरेटिंग सिस्टम" if has_online_presence else "उपयोग पैटर्न और सेवा इंटरैक्शन"}
- {"आईपी पता और सामान्य स्थान डेटा" if uses_cookies else "सामान्य स्थान जानकारी"}
- {"वेबसाइट उपयोग डेटा, पेज व्यूज़, और नेविगेशन पैटर्न" if has_online_presence and uses_cookies else "सेवा उपयोग आंकड़े"}
- {"कुकीज़ और ट्रैकिंग तकनीक डेटा" if uses_cookies else "अज्ञात उपयोग विश्लेषण"}

---

## {t['how_we_use']}

हम निम्नलिखित वैध व्यावसायिक उद्देश्यों के लिए आपकी जानकारी का उपयोग करते हैं:

### सेवा वितरण
- हमारी {business_type} सेवाओं का प्रावधान और रखरखाव
- {"लेन-देन और भुगतान की प्रक्रिया" if processes_payments else "सेवा अनुरोधों की प्रक्रिया"}
- {"आपके खाते और उपयोगकर्ता अनुभव का प्रबंधन" if has_online_presence else "व्यक्तिगत सेवा प्रदान करना"}
- आपकी पूछताछ और सहायता अनुरोधों का जवाब देना

### व्यावसायिक संचालन
- हमारी सेवाओं में सुधार और नई पेशकश विकसित करना
- बाजार अनुसंधान और विश्लेषण करना
- {"आपके अनुभव और सिफारिशों को व्यक्तिगत बनाना" if target_audience == "B2C" else "व्यावसायिक समाधान अनुकूलित करना"}
- सुरक्षा सुनिश्चित करना और धोखाधड़ी को रोकना

---

## {t['data_security']}

हम आपकी व्यक्तिगत जानकारी की सुरक्षा के लिए उद्योग-मानक सुरक्षा उपाय लागू करते हैं:

### तकनीकी सुरक्षा उपाय
- {"डेटा ट्रांसमिशन के लिए SSL/TLS एन्क्रिप्शन" if has_online_presence else "डेटा स्टोरेज और ट्रांसमिशन के लिए एन्क्रिप्शन"}
- सुरक्षित सर्वर और संरक्षित डेटाबेस
- नियमित सुरक्षा ऑडिट और भेद्यता मूल्यांकन
- {"खाता पहुंच के लिए मल्टी-फैक्टर प्रमाणीकरण" if has_online_presence else "पहुंच नियंत्रण और प्रमाणीकरण उपाय"}

---

## डेटा प्रतिधारण

हम आपकी व्यक्तिगत जानकारी को तब तक बनाए रखते हैं जब तक कि इस गोपनीयता नीति में उल्लिखित उद्देश्यों को पूरा करना आवश्यक हो, आमतौर पर **{data_retention_period} दिन** जब तक कि:
- कानून द्वारा एक लंबी अवधारण अवधि आवश्यक नहीं है
- आप अपनी जानकारी को हटाने का अनुरोध नहीं करते
- जानकारी कानूनी दावों या अनुपालन के लिए आवश्यक नहीं है
- {"आप हमारे साथ एक सक्रिय खाता बनाए रखते हैं" if has_online_presence else "आप हमारी सेवाओं का उपयोग जारी रखते हैं"}

---

## {t['contact_info']}

यदि आपके पास इस गोपनीयता नीति या हमारी डेटा प्रथाओं के संबंध में प्रश्न, चिंताएं या अनुरोध हैं, तो कृपया हमसे संपर्क करें:

**{business_name}**
- **ईमेल:** privacy@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **पता:** {business_name} गोपनीयता कार्यालय, {location_country}
- **फोन:** {"हमारी वेबसाइट पर दी गई जानकारी के माध्यम से हमसे संपर्क करें" if has_online_presence else "प्रदान की गई व्यावसायिक जानकारी के माध्यम से संपर्क करें"}

{location_country}-विशिष्ट गोपनीयता चिंताओं या नियामक पूछताछ के लिए, कृपया अपने पत्राचार में अपना स्थान शामिल करें.

---

**यह गोपनीयता नीति लागू डेटा सुरक्षा कानूनों के साथ अनुपालित है जिसमें {"भारतीय आईटी अधिनियम 2000, जीडीपीआर (जहां लागू हो), और " if location_country == "India" else ""}संबंधित गोपनीयता नियम {location_country} में शामिल हैं.**

*अंतिम समीक्षा और अपडेट: {current_date}*"""
        
        else:  # English (default)
            return f"""# {t['privacy_policy']}

**{t['effective_date']}:** {current_date}  
**{t['last_updated']}:** {current_date}

---

## {t['introduction']}

{t['welcome_text']} ("{business_name.lower()}", "we", "us", "our"). This Privacy Policy outlines how we collect, use, disclose, and safeguard your information when you {"visit our website " + website_url + " or " if has_online_presence else ""}use our services.

**{business_name}** is a {business_type} business operating in the {industry} industry, primarily serving {target_audience.lower()} customers{"" if location_country == "India" else f" with operations in {location_country}"}.

Please read this Privacy Policy carefully. By using or accessing our services, you acknowledge that you have read, understood, and agree to be bound by the terms of this Privacy Policy.

---

## {t['info_we_collect']}

We collect information to provide better services to our users and operate our business effectively.

### {t['personal_info']}
- Name, email address, and contact information
- {"Account credentials and login information" if has_online_presence else "Service-related identification"}
- {"Payment information and billing details" if processes_payments else "Business transaction details"}
- Communication preferences and history

### Usage and Technical Information
- {"Website usage data, IP address, and browser information" if has_online_presence else "Service usage patterns and technical data"}
- {"Cookies and similar tracking technologies" if uses_cookies else "Session and preference data"}
- Device information and access logs
- Service interaction and performance data

### Business Information
- Company details and business requirements
- Service preferences and customizations
- Feedback and support communications
- {"Analytics and marketing preferences" if target_audience == "B2C" else "Business communication preferences"}

---

## {t['how_we_use']}

We use your information for the following legitimate business purposes:

### Service Delivery
- Providing and maintaining our {business_type} services
- Processing {"transactions and payments" if processes_payments else "service requests"}
- {"Managing your account and user experience" if has_online_presence else "Delivering personalized service"}
- Responding to your inquiries and support requests

### Business Operations
- Improving our services and developing new offerings
- Conducting market research and analytics
- {"Personalizing your experience and recommendations" if target_audience == "B2C" else "Customizing business solutions"}
- Ensuring security and preventing fraud

### Legal and Compliance
- Complying with applicable laws and regulations
- {"Processing payments and maintaining financial records" if processes_payments else "Maintaining business records"}
- Protecting our rights and interests
- Responding to legal requests and preventing misuse

### Communication
- Sending service-related notifications and updates
- {"Marketing communications (with your consent)" if target_audience == "B2C" else "Business communications and updates"}
- Newsletter and promotional content (with opt-out options)
- Important policy or service changes

---

## INFORMATION SHARING AND DISCLOSURE

We do not sell, rent, or trade your personal information. We may share your information in the following limited circumstances:

### Service Providers
We work with trusted third-party service providers who assist us in operating our business:
- {"Payment processors and financial institutions" if processes_payments else "Business service providers"}
- {"Cloud hosting and data storage providers" if has_online_presence else "Data storage and backup services"}
- {"Analytics and marketing service providers" if uses_cookies else "Business analytics providers"}
- Professional service providers (legal, accounting, consulting)

### Legal Requirements
We may disclose your information when required by law or to:
- Comply with legal obligations and court orders
- Protect and defend our rights and interests
- Prevent fraud and ensure platform security
- Respond to government requests and investigations

### Business Transfers
In the event of a merger, acquisition, or sale of our business, your information may be transferred to the new entity, subject to the same privacy protections.

---

## {t['data_security']}

We implement industry-standard security measures to protect your personal information:

### Technical Safeguards
- {"SSL/TLS encryption for data transmission" if has_online_presence else "Encryption for data storage and transmission"}
- Secure servers and protected databases
- Regular security audits and vulnerability assessments
- {"Multi-factor authentication for account access" if has_online_presence else "Access controls and authentication measures"}

### Organizational Safeguards
- Limited access on a need-to-know basis
- Employee training on data protection
- Clear data handling and retention policies
- Incident response and breach notification procedures

### Physical Safeguards
- Secure facilities and equipment
- {"Restricted access to servers and data centers" if has_online_presence else "Protected data storage locations"}
- Proper disposal of physical media
- Environmental controls and monitoring

---

## DATA RETENTION

We retain your personal information for as long as necessary to fulfill the purposes outlined in this Privacy Policy, typically **{data_retention_period} days** unless:
- A longer retention period is required by law
- You request deletion of your information
- The information is necessary for legal claims or compliance
- {"You maintain an active account with us" if has_online_presence else "You continue to use our services"}

---

## YOUR PRIVACY RIGHTS

Depending on your location, you may have the following rights regarding your personal information:

### Access and Portability
- Request access to your personal information
- Receive a copy of your data in a portable format
- {"Download your account information" if has_online_presence else "Request your service records"}

### Correction and Updates
- Correct inaccurate or incomplete information
- Update your contact preferences
- {"Modify your account settings" if has_online_presence else "Update your service preferences"}

### Deletion and Restriction
- Request deletion of your personal information
- Restrict certain processing activities
- {"Close your account and delete associated data" if has_online_presence else "Discontinue services and data processing"}

### Objection and Withdrawal
- Object to certain types of processing
- Withdraw consent for optional data processing
- Opt-out of marketing communications

**To exercise these rights, please contact us using the information provided below.**

---

## CHILDREN'S PRIVACY

Our services are not directed to children under the age of 13{" (or 16 in certain jurisdictions)" if location_country in ["European Union", "UK", "Germany"] else ""}. We do not knowingly collect personal information from children. If you believe we have inadvertently collected information from a child, please contact us immediately.

---

## INTERNATIONAL DATA TRANSFERS

{"If you are located outside of " + location_country + ", please note that your information may be transferred to and processed in " + location_country + " where our servers and business operations are located. We ensure appropriate safeguards are in place for such transfers." if location_country != "India" else "Your information is primarily processed within India. If international transfers are necessary, we ensure appropriate legal safeguards are in place."}

---

## UPDATES TO THIS POLICY

We may update this Privacy Policy periodically to reflect changes in our practices or legal requirements. We will notify you of material changes by:
- {"Posting updates on our website" if has_online_presence else "Sending you direct notifications"}
- Email notifications for significant changes
- {"In-app notifications" if has_online_presence else "Service communications"}

The updated policy will be effective immediately upon posting, and your continued use of our services constitutes acceptance of the revised terms.

---

## {t['contact_info']}

If you have questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:

**{business_name}**
- **Email:** privacy@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Address:** {business_name} Privacy Office, {location_country}
- **Phone:** {"Contact us through the information provided on our website" if has_online_presence else "Contact through provided business information"}

For {location_country}-specific privacy concerns or regulatory inquiries, please include your location in your correspondence.

---

**This Privacy Policy is compliant with applicable data protection laws including {"the Indian IT Act 2000, GDPR (where applicable), and " if location_country == "India" else ""}relevant privacy regulations in {location_country}.**

*Last reviewed and updated: {current_date}*"""

    elif policy_type == 'terms_conditions':
        if language == 'hi':  # Hindi
            return f"""# नियम और शर्तें

**{t['effective_date']}:** {current_date}  
**{t['last_updated']}:** {current_date}

---

## शर्तों की स्वीकृति

**{business_name}** में आपका स्वागत है. ये नियम और शर्तें ("शर्तें") हमारी {business_type} सेवाओं {"और वेबसाइट " + website_url if has_online_presence else "और सेवाओं"} के आपके उपयोग को नियंत्रित करती हैं. हमारी सेवाओं का उपयोग या पहुंच करके, आप इन शर्तों से बंधे होने के लिए सहमत हैं.

यदि आप इन शर्तों से सहमत नहीं हैं, तो कृपया हमारी सेवाओं का उपयोग न करें.

---

## सेवाओं का विवरण

**{business_name}** एक {business_type} कंपनी है जो {industry} उद्योग में काम कर रही है. हम प्रदान करते हैं:

{"### डिजिटल सेवाएं" + chr(10) + "- ऑनलाइन प्लेटफॉर्म पहुंच और कार्यक्षमता" + chr(10) + "- उपयोगकर्ता खाता प्रबंधन" + chr(10) + "- डिजिटल सामग्री और संसाधन" if has_online_presence else "### व्यावसायिक सेवाएं"}
- {industry.title()} समाधान और विशेषज्ञता
- {"भुगतान प्रसंस्करण और लेन-देन सेवाएं" if processes_payments else "परामर्श और पेशेवर सेवाएं"}
- ग्राहक सहायता और तकनीकी सहायता
- {"अनुकूलित व्यावसायिक समाधान" if target_audience == "B2B" else "उपभोक्ता-केंद्रित सेवाएं"}

---

## उपयोगकर्ता जिम्मेदारियां

### खाता प्रबंधन
{"- सटीक खाता जानकारी बनाए रखें" + chr(10) + "- अपने लॉगिन प्रमाण-पत्रों की सुरक्षा करें" + chr(10) + "- अनधिकृत पहुंच के बारे में हमें सूचित करें" if has_online_presence else "- सटीक संपर्क जानकारी प्रदान करें" + chr(10) + "- हमारी टीम के साथ संचार बनाए रखें"}
- लागू कानूनों और नियमों का अनुपालन करें
- केवल वैध उद्देश्यों के लिए सेवाओं का उपयोग करें

### निषिद्ध गतिविधियां
आप सहमत हैं कि आप निम्नलिखित नहीं करेंगे:
- {"किसी भी कानून का उल्लंघन या दूसरों के अधिकारों का हनन" + chr(10) + "- दुर्भावनापूर्ण सामग्री या स्पैम अपलोड करना" if has_online_presence else "धोखाधड़ी या भ्रामक प्रथाओं में संलग्न होना"}
- हमारी सेवाओं या सिस्टम में हस्तक्षेप करना
- {"हमारे सॉफ़्टवेयर को रिवर्स इंजीनियर करना या कॉपी करना" if has_online_presence else "मालिकाना जानकारी का दुरुपयोग करना"}
- {"दूसरों के साथ खाता प्रमाण-पत्र साझा करना" if has_online_presence else "गोपनीयता समझौतों का उल्लंघन करना"}

---

## भुगतान शर्तें

{"### शुल्क और बिलिंग" + chr(10) + "- सेवा शुल्क खरीदारी से पहले स्पष्ट रूप से प्रदर्शित होते हैं" + chr(10) + "- भुगतान अधिकृत प्रदाताओं के माध्यम से सुरक्षित रूप से प्रसंस्करण किए जाते हैं" + chr(10) + "- सभी शुल्क लागू करों के अतिरिक्त हैं जब तक कि अन्यथा न कहा गया हो" + chr(10) + chr(10) + "### रिफंड नीति" + chr(10) + "- रिफंड हमारी अलग रिफंड नीति के अधीन हैं" + chr(10) + "- कुछ सेवाएं गैर-वापसी योग्य हो सकती हैं" + chr(10) + "- विवाद समाधान प्रक्रियाएं उपलब्ध हैं" if processes_payments else "### सेवा शुल्क" + chr(10) + "- सेवा शुल्क जुड़ाव से पहले सहमत होते हैं" + chr(10) + "- भुगतान शर्तें सेवा समझौतों में निर्दिष्ट हैं" + chr(10) + "- विलंब भुगतान शुल्क निर्दिष्ट के अनुसार लागू हो सकते हैं"}

---

## {t['contact_info']}

इन नियमों और शर्तों के बारे में प्रश्नों के लिए:

**{business_name}**
- **ईमेल:** legal@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **पता:** {business_name} कानूनी विभाग, {location_country}
- {"**फोन:** हमारी वेबसाइट संपर्क जानकारी के माध्यम से उपलब्ध" if has_online_presence else "**फोन:** प्रदान की गई व्यावसायिक जानकारी के माध्यम से संपर्क करें"}

---

**ये नियम {location_country} में लागू वाणिज्यिक कानूनों {"और " + industry + " व्यवसायों के लिए उद्योग-विशिष्ट नियमों" if business_type in ["services", "consulting"] else ""} के साथ अनुपालित हैं.**

*अंतिम समीक्षा और अपडेट: {current_date}*"""

        else:  # English (default)
            return f"""# TERMS AND CONDITIONS

**Effective Date:** {current_date}  
**Last Updated:** {current_date}

---

## ACCEPTANCE OF TERMS

Welcome to **{business_name}**. These Terms and Conditions ("Terms") govern your use of our {business_type} services and {"website " + website_url if has_online_presence else "services"}. By accessing or using our services, you agree to be bound by these Terms.

If you do not agree to these Terms, please do not use our services.

---

## DESCRIPTION OF SERVICES

**{business_name}** is a {business_type} company operating in the {industry} industry. We provide:

{"### Digital Services" + chr(10) + "- Online platform access and functionality" + chr(10) + "- User account management" + chr(10) + "- Digital content and resources" if has_online_presence else "### Business Services"}
- {industry.title()} solutions and expertise
- {"Payment processing and transaction services" if processes_payments else "Consultation and professional services"}
- Customer support and technical assistance
- {"Customized business solutions" if target_audience == "B2B" else "Consumer-focused services"}

---

## USER RESPONSIBILITIES

### Account Management
{"- Maintain accurate account information" + chr(10) + "- Protect your login credentials" + chr(10) + "- Notify us of unauthorized access" if has_online_presence else "- Provide accurate contact information" + chr(10) + "- Maintain communication with our team"}
- Comply with applicable laws and regulations
- Use services only for lawful purposes

### Prohibited Activities
You agree not to:
- {"Violate any laws or infringe on others' rights" + chr(10) + "- Upload malicious content or spam" if has_online_presence else "Engage in fraudulent or deceptive practices"}
- Interfere with our services or systems
- {"Reverse engineer or copy our software" if has_online_presence else "Misuse proprietary information"}
- {"Share account credentials with others" if has_online_presence else "Violate confidentiality agreements"}

---

## PAYMENT TERMS

{"### Fees and Billing" + chr(10) + "- Service fees are clearly displayed before purchase" + chr(10) + "- Payments are processed securely through authorized providers" + chr(10) + "- All fees are exclusive of applicable taxes unless stated otherwise" + chr(10) + chr(10) + "### Refund Policy" + chr(10) + "- Refunds are subject to our separate Refund Policy" + chr(10) + "- Certain services may be non-refundable" + chr(10) + "- Dispute resolution procedures are available" if processes_payments else "### Service Fees" + chr(10) + "- Service fees are agreed upon before engagement" + chr(10) + "- Payment terms are specified in service agreements" + chr(10) + "- Late payment fees may apply as specified"}

---

## CONTACT INFORMATION

For questions about these Terms and Conditions:

**{business_name}**
- **Email:** legal@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Address:** {business_name} Legal Department, {location_country}
- {"**Phone:** Available through our website contact information" if has_online_presence else "**Phone:** Contact through provided business information"}

---

**These Terms are compliant with applicable commercial laws in {location_country} {"and industry-specific regulations for " + industry + " businesses" if business_type in ["services", "consulting"] else ""}.**

*Last reviewed and updated: {current_date}*"""

## PAYMENT TERMS

{"### Fees and Billing" + chr(10) + "- Service fees are clearly displayed before purchase" + chr(10) + "- Payments are processed securely through authorized providers" + chr(10) + "- All fees are exclusive of applicable taxes unless stated otherwise" + chr(10) + chr(10) + "### Refund Policy" + chr(10) + "- Refunds are subject to our separate Refund Policy" + chr(10) + "- Certain services may be non-refundable" + chr(10) + "- Dispute resolution procedures are available" if processes_payments else "### Service Fees" + chr(10) + "- Service fees are agreed upon before engagement" + chr(10) + "- Payment terms are specified in service agreements" + chr(10) + "- Late payment fees may apply as specified"}

---

## INTELLECTUAL PROPERTY

### Our Rights
- All content, trademarks, and intellectual property remain our property
- {"Website design, software, and digital content are protected" if has_online_presence else "Service methodologies and proprietary processes are protected"}
- You receive a limited license to use our services as intended

### Your Rights
- You retain ownership of content you provide to us
- We may use your content to provide services as agreed
- You grant us necessary licenses to deliver our services

---

## PRIVACY AND DATA PROTECTION

Your privacy is important to us. Our data practices are governed by our Privacy Policy, which is incorporated into these Terms by reference. Key points:

- We collect and process information as described in our Privacy Policy
- {"We use cookies and tracking technologies with your consent" if uses_cookies else "We collect minimal necessary information for service delivery"}
- {"We implement security measures to protect your data" if has_online_presence else "We maintain confidentiality of your business information"}
- You have rights regarding your personal information

---

## DISCLAIMERS AND LIMITATIONS

### Service Availability
- Services are provided "as is" without warranties
- {"We do not guarantee uninterrupted website availability" if has_online_presence else "We strive to provide reliable service delivery"}
- Maintenance and updates may temporarily affect service access

### Limitation of Liability
TO THE MAXIMUM EXTENT PERMITTED BY LAW:
- Our liability is limited to the amount paid for services
- We are not liable for indirect, incidental, or consequential damages
- {"Force majeure events may affect service delivery" if business_type in ["manufacturing", "retail"] else "External factors beyond our control may impact services"}

---

## DISPUTE RESOLUTION

### Governing Law
These Terms are governed by the laws of {location_country}.

### Resolution Process
1. **Direct Communication:** Contact us first to resolve issues
2. **Mediation:** Participate in good faith mediation if needed
3. **Arbitration:** {"Binding arbitration for unresolved disputes" if location_country == "India" else "Legal proceedings in appropriate jurisdiction"}

### Exceptions
Certain disputes may be resolved in small claims court or through regulatory processes.

---

## TERMINATION

### Your Right to Terminate
- {"You may close your account at any time" if has_online_presence else "You may discontinue services with appropriate notice"}
- {"Download your data before account closure" if has_online_presence else "Request your records before service termination"}

### Our Right to Terminate
We may suspend or terminate your access if you:
- Violate these Terms or our policies
- {"Engage in prohibited activities" if has_online_presence else "Breach service agreements"}
- {"Fail to pay applicable fees" if processes_payments else "Violate professional conduct standards"}

---

## MODIFICATIONS

We may update these Terms periodically. Changes will be effective:
- {"Upon posting on our website" if has_online_presence else "Upon notification to you"}
- After reasonable notice for material changes
- Immediately for legal compliance updates

Continued use of our services constitutes acceptance of updated Terms.

---

## CONTACT INFORMATION

For questions about these Terms and Conditions:

**{business_name}**
- **Email:** legal@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Address:** {business_name} Legal Department, {location_country}
- {"**Phone:** Available through our website contact information" if has_online_presence else "**Phone:** Contact through provided business information"}

---

## ADDITIONAL PROVISIONS

### Severability
If any provision of these Terms is found unenforceable, the remaining provisions will continue in effect.

### Entire Agreement
These Terms, together with our Privacy Policy {"and any service-specific agreements" if business_type in ["services", "consulting"] else ""}, constitute the complete agreement between us.

### Assignment
We may assign these Terms in connection with a business transfer. You may not assign your rights without our consent.

---

**These Terms are compliant with applicable commercial laws in {location_country} and industry-specific regulations for {industry} businesses.**

*Last reviewed and updated: {current_date}*"""

    elif policy_type == 'refund_policy':
        return f"""# REFUND POLICY

**Effective Date:** {current_date}  
**Last Updated:** {current_date}

---

## OVERVIEW

At **{business_name}**, we are committed to customer satisfaction. This Refund Policy outlines the circumstances under which refunds may be granted for our {business_type} services {"and products" if business_type in ["retail", "e-commerce"] else ""}.

This policy applies to all {"purchases made through our website " + website_url + " and " if has_online_presence else ""}services provided by {business_name}.

---

## REFUND ELIGIBILITY

### Qualifying Circumstances
{"Refunds may be granted in the following situations:" + chr(10) + "- Service delivery failure or non-performance" + chr(10) + "- Defective products or unsatisfactory service quality" if processes_payments else "Service adjustments may be considered for:"}
- {"Technical issues preventing service access" if has_online_presence else "Service delivery issues beyond your control"}
- {"Billing errors or duplicate charges" if processes_payments else "Billing discrepancies or errors"}
- Cancellation within the specified timeframe
- {"Product returns within the return window" if business_type in ["retail", "e-commerce"] else "Service modifications before delivery"}

### Non-Refundable Services
{"Certain services and products are non-refundable:" if processes_payments else "The following circumstances typically do not qualify for refunds:"}
- {"Digital downloads after delivery" if has_online_presence else "Completed consulting services"}
- {"Customized or personalized services" if business_type in ["services", "consulting"] else "Specialized solutions"}
- {"Services used beyond the trial period" if has_online_presence else "Services substantially delivered"}
- {"Third-party fees and processing charges" if processes_payments else "External costs incurred on your behalf"}

---

## REFUND TIMEFRAMES

### Request Window
{"- Standard services: 30 days from purchase" + chr(10) + "- Digital products: 14 days from delivery" + chr(10) + "- Subscription services: According to subscription terms" if processes_payments else "- Service engagements: Within 14 days of service commencement" + chr(10) + "- Consulting services: Before substantial work begins"}
- {"Physical products: " + ("30 days from delivery" if business_type in ["retail", "e-commerce"] else "N/A") if business_type in ["retail", "e-commerce"] else "Project-based services: As specified in service agreement"}

### Processing Time
Once approved, refunds are typically processed:
- {"Credit card refunds: 5-10 business days" if processes_payments else "Service credits: Immediate application to account"}
- {"Bank transfer refunds: 3-7 business days" if processes_payments else "Cash refunds: 5-10 business days"}
- {"Digital wallet refunds: 1-3 business days" if processes_payments else "Alternative compensation: As mutually agreed"}

---

## REFUND PROCESS

### Step 1: Contact Us
- **Email:** refunds@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Include:** {"Order number, purchase date, and reason for refund" if processes_payments else "Service details, engagement date, and refund reason"}
- **Provide:** {"Screenshots or documentation if applicable" if has_online_presence else "Relevant documentation"}

### Step 2: Review Process
- We will acknowledge your request within {"24-48 hours" if has_online_presence else "2 business days"}
- {"Review of purchase records and service usage" if processes_payments else "Assessment of service delivery and satisfaction"}
- Additional information may be requested

### Step 3: Decision Notification
- Approval or denial notification within {"5-7 business days" if processes_payments else "7-10 business days"}
- Clear explanation of decision and next steps
- {"Refund processing timeline if approved" if processes_payments else "Resolution timeline if approved"}

### Step 4: Refund Processing
{"- Original payment method refund (preferred)" + chr(10) + "- Store credit or account credit (alternative)" + chr(10) + "- Bank transfer for certain payment methods" if processes_payments else "- Service credit for future engagements" + chr(10) + "- Cash refund where applicable" + chr(10) + "- Alternative compensation as agreed"}

---

## SPECIAL CIRCUMSTANCES

### Subscription Services
{"- Monthly subscriptions: Cancel anytime, no refund for current period" + chr(10) + "- Annual subscriptions: Pro-rated refund for unused months" + chr(10) + "- Free trials: No charges if canceled during trial" if has_online_presence else "- Ongoing service agreements: Refund for unused service periods" + chr(10) + "- Contract services: According to contract terms"}

### Business Services
{"- Consulting services: Refund for undelivered work only" + chr(10) + "- Custom solutions: Limited refund after work begins" + chr(10) + "- Training services: Refund before commencement only" if business_type in ["services", "consulting"] else "- Product sales: Standard return policy applies" + chr(10) + "- Service packages: Partial refunds for unused components"}

### Exceptional Circumstances
- Medical emergencies or hardship situations
- {"Technical failures beyond user control" if has_online_presence else "Service provider unavailability"}
- {"Force majeure events affecting service delivery" if business_type in ["services", "consulting"] else "External factors preventing service use"}

---

## CONDITIONS AND RESTRICTIONS

### General Conditions
{"- Products must be in original condition for returns" + chr(10) + "- Digital products must not be copied or shared" + chr(10) + "- Account must be in good standing" if business_type in ["retail", "e-commerce"] else "- Services must not be substantially utilized" + chr(10) + "- No breach of service terms" + chr(10) + "- Reasonable cause for refund request"}

### Refund Limitations
- {"Processing fees may not be refundable" if processes_payments else "Administrative costs may be deducted"}
- {"Currency conversion fees are non-refundable" if processes_payments else "Third-party costs may not be refunded"}
- Maximum refund amount is the original purchase price
- {"Multiple refund requests may be subject to review" if processes_payments else "Repeated service issues will be investigated"}

---

## DISPUTE RESOLUTION

### Internal Resolution
1. Contact our customer service team first
2. {"Escalation to management if needed" if business_type in ["services", "retail"] else "Discussion with service delivery team"}
3. {"Review by our refund committee for complex cases" if processes_payments else "Case-by-case evaluation for unique situations"}

### External Resolution
If internal resolution is unsuccessful:
- {"Dispute with payment provider (credit card company, etc.)" if processes_payments else "Professional mediation services"}
- {"Consumer protection agency complaint" if target_audience == "B2C" else "Business dispute resolution services"}
- {"Legal action as a last resort" if processes_payments else "Arbitration or legal consultation"}

---

## EXCHANGES AND STORE CREDIT

### Exchange Options
{"- Exchange for different products of equal value" + chr(10) + "- Upgrade to premium services (pay difference)" + chr(10) + "- Downgrade with partial refund" if business_type in ["retail", "e-commerce"] else "- Alternative service delivery methods" + chr(10) + "- Rescheduling of service appointments" + chr(10) + "- Modification of service scope"}

### Store Credit
{"- Credit valid for 12 months from issue date" + chr(10) + "- Can be applied to any products or services" + chr(10) + "- Non-transferable and non-refundable" if processes_payments else "- Credit applied to future service engagements" + chr(10) + "- Flexible application to different service types" + chr(10) + "- Reasonable validity period"}

---

## CONTACT INFORMATION

For refund requests and questions:

**{business_name} Customer Service**
- **Email:** refunds@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Phone:** {"Available through our website contact information" if has_online_presence else "Contact through provided business information"}
- **Address:** {business_name} Customer Service, {location_country}
- **Hours:** {"Business hours as posted on our website" if has_online_presence else "Standard business hours"}

### Escalation Contacts
- **Manager:** manager@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Legal:** legal@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}

---

## POLICY UPDATES

This Refund Policy may be updated to reflect:
- Changes in business practices
- Legal or regulatory requirements
- {"Payment processor policy updates" if processes_payments else "Industry standard updates"}
- Customer feedback and service improvements

{"Updated policies will be posted on our website with effective dates." if has_online_presence else "Updated policies will be communicated directly to customers."}

---

**This Refund Policy complies with consumer protection laws in {location_country} {"and applicable online commerce regulations" if has_online_presence else "and relevant business service standards"}.**

*Last reviewed and updated: {current_date}*"""

    elif policy_type == 'cookie_policy':
        if not uses_cookies and not has_online_presence:
            return f"""# COOKIE POLICY

**Effective Date:** {current_date}  
**Last Updated:** {current_date}

---

## NOTICE

**{business_name}** does not currently operate a website or use cookies and tracking technologies. This policy is provided for informational purposes and would apply if we implement web-based services in the future.

As a {business_type} business in the {industry} industry, we focus on direct service delivery {"and do not currently collect digital tracking data" if not collects_personal_data else "while maintaining your privacy"}.

If our operations change to include website services or digital tracking, this policy will be updated accordingly and you will be notified of any changes.

---

## CONTACT INFORMATION

For questions about our current data practices:

**{business_name}**
- **Email:** privacy@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Address:** {business_name}, {location_country}

*Last reviewed and updated: {current_date}*"""
        
        return f"""# COOKIE POLICY

**Effective Date:** {current_date}  
**Last Updated:** {current_date}

---

## INTRODUCTION

This Cookie Policy explains how **{business_name}** ("we", "us", or "our") uses cookies and similar tracking technologies on our website {website_url} {"and related digital services" if has_online_presence else ""}.

This policy should be read alongside our Privacy Policy, which explains how we collect, use, and protect your personal information.

---

## WHAT ARE COOKIES

Cookies are small text files that are placed on your device (computer, smartphone, tablet) when you visit websites. They are widely used to make websites work more efficiently and to provide information to website owners.

### Types of Cookies We Use

#### Essential Cookies
These cookies are necessary for our website to function properly:
- **Session cookies:** Enable core website functionality
- **Security cookies:** Protect against fraud and maintain security
- **Load balancing cookies:** Ensure optimal website performance
- **Authentication cookies:** Keep you logged in to your account

#### Analytics Cookies
These help us understand how visitors use our website:
- **Google Analytics:** {"Website traffic and user behavior analysis" if has_online_presence else "Basic usage statistics"}
- **Performance monitoring:** Page load times and error tracking
- **Usage patterns:** Most popular content and navigation paths
- **Demographic data:** {"General location and device information" if target_audience == "B2C" else "Business user analytics"}

#### Functionality Cookies
These enhance your experience on our website:
- **Preference cookies:** Remember your language and region settings
- **Customization cookies:** {"Personalize content and recommendations" if target_audience == "B2C" else "Customize business interface"}
- **Shopping cart cookies:** {"Remember items in your cart" if processes_payments else "Remember service selections"}
- **Form data cookies:** Save partially completed forms

#### Marketing Cookies
{"These cookies track your browsing activity for advertising purposes:" + chr(10) + "- **Advertising networks:** Display relevant ads on other websites" + chr(10) + "- **Social media pixels:** Enable social sharing and targeted advertising" + chr(10) + "- **Retargeting cookies:** Show you relevant ads after visiting our site" + chr(10) + "- **Conversion tracking:** Measure effectiveness of marketing campaigns" if target_audience == "B2C" else "These cookies support our business marketing efforts:" + chr(10) + "- **Lead tracking:** Monitor business inquiry sources" + chr(10) + "- **Campaign analytics:** Measure marketing effectiveness" + chr(10) + "- **Professional networks:** LinkedIn and industry platform integration" + chr(10) + "- **B2B targeting:** Relevant content for business users"}

---

## HOW WE USE COOKIES

### Website Functionality
- {"Maintain your login session and preferences" if has_online_presence else "Enable core service functionality"}
- {"Process online transactions securely" if processes_payments else "Handle service requests efficiently"}
- Remember your language and location preferences
- {"Provide personalized content and recommendations" if target_audience == "B2C" else "Customize business solutions display"}

### Analytics and Performance
- Measure website traffic and user engagement
- {"Identify popular products and services" if business_type in ["retail", "e-commerce"] else "Understand service demand patterns"}
- {"Monitor website performance and loading speeds" if has_online_presence else "Track digital service performance"}
- Generate reports on website usage and effectiveness

### Marketing and Advertising
{"- Display targeted advertisements on other websites" + chr(10) + "- Measure the effectiveness of advertising campaigns" + chr(10) + "- Provide personalized content and offers" + chr(10) + "- Enable social media sharing and integration" if target_audience == "B2C" else "- Track business lead generation sources" + chr(10) + "- Measure marketing campaign effectiveness" + chr(10) + "- Customize content for business users" + chr(10) + "- Integrate with professional networking platforms"}

### Security and Fraud Prevention
- Detect and prevent fraudulent activity
- {"Secure online payment processing" if processes_payments else "Protect sensitive business information"}
- Monitor for suspicious behavior and bot traffic
- Maintain website security and integrity

---

## THIRD-PARTY COOKIES

We work with trusted third-party service providers who may set cookies on our website:

### Analytics Providers
- **Google Analytics:** {"Website traffic analysis and user insights" if has_online_presence else "Basic digital analytics"}
- **Hotjar:** {"User experience analysis and heatmaps" if has_online_presence else "Digital user experience monitoring"}

### Advertising Partners
{"- **Google Ads:** Targeted advertising and conversion tracking" + chr(10) + "- **Facebook Pixel:** Social media advertising and analytics" + chr(10) + "- **LinkedIn Insight:** Professional network advertising" if target_audience == "B2C" else "- **LinkedIn Marketing:** Business-to-business advertising" + chr(10) + "- **Google Ads:** Professional services advertising" + chr(10) + "- **Industry platforms:** Sector-specific advertising networks"}

### Payment Processors
{"- **Stripe/PayPal:** Secure payment processing cookies" + chr(10) + "- **Banking partners:** Transaction security and fraud prevention" if processes_payments else "- **Payment providers:** Secure transaction processing when applicable"}

### Communication Tools
- **Live chat services:** Customer support functionality
- {"**Email marketing:** Newsletter and communication tracking" if target_audience == "B2C" else "**Business communication:** Professional correspondence tracking"}

---

## YOUR COOKIE CHOICES

### Browser Settings
You can control cookies through your browser settings:

#### Chrome
1. Go to Settings > Privacy and security > Cookies and other site data
2. Choose your preferred cookie settings
3. {"Manage exceptions for specific websites" if has_online_presence else "Configure site-specific preferences"}

#### Firefox
1. Go to Options > Privacy & Security > Cookies and Site Data
2. Select your cookie preferences
3. {"Use custom settings for enhanced control" if has_online_presence else "Configure tracking protection"}

#### Safari
1. Go to Preferences > Privacy > Cookies and website data
2. Choose your blocking preferences
3. {"Manage website-specific settings" if has_online_presence else "Configure cross-site tracking prevention"}

#### Edge
1. Go to Settings > Site permissions > Cookies and site data
2. Configure your cookie preferences
3. {"Block or allow specific sites" if has_online_presence else "Manage site permissions"}

### Opt-Out Tools
{"- **Google Analytics Opt-out:** Use the Google Analytics opt-out browser add-on" + chr(10) + "- **Advertising opt-outs:** Visit NAI or DAA opt-out pages" + chr(10) + "- **Social media:** Adjust privacy settings on social platforms" if target_audience == "B2C" else "- **Business analytics:** Contact us for opt-out assistance" + chr(10) + "- **Professional networks:** Manage privacy settings on LinkedIn" + chr(10) + "- **Marketing communications:** Use unsubscribe links in emails"}

### Impact of Blocking Cookies
If you disable cookies, {"some website functionality may be limited:" + chr(10) + "- You may need to log in repeatedly" + chr(10) + "- Your preferences won't be saved" + chr(10) + "- Some features may not work properly" + chr(10) + "- Personalization will be reduced" if has_online_presence else "some digital services may be affected:" + chr(10) + "- Session management may be impacted" + chr(10) + "- Service preferences won't be remembered" + chr(10) + "- Some features may not function optimally"}

---

## MOBILE APPS AND DEVICES

{"If we develop mobile applications, they may use similar tracking technologies:" + chr(10) + "- **Device identifiers:** For app functionality and analytics" + chr(10) + "- **Push notification tokens:** For communication" + chr(10) + "- **Location data:** If relevant to services (with permission)" + chr(10) + "- **App usage analytics:** To improve functionality" if has_online_presence else "Our digital services may include mobile-optimized interfaces:" + chr(10) + "- **Mobile web cookies:** Similar to desktop cookie usage" + chr(10) + "- **Device-adaptive content:** Optimized for mobile devices" + chr(10) + "- **Mobile analytics:** Understanding mobile user patterns"}

---

## INTERNATIONAL TRANSFERS

{"Cookie data may be processed in different countries where our service providers operate. We ensure appropriate safeguards are in place for international data transfers, in compliance with " + location_country + " privacy laws." if location_country != "United States" else "Cookie data is primarily processed within the United States, with appropriate protections for international visitors."}

---

## UPDATES TO THIS POLICY

We may update this Cookie Policy to reflect:
- Changes in cookie usage or technologies
- New third-party partnerships
- Legal or regulatory requirements
- User feedback and privacy best practices

{"Updated policies will be posted on our website with clear notification of changes." if has_online_presence else "Updated policies will be communicated to users of our digital services."}

---

## CONTACT INFORMATION

For questions about our cookie practices:

**{business_name} Privacy Team**
- **Email:** privacy@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Address:** {business_name} Privacy Office, {location_country}
- {"**Online form:** Available through our website contact page" if has_online_presence else "**Phone:** Contact through provided business information"}

### Data Protection Officer
{"For EU/UK residents or complex privacy questions:" + chr(10) + "- **Email:** dpo@" + website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0] if location_country in ["European Union", "UK", "Germany"] else "For privacy-related concerns:" + chr(10) + "- **Email:** privacy@" + website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}

---

## CONSENT MANAGEMENT

{"We use a cookie consent management system that allows you to:" + chr(10) + "- Accept or reject different types of cookies" + chr(10) + "- Change your preferences at any time" + chr(10) + "- Access detailed information about each cookie category" + chr(10) + "- Contact us with questions about cookie usage" if has_online_presence else "We obtain consent for cookie usage through:" + chr(10) + "- Clear notice when you first visit our digital services" + chr(10) + "- Options to manage your preferences" + chr(10) + "- Ongoing ability to change your settings" + chr(10) + "- Transparent information about cookie purposes"}

**Your continued use of our {"website" if has_online_presence else "digital services"} after accepting this policy indicates your consent to our cookie usage as described above.**

---

**This Cookie Policy complies with applicable privacy laws including {"GDPR, " if location_country in ["European Union", "UK", "Germany"] else ""}ePrivacy directives, {"and " + location_country + " digital privacy regulations" if location_country != "United States" else "and US privacy legislation"}.**

*Last reviewed and updated: {current_date}*"""

    else:
        return f"""# {policy_type.replace('_', ' ').title()}

**Effective Date:** {current_date}  
**Last Updated:** {current_date}

---

## POLICY DOCUMENT

This {policy_type.replace('_', ' ').title()} for **{business_name}** is currently being developed. 

As a {business_type} business operating in the {industry} industry{"" if location_country == "India" else f" with operations in {location_country}"}, we are committed to maintaining comprehensive legal documentation.

This document will be updated with detailed policy content specific to your business requirements and applicable legal standards.

---

## CONTACT INFORMATION

For questions about this policy:

**{business_name}**
- **Email:** legal@{website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]}
- **Address:** {business_name}, {location_country}

*Policy under development - Last updated: {current_date}*"""
    
    # Fallback for unsupported policy types
    return f"Policy type '{policy_type}' is not supported."

@app.post("/generate-policies")
async def generate_policies(payload: dict, current_user: str = Depends(get_current_user)):
    """Generate policy documents based on provided business details and requested policy types.
    Saves generated policies to Supabase and returns them to the frontend.
    Expected payload: { business_details: {...}, policy_types: [..], language: 'en' }
    """
    try:
        business = payload.get("business_details", {})
        policy_types = payload.get("policy_types", [])
        language = payload.get("language", "en")
        if not business or not policy_types:
            raise HTTPException(status_code=400, detail="business_details and policy_types are required")

        print(f"📝 Generating {len(policy_types)} policies for user {current_user}")
        
        policies = {}
        saved_policy_ids = []
        
        # Generate and save each policy
        for policy_type in policy_types:
            try:
                # Generate policy content
                policy_content = generate_policy_content(policy_type, business, language)
                policies[policy_type] = policy_content
                
                # Prepare policy data for Supabase
                business_name = business.get('business_name', 'Unknown Business')
                location_country = business.get('location_country', 'India')
                
                # Determine compliance regions based on business location
                compliance_regions = ['Indian_IT_Act']  # Default for India
                if location_country in ['European Union', 'Germany', 'France', 'UK']:
                    compliance_regions.append('GDPR')
                elif location_country == 'United States':
                    compliance_regions.extend(['CCPA', 'COPPA'])
                elif location_country == 'Canada':
                    compliance_regions.append('PIPEDA')
                
                policy_data = {
                    'user_id': int(current_user),
                    'business_name': business_name,
                    'policy_type': policy_type,
                    'content': policy_content,
                    'language': language,
                    'compliance_regions': compliance_regions
                }
                
                print(f"💾 Saving {policy_type} policy to Supabase for {business_name}")
                
                # Insert policy into Supabase
                result = supabase.table('policies').insert(policy_data).execute()
                
                if result.data:
                    policy_id = result.data[0]['id']
                    saved_policy_ids.append(policy_id)
                    print(f"✅ Successfully saved {policy_type} policy with ID: {policy_id}")
                else:
                    print(f"⚠️ Warning: No data returned when saving {policy_type} policy")
                    
            except Exception as policy_error:
                print(f"❌ Error processing {policy_type} policy: {policy_error}")
                # Continue with other policies even if one fails
                continue
        
        print(f"✅ Successfully generated and saved {len(saved_policy_ids)} policies")
        
        return {
            "success": True, 
            "policies": policies,
            "saved_policy_ids": saved_policy_ids,
            "total_saved": len(saved_policy_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating policies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate policies: {str(e)}")

@app.get("/get-policies") 
async def get_policies(current_user: str = Depends(get_current_user)):
    """Get generated policies for the current user from Supabase"""
    try:
        print(f"📋 Fetching policies for user: {current_user}")
        
        # Query policies table for the current user, ordered by most recent first
        result = supabase.table('policies').select(
            'id, business_name, policy_type, content, language, compliance_regions, generated_at, updated_at'
        ).eq('user_id', int(current_user)).order('generated_at', desc=True).execute()
        
        if not result.data:
            print(f"ℹ️ No policies found for user {current_user}")
            return {"success": True, "data": [], "total_count": 0}
        
        policies_data = []
        for policy in result.data:
            # Transform the data to match frontend expectations
            formatted_policy = {
                "id": str(policy['id']),
                "policy_type": policy['policy_type'],
                "content": policy['content'],
                "generated_at": policy['generated_at'],
                "compliance_regions": policy.get('compliance_regions', []),
                "business_name": policy['business_name'],
                "language": policy.get('language', 'en')
            }
            policies_data.append(formatted_policy)
        
        print(f"✅ Retrieved {len(policies_data)} policies from Supabase")
        
        return {
            "success": True, 
            "data": policies_data,
            "total_count": len(policies_data)
        }
        
    except Exception as e:
        print(f"❌ Error fetching policies from Supabase: {e}")
        # Return empty array instead of failing completely
        return {
            "success": False, 
            "data": [],
            "total_count": 0,
            "error": f"Failed to fetch policies: {str(e)}"
        }

@app.delete("/delete-policy/{policy_id}")
async def delete_policy(policy_id: str, current_user: str = Depends(get_current_user)):
    """Delete a specific policy for the current user"""
    try:
        print(f"🗑️ Attempting to delete policy {policy_id} for user {current_user}")
        
        # Verify the policy belongs to the current user before deleting
        verify_result = supabase.table('policies').select('id, user_id, policy_type').eq('id', int(policy_id)).eq('user_id', int(current_user)).execute()
        
        if not verify_result.data:
            print(f"❌ Policy {policy_id} not found or doesn't belong to user {current_user}")
            raise HTTPException(status_code=404, detail="Policy not found or access denied")
        
        policy_info = verify_result.data[0]
        print(f"🔍 Found policy: {policy_info['policy_type']} (ID: {policy_id})")
        
        # Delete the policy
        delete_result = supabase.table('policies').delete().eq('id', int(policy_id)).eq('user_id', int(current_user)).execute()
        
        if delete_result.data:
            print(f"✅ Successfully deleted policy {policy_id}")
            return {
                "success": True,
                "message": f"Policy {policy_info['policy_type']} deleted successfully",
                "deleted_policy_id": policy_id
            }
        else:
            print(f"⚠️ No rows affected when deleting policy {policy_id}")
            raise HTTPException(status_code=500, detail="Failed to delete policy")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting policy {policy_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete policy: {str(e)}")

# ----------------- Insurance Hub Endpoints ----------------- #

def _calculate_risk_score(assets: Dict[str, Any], workforce_size: int, risk_concerns: List[str]) -> Dict[str, Any]:
    # Basic heuristic risk score (0-100)
    asset_total = 0
    for v in assets.values():
        try:
            asset_total += float(v) if v is not None else 0
        except (TypeError, ValueError):
            continue
    base = 40
    # Asset weighting
    if asset_total > 5_000_000:
        base += 25
    elif asset_total > 1_000_000:
        base += 18
    elif asset_total > 250_000:
        base += 12
    elif asset_total > 50_000:
        base += 6
    # Workforce
    if workforce_size:
        if workforce_size > 200:
            base += 15
        elif workforce_size > 50:
            base += 10
        elif workforce_size > 10:
            base += 5
    # Risk concerns diversity
    concern_points = min(len(set(risk_concerns)) * 3, 18)
    base += concern_points
    score = max(0, min(100, base))
    if score >= 80:
        level = "High"
    elif score >= 65:
        level = "Medium"
    elif score >= 50:
        level = "Elevated"
    else:
        level = "Low"
    # Business size classification (simplistic - could blend revenue later)
    if workforce_size is None:
        workforce_size = 0
    if workforce_size <= 10:
        business_size = "micro"
    elif workforce_size <= 50:
        business_size = "small"
    elif workforce_size <= 250:
        business_size = "medium"
    else:
        business_size = "large"
    return {"risk_score": score, "risk_level": level, "asset_total": asset_total, "business_size": business_size}

@app.post("/insurance/assess")
async def insurance_assess(req: InsuranceAssessmentRequest, current_user: str = Depends(get_current_user)):
    """Perform risk assessment and return recommended insurance templates."""
    try:
        # Fetch templates from Supabase insurance_templates table
        try:
            res = supabase.table('insurance_templates').select('*').eq('is_active', True).execute()
            templates_raw = res.data or []
            print(f"✅ Loaded {len(templates_raw)} templates from Supabase")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error fetching insurance templates from Supabase: {error_msg}")
            
            # Check if it's a table not found error
            if "Could not find the table" in error_msg or "insurance_templates" in error_msg:
                return {
                    "success": False,
                    "error": "insurance_templates_not_found",
                    "message": "Insurance templates table not found in Supabase",
                    "instructions": {
                        "step1": "Go to Supabase Dashboard: https://supabase.com/dashboard/project/eecbqzvcnwrkcxgwjxlt",
                        "step2": "Navigate to SQL Editor",
                        "step3": "Execute the insurance table creation script",
                        "step4": "Copy and run the SQL from supabase_schema.sql file"
                    },
                    "sql_location": "/Nexora-2/nexora/python_services/supabase_schema.sql",
                    "details": "The insurance_templates table needs to be created in your Supabase database before the Insurance Hub can function properly."
                }
            else:
                raise HTTPException(status_code=500, detail=f"Database error: {error_msg}")
        
        if not templates_raw:
            return {
                "success": False,
                "error": "no_templates",
                "message": "No insurance templates found in database",
                "instructions": {
                    "step1": "Insurance templates table exists but has no data",
                    "step2": "Run the data insertion SQL from supabase_schema.sql",
                    "step3": "This will add sample insurance policies to recommend"
                }
            }

        risk_calc = _calculate_risk_score(req.assets, req.workforce_size or 0, req.risk_concerns)

        recommended = []
        for tpl in templates_raw:
            # Filter by business type
            tpl_business_types = tpl.get('business_types') or []
            if req.business_type not in tpl_business_types:
                continue
            # Risk concern intersection
            tpl_risks = set(tpl.get('risk_categories') or [])
            if req.risk_concerns and not (tpl_risks.intersection(req.risk_concerns)):
                # allow partial - skip strict filter; comment to enforce
                pass
            # Estimate coverage based on asset_total proportion
            min_cov = float(tpl.get('min_coverage_amount') or 0)
            max_cov = float(tpl.get('max_coverage_amount') or min_cov)
            asset_total = risk_calc['asset_total']
            if max_cov > min_cov:
                # linear scale
                coverage_est = min_cov + (min(1.0, asset_total / (max_cov * 1.2)) * (max_cov - min_cov))
            else:
                coverage_est = min_cov
            # Premium estimate
            base_premium = float(tpl.get('base_premium') or 0)
            risk_multiplier = 1 + (risk_calc['risk_score'] / 200)  # up to +50%
            premium_est = round(base_premium * risk_multiplier, 2)
            premium_range = f"₹{int(premium_est*0.9)} - ₹{int(premium_est*1.2)}"
            risk_match_set = tpl_risks.intersection(req.risk_concerns)
            # Scoring heuristic
            match_score = (
                (len(risk_match_set) * 10) +              # risk alignment
                (15 if req.business_type in tpl_business_types else 0) +
                (5 if risk_calc['business_size'] in ['small','medium'] else 0) +
                (3 if (req.preferences or {}).get('focus') in tpl_risks else 0)
            )
            reason_parts = []
            if risk_match_set:
                reason_parts.append(f"covers key risks: {', '.join(sorted(risk_match_set))}")
            else:
                reason_parts.append("broad foundational cover relevant to your sector")
            reason_parts.append(f"scaled coverage ≈ ₹{int(coverage_est):,}")
            reason_parts.append(f"risk score {risk_calc['risk_score']} ({risk_calc['risk_level']})")
            reason_parts.append(f"business size {risk_calc['business_size']}")
            recommended.append({
                "template_id": tpl.get('template_id'),
                "policy_name": tpl.get('policy_name'),
                "policy_type": tpl.get('policy_type'),
                "provider_name": tpl.get('provider_name'),
                "estimated_coverage_amount": round(coverage_est, 2),
                "coverage_range": f"₹{int(min_cov)} - ₹{int(max_cov)}",
                "premium_estimate": premium_est,
                "premium_range": premium_range,
                "legal_compliance": tpl.get('legal_compliance', True),
                "compliance_authority": tpl.get('compliance_authority', 'IRDAI'),
                "compliance_badge": ("✅ IRDAI Approved" if tpl.get('legal_compliance') else "⚠️ Review Required"),
                "coverage_details": tpl.get('coverage_description'),
                "exclusions": tpl.get('exclusions_description'),
                "optional_addons": tpl.get('optional_addons'),
                "risk_match": list(risk_match_set),
                "match_score": match_score,
                "reason": "; ".join(reason_parts)
            })

        # Guarantee at least one recommendation (fallback if filtering yields none)
        if not recommended and templates_raw:
            fallback = templates_raw[:1]
            for tpl in fallback:
                min_cov = float(tpl.get('min_coverage_amount') or 0)
                max_cov = float(tpl.get('max_coverage_amount') or min_cov)
                base_premium = float(tpl.get('base_premium') or 0)
                premium_est = round(base_premium * 1.1, 2)
                recommended.append({
                    "template_id": tpl.get('template_id'),
                    "policy_name": tpl.get('policy_name'),
                    "policy_type": tpl.get('policy_type'),
                    "provider_name": tpl.get('provider_name'),
                    "estimated_coverage_amount": min_cov,
                    "coverage_range": f"₹{int(min_cov)} - ₹{int(max_cov)}",
                    "premium_estimate": premium_est,
                    "premium_range": f"₹{int(premium_est*0.9)} - ₹{int(premium_est*1.2)}",
                    "legal_compliance": tpl.get('legal_compliance', True),
                    "compliance_authority": tpl.get('compliance_authority', 'IRDAI'),
                    "compliance_badge": ("✅ IRDAI Approved" if tpl.get('legal_compliance') else "⚠️ Review Required"),
                    "coverage_details": tpl.get('coverage_description'),
                    "exclusions": tpl.get('exclusions_description'),
                    "optional_addons": tpl.get('optional_addons'),
                    "risk_match": [],
                    "match_score": 0,
                    "reason": "Core policy offered as a baseline recommendation (no direct risk match found)."
                })

        # Sort by match_score descending
        recommended.sort(key=lambda r: r.get('match_score', 0), reverse=True)

        # Persist assessment if table exists
        assessment_id = None
        try:
            # Mark previous as not current
            supabase.table('business_risk_assessments').update({"is_current": False}).eq('user_id', int(current_user)).eq('is_current', True).execute()
            ins = supabase.table('business_risk_assessments').insert({
                'business_id': None,  # Optional: require business linkage later
                'user_id': int(current_user),
                'assessment_data': req.model_dump(),
                'risk_score': int(risk_calc['risk_score']),
                'risk_level': risk_calc['risk_level'],
                'identified_risks': req.risk_concerns,
                'recommended_policies': [r['policy_type'] for r in recommended],
                'is_current': True
            }).execute()
            if ins.data:
                assessment_id = ins.data[0].get('assessment_id')
            print(f"✅ Saved assessment {assessment_id} to database")
        except Exception as e:
            print(f"ℹ️ Could not persist risk assessment to DB: {e}")
            # Create a simple in-memory assessment ID for tracking
            import time
            assessment_id = f"temp_{int(current_user)}_{int(time.time())}"
            print(f"✅ Created temporary assessment ID: {assessment_id}")

        return {
            "success": True,
            "assessment_id": assessment_id,
            **risk_calc,
            "recommendations": recommended,
            "count": len(recommended)
        }
    except Exception as e:
        print(f"❌ Insurance assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@app.post('/insurance/policies')
async def create_insurance_policy(payload: InsurancePolicyCreate, current_user: str = Depends(get_current_user)):
    """Store a selected / purchased insurance policy for tracking & reminders."""
    try:
        data = payload.model_dump()
        data['user_id'] = int(current_user)
        # Auto provider fallback
        if not data.get('provider_name'):
            data['provider_name'] = 'Not Specified'
        # Insert
        res = supabase.table('insurance_policies').insert(data).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Insert failed")
        policy = res.data[0]
        # Create auto reminder 30 days prior if expiry exists
        try:
            if policy.get('expiry_date'):
                from datetime import datetime as _dt, timedelta as _td
                expiry_dt = _dt.fromisoformat(policy['expiry_date']) if isinstance(policy['expiry_date'], str) else policy['expiry_date']
                reminder_date = expiry_dt - _td(days=30)
                if reminder_date.date() > _dt.utcnow().date():
                    supabase.table('policy_reminders').insert({
                        'policy_id': policy['policy_id'],
                        'user_id': int(current_user),
                        'reminder_type': 'renewal',
                        'reminder_date': reminder_date.date().isoformat(),
                        'notification_message': f"Renewal reminder for {policy['policy_name']}"
                    }).execute()
        except Exception as e:
            print(f"ℹ️ Could not create reminder: {e}")
        return {"success": True, "policy": policy}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Create policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create policy: {str(e)}")

@app.get('/insurance/policies')
async def list_insurance_policies(current_user: str = Depends(get_current_user)):
    try:
        res = supabase.table('insurance_policies').select('*').eq('user_id', int(current_user)).order('created_at', desc=True).execute()
        policies = res.data or []
        # annotate days to expiry
        annotated = []
        for p in policies:
            expiry = p.get('expiry_date')
            days_to_expiry = None
            if expiry:
                try:
                    from datetime import datetime as _dt
                    exp_dt = _dt.fromisoformat(expiry) if isinstance(expiry, str) else expiry
                    days_to_expiry = (exp_dt.date() - _dt.utcnow().date()).days
                except Exception:
                    pass
            p['days_to_expiry'] = days_to_expiry
            p['compliance_badge'] = "✅ IRDAI Approved" if p.get('legal_compliance') else "⚠️ Review"
            annotated.append(p)
        return {"success": True, "policies": annotated, "count": len(annotated)}
    except Exception as e:
        print(f"❌ List policies error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list policies: {str(e)}")

@app.get('/insurance/policies/{policy_id}')
async def get_insurance_policy(policy_id: int, current_user: str = Depends(get_current_user)):
    try:
        res = supabase.table('insurance_policies').select('*').eq('policy_id', policy_id).eq('user_id', int(current_user)).limit(1).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Policy not found")
        p = res.data[0]
        p['compliance_badge'] = "✅ IRDAI Approved" if p.get('legal_compliance') else "⚠️ Review"
        return {"success": True, "policy": p}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get policy: {str(e)}")

@app.put('/insurance/policies/{policy_id}')
async def update_insurance_policy(policy_id: int, payload: InsurancePolicyUpdate, current_user: str = Depends(get_current_user)):
    try:
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not data:
            raise HTTPException(status_code=400, detail="No changes provided")
        res = supabase.table('insurance_policies').update(data).eq('policy_id', policy_id).eq('user_id', int(current_user)).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Policy not found or not updated")
        return {"success": True, "policy": res.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Update policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update policy: {str(e)}")

@app.post('/insurance/policies/{policy_id}/upload-document')
async def upload_policy_document(policy_id: int, file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    try:
        # Save locally (placeholder). In production use Supabase Storage / S3.
        docs_dir = Path('policy_docs')
        docs_dir.mkdir(exist_ok=True)
        ext = file.filename.split('.')[-1]
        fname = f"policy_{policy_id}_{uuid4().hex}.{ext}"
        path = docs_dir / fname
        with path.open('wb') as f:
            shutil.copyfileobj(file.file, f)
        doc_url = f"/static/policy_docs/{fname}"  # placeholder path
        # Update record
        supabase.table('insurance_policies').update({
            'document_url': str(path),
            'document_filename': file.filename
        }).eq('policy_id', policy_id).eq('user_id', int(current_user)).execute()
        return {"success": True, "document_url": str(path), "stored_as": fname}
    except Exception as e:
        print(f"❌ Upload policy document error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@app.get('/insurance/policies/compare')
async def compare_policies(ids: str, current_user: str = Depends(get_current_user)):
    try:
        id_list = [int(i) for i in ids.split(',') if i.strip().isdigit()][:10]
        if not id_list:
            raise HTTPException(status_code=400, detail="No valid ids provided")
        res = supabase.table('insurance_policies').select('*').in_('policy_id', id_list).eq('user_id', int(current_user)).execute()
        policies = res.data or []
        # Build comparison matrix
        fields = ['policy_name', 'policy_type', 'coverage_amount', 'premium_amount', 'expiry_date', 'legal_compliance']
        comparison = []
        for p in policies:
            comparison.append({f: p.get(f) for f in fields} | {"policy_id": p.get('policy_id')})
        return {"success": True, "comparison": comparison, "count": len(comparison)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Compare policies error: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.post('/insurance/connect-advisor')
async def connect_advisor(payload: AdvisorConnectRequest, current_user: str = Depends(get_current_user)):
    try:
        # Placeholder: just echo request; future: store or send email / queue
        ticket_id = f"ADV-{uuid4().hex[:8].upper()}"
        return {"success": True, "ticket_id": ticket_id, "message": "Advisor request received. We'll reach out soon.", "echo": payload.model_dump()}
    except Exception as e:
        print(f"❌ Advisor connect error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create advisor request: {str(e)}")

@app.get('/insurance/reminders')
async def list_policy_reminders(current_user: str = Depends(get_current_user)):
    """List upcoming policy renewal reminders for the user (next 120 days)."""
    try:
        from datetime import datetime as _dt, timedelta as _td
        today = _dt.utcnow().date().isoformat()
        future = (_dt.utcnow() + _td(days=120)).date().isoformat()
        res = supabase.table('policy_reminders').select('*').eq('user_id', int(current_user)).gte('reminder_date', today).lte('reminder_date', future).order('reminder_date', desc=False).execute()
        reminders = res.data or []
        return {"success": True, "reminders": reminders, "count": len(reminders)}
    except Exception as e:
        print(f"❌ List reminders error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list reminders: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Nexora Credit Score API with Supabase Database...")
    uvicorn.run("combined_api:app", host="0.0.0.0", port=8001, reload=False)
