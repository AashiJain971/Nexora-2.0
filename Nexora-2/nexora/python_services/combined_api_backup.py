#!/usr/bin/env python3
"""
Nexora Credit Score API - Supabase Database Only
This version uses only Supabase database, no        # Check if tables exist by querying them
        try:
            # Try to select from users table
            result = supabase.table('users').select('id').limit(1).execute()
            print("✅ Users table exists and is accessible")
            
            # Try to select from invoices table
            result = supabase.table('invoices').select('id').limit(1).execute()
            print("✅ Invoices table exists and is accessible")
            return True
        except Exception as e:
            error_msg = str(e)
            if 'users' in error_msg or 'invoices' in error_msg:
                print("⚠️ Database tables not found or not accessible")
                print("💡 Please create the database tables in your Supabase SQL editor.")
                print("🔗 Go to: https://eecbqzvcnwrkcxgwjxlt.supabase.co")
                print("� Navigate to 'SQL Editor' and run the schema from supabase_schema.sql")
            else:
                print(f"⚠️ Database error: {error_msg}")
            return Falsetorage
"""

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
from policy_generator import (
    BusinessDetails, 
    PolicyGenerateRequest, 
    generate_policies,
    determine_compliance_regions
)
from dotenv import load_dotenv
from supabase import create_client, Client
import uvicorn

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://eecbqzvcnwrkcxgwjxlt.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVlY2JxenZjbndya2N4Z3dqeGx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0Mjk1NjEsImV4cCI6MjA3MTAwNTU2MX0.CkhFT-6LKFg6NCc9WIiZRjNQ7VGVX6nJmoOxjMVHDKs")

# GROQ API configuration
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

def verify_token(token: str):
    """Verify JWT token and return user ID"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise jwt.InvalidTokenError("Invalid token payload")
        return user_id
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")

# ----------------- Database Initialization ----------------- #
def init_database_tables():
    """Initialize database tables using raw SQL"""
    try:
        print("🔧 Checking Supabase database tables...")
        
        # Check if tables exist by querying them
        try:
            # Try to select from users table
            result = supabase.table('users').select('id').limit(1).execute()
            print("✅ Users table exists and is accessible")
            return True
        except Exception as e:
            print("⚠️ Users table not found or not accessible")
            print("💡 Please create the users table in your Supabase SQL editor.")
            print("🔗 Go to: https://eecbqzvcnwrkcxgwjxlt.supabase.co")
            print("� Navigate to 'SQL Editor' and run the schema from supabase_schema.sql")
            return False
            
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        print("💡 Please ensure your Supabase database is properly configured")
        return False

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
            "upload": "/process-invoice",
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
        try:
            result = supabase.table("users").insert(user_data).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create user - no data returned")
        except Exception as db_error:
            error_msg = str(db_error)
            if "table 'public.users'" in error_msg and "not exist" in error_msg:
                raise HTTPException(
                    status_code=500, 
                    detail="Database tables not found. Please create the users table in your Supabase SQL editor first. Check the server logs for SQL commands."
                )
            elif "already exists" in error_msg or "duplicate" in error_msg:
                raise HTTPException(status_code=400, detail="Email already registered")
            else:
                print(f"Database error: {error_msg}")
                raise HTTPException(status_code=500, detail=f"Database error: {error_msg}")
        
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

@app.post("/process-invoice")
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
        try:
            invoice_result = await asyncio.to_thread(extract_invoice_main, temp_file_path, GROQ_API_KEY)
            print(f"🔍 Invoice extraction result: {invoice_result}")
        except Exception as e:
            print(f"❌ Invoice extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Invoice extraction failed: {str(e)}")
        
        # Normalize / validate invoice_result
        # The extractor may return a JSON string (from invoice_2.structure_invoice_json) instead of a dict with success flag
        if isinstance(invoice_result, str):
            try:
                parsed = json.loads(invoice_result)
                # Wrap into expected structure if needed
                if isinstance(parsed, dict) and 'success' not in parsed:
                    invoice_result = {"success": True, **parsed}
                else:
                    invoice_result = parsed
                print("🔄 Parsed string invoice_result into dict")
            except json.JSONDecodeError as je:
                print(f"❌ Could not parse invoice extraction string as JSON: {je}")
                raise HTTPException(status_code=500, detail="Invoice extraction produced invalid JSON output")

        if not isinstance(invoice_result, dict):
            print(f"❌ Invoice extraction output is not a dict: {type(invoice_result)} -> {invoice_result}")
            raise HTTPException(status_code=500, detail="Invoice extraction returned unsupported data format")

        # Empty dict means extraction failed
        if not invoice_result:
            raise HTTPException(status_code=400, detail="Invoice extraction failed: empty result")

        # Treat absence of explicit success flag as success (legacy extractor)
        if invoice_result.get("success") is False:
            raise HTTPException(status_code=400, detail=f"Invoice extraction failed: {invoice_result.get('error', 'Unknown error')}")

        if 'invoice_details' not in invoice_result:
            # Provide a graceful fallback so user still gets a stored record instead of generic 500
            print("⚠️ Invoice extraction missing 'invoice_details'; generating placeholder.")
            import uuid
            placeholder_invoice = {
                "invoice_number": f"TEMP-{int(datetime.now().timestamp())}-{str(uuid.uuid4())[:8]}",
                "client": "Unknown",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "payment_terms": "N/A",
                "industry": "General",
                "total_amount": 0.0,
                "currency": "USD",
                "pending_amount": 0.0,
                "small_analysis": "Placeholder invoice created due to extraction issue",
                "line_items": [],
                "tax_amount": 0.0,
                "extra_charges": 0.0
            }
            invoice_result['invoice_details'] = placeholder_invoice

        invoice_details = invoice_result['invoice_details']
        if not isinstance(invoice_details, dict):
            raise HTTPException(status_code=500, detail="Invoice extraction returned malformed invoice details")

        invoice_number = invoice_details.get('invoice_number', 'Unknown')
        print(f"✅ Invoice extracted: {invoice_number}")
        
        # Get all existing invoices for user to calculate historical data
        existing_invoices = supabase.table('invoices').select('*').eq('user_id', int(current_user)).execute()
        total_invoices = len(existing_invoices.data) if existing_invoices.data else 0
        
        # Calculate total amounts for credit score calculation
        total_amount = sum([inv['total_amount'] for inv in existing_invoices.data]) if existing_invoices.data else 0
        total_amount += float(invoice_details['total_amount'])
        
        # Calculate credit score for this invoice
        print("📊 Calculating credit score...")
        credit_score_data = {
            "no_of_invoices": total_invoices + 1,
            "total_amount": total_amount,
            "total_amount_pending": float(invoice_details['total_amount']),
            "total_amount_paid": total_amount - float(invoice_details['total_amount']),
            "tax": float(invoice_details.get('tax_amount', 0)),
            "extra_charges": float(invoice_details.get('extra_charges', 0)),
            "payment_completion_rate": 0.8,  # Default assumption
            "paid_to_pending_ratio": 0.6     # Default assumption
        }
        
        print(f"📊 Credit score data: {credit_score_data}")
        try:
            credit_score_result = await asyncio.to_thread(calculate_credit_score_main, credit_score_data, GROQ_API_KEY)
            print(f"📊 Credit score result: {credit_score_result}")
        except Exception as e:
            print(f"❌ Credit score calculation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Credit score calculation failed: {str(e)}")
        
        # Parse credit score result if it's a JSON string
        if isinstance(credit_score_result, str):
            try:
                credit_score_result = json.loads(credit_score_result)
                print("🔄 Parsed credit score result from JSON string")
            except json.JSONDecodeError as je:
                print(f"❌ Could not parse credit score result as JSON: {je}")
                # Provide fallback structure
                credit_score_result = {
                    "credit_score_analysis": {
                        "final_weighted_credit_score": 0
                    }
                }
        
        individual_credit_score = credit_score_result.get('credit_score_analysis', {}).get('final_weighted_credit_score', 0)
        
        print(f"✅ Individual credit score calculated: {individual_credit_score}")
        
        # Prepare invoice data for database
        invoice_db_data = {
            "user_id": int(current_user),
            "invoice_number": invoice_details["invoice_number"],
            "client": invoice_details["client"],
            "date": invoice_details.get("date"),
            "payment_terms": invoice_details.get("payment_terms"),
            "industry": invoice_details.get("industry", "General"),
            "total_amount": float(invoice_details["total_amount"]),
            "currency": invoice_details.get("currency", "INR")[:10],  # Truncate to 10 chars
            "tax_amount": float(invoice_details.get("tax_amount", 0)),
            "extra_charges": float(invoice_details.get("extra_charges", 0)),
            "line_items": invoice_details.get("line_items", []),
            "status": "pending",
            "credit_score": individual_credit_score,
            "credit_score_data": credit_score_result.get('credit_score_analysis', {})
        }

        # Check for duplicate invoice number for this user
        existing_invoice = supabase.table("invoices").select("id").eq("user_id", int(current_user)).eq("invoice_number", invoice_db_data["invoice_number"]).execute()
        
        if existing_invoice.data:
            # Make invoice number unique by appending timestamp
            import uuid
            original_number = invoice_db_data["invoice_number"]
            invoice_db_data["invoice_number"] = f"{original_number}-{int(datetime.now().timestamp())}-{str(uuid.uuid4())[:8]}"
            print(f"⚠️ Duplicate invoice number detected, using unique number: {invoice_db_data['invoice_number']}")
        
        # Insert invoice into database
        print("💾 Saving invoice to Supabase...")
        print(f"💾 Invoice data: {invoice_db_data}")
        try:
            result = supabase.table("invoices").insert(invoice_db_data).execute()
            print(f"💾 Database result: {result}")
        except Exception as e:
            print(f"❌ Database save failed: {e}")
            raise HTTPException(status_code=500, detail=f"Database save failed: {str(e)}")
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save invoice to database")
        
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
            "credit_score_analysis": credit_score_result.get('credit_score_analysis', {}),
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
        print(f"❌ Error type: {type(e).__name__}")
        print(f"❌ Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Invoice processing failed: {str(e)}")

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
        
        try:
            # Try to get invoices from database first
            result = supabase.table('invoices').select('*').eq('user_id', int(current_user)).order('created_at', desc=True).execute()
            invoices = result.data or []
            
            if invoices:
                print(f"✅ Retrieved {len(invoices)} invoices from Supabase")
                return {
                    "success": True,
                    "invoices": invoices,
                    "total_count": len(invoices)
                }
        except Exception as db_error:
            print(f"⚠️ Database table not found, using mock data: {db_error}")
            
        # If database tables don't exist or no data, return mock invoices with proper line_items
        mock_invoices = [
            {
                "id": 1,
                "user_id": int(current_user),
                "invoice_number": "INV-2024-001",
                "client": "TechStart Solutions Pvt Ltd",
                "date": "2024-01-15",
                "payment_terms": "Net 30 days",
                "industry": "Technology",
                "total_amount": 25000.00,
                "currency": "INR",
                "tax_amount": 4500.00,
                "extra_charges": 500.00,
                "line_items": [
                    {"description": "Web Development Service", "amount": 15000.00},
                    {"description": "Mobile App UI/UX Design", "amount": 8000.00},
                    {"description": "Database Setup & Configuration", "amount": 2000.00}
                ],
                "status": "pending",
                "credit_score": 78.5,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "user_id": int(current_user),
                "invoice_number": "INV-2024-002",
                "client": "Digital Marketing Agency",
                "date": "2024-01-20",
                "payment_terms": "Net 15 days",
                "industry": "Marketing",
                "total_amount": 18000.00,
                "currency": "INR",
                "tax_amount": 3240.00,
                "extra_charges": 0.00,
                "line_items": [
                    {"description": "SEO Optimization Service", "amount": 12000.00},
                    {"description": "Google Ads Campaign Setup", "amount": 6000.00}
                ],
                "status": "paid",
                "credit_score": 85.2,
                "created_at": "2024-01-20T14:45:00Z",
                "updated_at": "2024-01-25T09:15:00Z"
            },
            {
                "id": 3,
                "user_id": int(current_user),
                "invoice_number": "INV-2024-003",
                "client": "E-commerce Startup",
                "date": "2024-02-01",
                "payment_terms": "Net 30 days",
                "industry": "E-commerce",
                "total_amount": 35000.00,
                "currency": "INR",
                "tax_amount": 6300.00,
                "extra_charges": 1200.00,
                "line_items": [
                    {"description": "Full E-commerce Platform Development", "amount": 22000.00},
                    {"description": "Payment Gateway Integration", "amount": 5000.00},
                    {"description": "Shopping Cart & Inventory System", "amount": 8000.00}
                ],
                "status": "pending",
                "credit_score": 82.1,
                "created_at": "2024-02-01T11:20:00Z",
                "updated_at": "2024-02-01T11:20:00Z"
            },
            {
                "id": 4,
                "user_id": int(current_user),
                "invoice_number": "INV-2024-004",
                "client": "Healthcare Solutions Ltd",
                "date": "2024-02-10",
                "payment_terms": "Net 45 days",
                "industry": "Healthcare",
                "total_amount": 42000.00,
                "currency": "INR",
                "tax_amount": 7560.00,
                "extra_charges": 800.00,
                "line_items": [
                    {"description": "Patient Management System", "amount": 28000.00},
                    {"description": "Appointment Booking Module", "amount": 8000.00},
                    {"description": "Medical Records Database", "amount": 6000.00}
                ],
                "status": "pending",
                "credit_score": 79.8,
                "created_at": "2024-02-10T16:30:00Z",
                "updated_at": "2024-02-10T16:30:00Z"
            }
        ]
        
        print(f"✅ Using mock data: {len(mock_invoices)} sample invoices with line items")
        
        return {
            "success": True,
            "invoices": mock_invoices,
            "total_count": len(mock_invoices)
        }
        
    except Exception as e:
        print(f"❌ Error fetching user invoices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")

@app.get("/test/invoices")
async def test_invoices():
    """Test endpoint to verify line_items structure without authentication"""
    mock_invoices = [
        {
            "id": 1,
            "user_id": 1,
            "invoice_number": "TEST-001",
            "client": "Test Client",
            "date": "2024-01-15",
            "payment_terms": "Net 30 days",
            "industry": "Technology",
            "total_amount": 15000.00,
            "currency": "INR",
            "tax_amount": 2250.00,
            "extra_charges": 0.00,
            "line_items": [
                {"description": "Web Development", "amount": 10000.00},
                {"description": "Testing & QA", "amount": 5000.00}
            ],
            "status": "pending",
            "created_at": "2024-01-15T10:30:00Z",
        }
    ]
    
    return {
        "success": True,
        "invoices": mock_invoices,
        "total_count": len(mock_invoices)
    }

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

@app.post("/calculate-credit-score")
async def calculate_credit_score(credit_data: dict):
    """Calculate credit score (main endpoint that frontend expects)"""
    try:
        print("📊 Calculating credit score...")
        result = await asyncio.to_thread(calculate_credit_score_main, credit_data, GROQ_API_KEY)
        print("✅ Credit score calculated successfully")
        return result
    except Exception as e:
        print(f"❌ Credit score calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Credit score calculation failed: {str(e)}")

# ----------------- Privacy Policy Generator Endpoints ----------------- #

@app.post("/register-business")
async def register_business(business_data: BusinessDetails, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Register business details for policy generation"""
    try:
        # Verify JWT token
        user_id = verify_token(credentials.credentials)
        
        # Convert Pydantic model to dict
        business_dict = business_data.dict()
        business_dict['user_id'] = user_id
        business_dict['created_at'] = datetime.utcnow().isoformat()
        business_dict['updated_at'] = datetime.utcnow().isoformat()
        
        # Check if business already exists for this user
        existing = supabase.table('businesses').select('*').eq('user_id', user_id).execute()
        
        if existing.data:
            # Update existing business
            result = supabase.table('businesses').update(business_dict).eq('user_id', user_id).execute()
            print(f"✅ Business updated for user {user_id}")
        else:
            # Insert new business
            result = supabase.table('businesses').insert(business_dict).execute()
            print(f"✅ Business registered for user {user_id}")
        
        return {"success": True, "message": "Business details saved successfully", "data": result.data[0]}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Business registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/get-business")
async def get_business(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get business details for the authenticated user"""
    try:
        # Verify JWT token
        user_id = verify_token(credentials.credentials)
        
        # Get business details
        result = supabase.table('businesses').select('*').eq('user_id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Business not found")
        
        return {"success": True, "data": result.data[0]}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Get business error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get business: {str(e)}")

@app.post("/generate-policies")
async def generate_policies_endpoint(request: PolicyGenerateRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate legal policies based on business details"""
    try:
        # Verify JWT token
        user_id = verify_token(credentials.credentials)
        
        # Generate policies
        policies = generate_policies(request.business_details, request.policy_types, request.language)
        
        # Save each policy to database
        policy_records = []
        for policy_type, content in policies.items():
            policy_data = {
                'user_id': user_id,
                'business_name': request.business_details.business_name,
                'policy_type': policy_type,
                'content': content,
                'language': request.language,
                'compliance_regions': determine_compliance_regions(request.business_details.location_country),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Check if policy already exists
            existing = supabase.table('policies').select('*').eq('user_id', user_id).eq('policy_type', policy_type).execute()
            
            if existing.data:
                # Update existing policy
                policy_data['updated_at'] = datetime.utcnow().isoformat()
                result = supabase.table('policies').update(policy_data).eq('user_id', user_id).eq('policy_type', policy_type).execute()
                policy_records.append(result.data[0])
            else:
                # Insert new policy
                result = supabase.table('policies').insert(policy_data).execute()
                policy_records.append(result.data[0])
        
        print(f"✅ Generated {len(policies)} policies for user {user_id}")
        
        return {
            "success": True, 
            "message": f"Generated {len(policies)} policies successfully",
            "policies": policies,
            "policy_records": policy_records
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Policy generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Policy generation failed: {str(e)}")

@app.get("/get-policies")
async def get_user_policies(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all generated policies for the authenticated user"""
    try:
        # Verify JWT token
        user_id = verify_token(credentials.credentials)
        
        # Get all policies for user
        result = supabase.table('policies').select('*').eq('user_id', user_id).order('generated_at', desc=True).execute()
        
        return {"success": True, "data": result.data}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Get policies error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get policies: {str(e)}")

@app.get("/get-policy/{policy_id}")
async def get_policy_by_id(policy_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get a specific policy by ID"""
    try:
        # Verify JWT token
        user_id = verify_token(credentials.credentials)
        
        # Get policy
        result = supabase.table('policies').select('*').eq('id', policy_id).eq('user_id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return {"success": True, "data": result.data[0]}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Get policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get policy: {str(e)}")

@app.delete("/delete-policy/{policy_id}")
async def delete_policy(policy_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete a specific policy"""
    try:
        # Verify JWT token
        user_id = verify_token(credentials.credentials)
        
        # Delete policy
        result = supabase.table('policies').delete().eq('id', policy_id).eq('user_id', user_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        print(f"✅ Policy {policy_id} deleted for user {user_id}")
        
        return {"success": True, "message": "Policy deleted successfully"}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Delete policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete policy: {str(e)}")

# =============================================================================
# INSURANCE HUB ENDPOINTS
# =============================================================================

from pydantic import Field
from datetime import date

# Insurance-related models
class BusinessRiskAssessment(BaseModel):
    business_type: str
    industry: str
    employee_count: int
    annual_revenue: Optional[float] = None
    assets: Dict[str, float]  # {"machinery": 500000, "inventory": 200000}
    risk_concerns: List[str]  # ["fire", "theft", "cyber", "employee_welfare"]
    has_existing_insurance: bool = False
    existing_policies: Optional[List[str]] = []

class InsuranceRecommendationRequest(BaseModel):
    business_assessment: BusinessRiskAssessment

class InsurancePolicyRequest(BaseModel):
    policy_name: str
    policy_type: str
    provider_name: str
    coverage_amount: float
    premium_amount: float
    premium_frequency: str = "annual"
    start_date: date
    expiry_date: date
    policy_number: Optional[str] = None
    document_url: Optional[str] = None
    notes: Optional[str] = None

class InsurancePolicyUpdate(BaseModel):
    policy_name: Optional[str] = None
    coverage_amount: Optional[float] = None
    premium_amount: Optional[float] = None
    expiry_date: Optional[date] = None
    policy_number: Optional[str] = None
    document_url: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

@app.post("/insurance/assess-risk")
async def assess_business_risk(request: InsuranceRecommendationRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Assess business risk and provide insurance recommendations"""
    try:
        user_id = verify_token(credentials.credentials)
        assessment = request.business_assessment
        
        # Calculate risk score based on business factors
        risk_score = calculate_risk_score(assessment)
        
        # Get recommended insurance templates
        recommendations = await get_insurance_recommendations(assessment, risk_score)
        
        # Save risk assessment
        assessment_data = {
            'user_id': user_id,
            'assessment_data': assessment.dict(),
            'recommended_policies': recommendations,
            'risk_score': risk_score,
            'priority_risks': get_priority_risks(assessment.risk_concerns)
        }
        
        # Check if business exists
        business_result = supabase.table('businesses').select('id').eq('user_id', user_id).execute()
        if business_result.data:
            assessment_data['business_id'] = business_result.data[0]['id']
        
        result = supabase.table('business_risk_assessments').insert(assessment_data).execute()
        
        return {
            "success": True,
            "risk_score": risk_score,
            "priority_risks": get_priority_risks(assessment.risk_concerns),
            "recommendations": recommendations,
            "assessment_id": result.data[0]['id']
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Risk assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@app.post("/insurance/policies")
async def add_insurance_policy(policy: InsurancePolicyRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Add a new insurance policy to user's portfolio"""
    try:
        user_id = verify_token(credentials.credentials)
        
        policy_data = {
            'user_id': user_id,
            **policy.dict()
        }
        
        # Get business ID if exists
        business_result = supabase.table('businesses').select('id').eq('user_id', user_id).execute()
        if business_result.data:
            policy_data['business_id'] = business_result.data[0]['id']
        
        result = supabase.table('insurance_policies').insert(policy_data).execute()
        
        return {"success": True, "message": "Insurance policy added successfully", "policy": result.data[0]}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Add insurance policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add policy: {str(e)}")

@app.get("/insurance/policies")
async def get_user_insurance_policies(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all insurance policies for the authenticated user"""
    try:
        user_id = verify_token(credentials.credentials)
        
        result = supabase.table('insurance_policies')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('expiry_date', desc=False)\
            .execute()
        
        return {"success": True, "policies": result.data}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Get insurance policies error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get policies: {str(e)}")

@app.get("/insurance/expiring")
async def get_expiring_policies(days: int = 30, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get policies expiring within specified days"""
    try:
        user_id = verify_token(credentials.credentials)
        
        expiry_threshold = (datetime.now() + timedelta(days=days)).date()
        
        result = supabase.table('insurance_policies')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('status', 'active')\
            .lte('expiry_date', expiry_threshold.isoformat())\
            .order('expiry_date')\
            .execute()
        
        return {"success": True, "expiring_policies": result.data, "days": days}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Get expiring policies error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get expiring policies: {str(e)}")

@app.get("/insurance/templates")
async def get_insurance_templates(business_type: Optional[str] = None, policy_type: Optional[str] = None):
    """Get available insurance templates for recommendations"""
    try:
        # Mock data for demo purposes (until Supabase tables are created)
        mock_templates = [
            {
                "id": 1,
                "name": "Professional Indemnity Insurance",
                "provider": "HDFC ERGO",
                "policy_type": "professional_indemnity",
                "description": "Protection against professional errors and omissions for service businesses",
                "base_premium": 15000,
                "coverage_amount": 1000000,
                "is_irdai_approved": True,
                "compliance_level": "full",
                "business_types": ["technology", "consulting", "professional_services"],
                "features": ["errors_omissions", "legal_costs", "defense_costs"],
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "name": "Cyber Liability Insurance", 
                "provider": "ICICI Lombard",
                "policy_type": "cyber_liability",
                "description": "Comprehensive protection against cyber attacks and data breaches",
                "base_premium": 25000,
                "coverage_amount": 2000000,
                "is_irdai_approved": True,
                "compliance_level": "full",
                "business_types": ["technology", "ecommerce", "financial_services"],
                "features": ["data_breach", "cyber_extortion", "business_interruption"],
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 3,
                "name": "Public Liability Insurance",
                "provider": "New India Assurance", 
                "policy_type": "public_liability",
                "description": "Coverage for third-party claims and public liability incidents",
                "base_premium": 12000,
                "coverage_amount": 500000,
                "is_irdai_approved": True,
                "compliance_level": "full",
                "business_types": ["retail", "manufacturing", "hospitality"],
                "features": ["third_party_injury", "property_damage", "legal_expenses"],
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 4,
                "name": "Product Liability Insurance",
                "provider": "Bajaj Allianz",
                "policy_type": "product_liability", 
                "description": "Protection against claims from defective products",
                "base_premium": 18000,
                "coverage_amount": 1500000,
                "is_irdai_approved": True,
                "compliance_level": "full",
                "business_types": ["manufacturing", "retail", "food_beverage"],
                "features": ["product_defects", "recall_costs", "legal_defense"],
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 5,
                "name": "Directors & Officers Insurance",
                "provider": "Tata AIG",
                "policy_type": "directors_officers",
                "description": "Protection for company directors and officers against management liability",
                "base_premium": 35000,
                "coverage_amount": 5000000,
                "is_irdai_approved": True,
                "compliance_level": "full", 
                "business_types": ["technology", "financial_services", "healthcare"],
                "features": ["management_liability", "legal_costs", "regulatory_investigations"],
                "created_at": "2024-01-15T10:30:00Z"
            }
        ]
        
        try:
            # Try database first
            query = supabase.table('insurance_templates').select('*')
            
            if business_type:
                query = query.contains('business_types', [business_type])
            
            if policy_type:
                query = query.eq('policy_type', policy_type)
            
            result = query.execute()
            if result.data:
                return {"success": True, "templates": result.data}
        except Exception:
            # Database tables don't exist, use mock data
            pass
        
        # Filter mock data
        templates = mock_templates
        if business_type:
            templates = [t for t in templates if business_type in t["business_types"]]
        if policy_type:
            templates = [t for t in templates if t["policy_type"] == policy_type]
        
        return {"success": True, "templates": templates}
        
    except Exception as e:
        print(f"❌ Get insurance templates error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

# Helper functions for insurance
def calculate_risk_score(assessment: BusinessRiskAssessment) -> int:
    """Calculate risk score based on business assessment"""
    score = 50  # Base score
    
    # Business type risk factors
    high_risk_types = ['manufacturing', 'chemical', 'construction']
    if assessment.business_type.lower() in high_risk_types:
        score += 20
    
    # Employee count factor
    if assessment.employee_count > 100:
        score += 15
    elif assessment.employee_count > 50:
        score += 10
    elif assessment.employee_count > 10:
        score += 5
    
    # Risk concerns factor
    risk_weights = {
        'fire': 15, 'theft': 10, 'cyber': 12, 'employee_welfare': 8,
        'natural_disasters': 15, 'liability': 10, 'transport': 8
    }
    for risk in assessment.risk_concerns:
        score += risk_weights.get(risk.lower(), 5)
    
    # Asset value factor
    total_assets = sum(assessment.assets.values())
    if total_assets > 10000000:  # 1 crore
        score += 20
    elif total_assets > 5000000:  # 50 lakh
        score += 15
    elif total_assets > 1000000:  # 10 lakh
        score += 10
    
    return min(score, 100)  # Cap at 100

async def get_insurance_recommendations(assessment: BusinessRiskAssessment, risk_score: int) -> List[Dict]:
    """Get insurance recommendations based on assessment"""
    try:
        # Get templates matching business type and risk concerns
        templates_result = supabase.table('insurance_templates')\
            .select('*')\
            .contains('business_types', [assessment.business_type])\
            .execute()
        
        recommendations = []
        for template in templates_result.data:
            # Calculate relevance score
            relevance_score = 0
            
            # Check risk category match
            template_risks = template.get('risk_categories', [])
            matching_risks = set(assessment.risk_concerns).intersection(set(template_risks))
            relevance_score += len(matching_risks) * 20
            
            # Business size match
            if (template.get('min_business_size', 1) <= assessment.employee_count):
                relevance_score += 10
            
            # Only recommend if relevance > 20
            if relevance_score >= 20:
                # Calculate estimated premium based on assessment
                base_premium = template['premium_range_min']
                risk_multiplier = 1 + (risk_score - 50) / 100  # Adjust based on risk
                estimated_premium = base_premium * risk_multiplier
                
                recommendation = {
                    'template_id': template['id'],
                    'policy_name': template['policy_name'],
                    'policy_type': template['policy_type'],
                    'provider_name': template['provider_name'],
                    'coverage_description': template['coverage_description'],
                    'recommended_coverage': template['base_coverage_amount'],
                    'estimated_premium': round(estimated_premium, 2),
                    'legal_compliance': template['legal_compliance'],
                    'compliance_authority': template['compliance_authority'],
                    'coverage_features': template['coverage_features'],
                    'optional_addons': template['optional_addons'],
                    'relevance_score': relevance_score,
                    'matching_risks': list(matching_risks)
                }
                recommendations.append(recommendation)
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommendations[:6]  # Return top 6 recommendations
        
    except Exception as e:
        print(f"❌ Get insurance recommendations error: {e}")
        return []

def get_priority_risks(risk_concerns: List[str]) -> List[str]:
    """Get top 3 priority risks based on severity"""
    risk_priorities = {
        'fire': 10, 'cyber': 9, 'liability': 8, 'theft': 7,
        'employee_welfare': 6, 'natural_disasters': 9, 'transport': 5
    }
    
    sorted_risks = sorted(risk_concerns, key=lambda x: risk_priorities.get(x.lower(), 1), reverse=True)
    return sorted_risks[:3]

@app.post("/insurance/risk-assessment")
async def submit_risk_assessment(
    business_type: str,
    industry: str,
    employee_count: int,
    annual_revenue: Optional[float] = None,
    risk_concerns: List[str] = [],
    current_user: str = Depends(get_current_user)
):
    """Submit business risk assessment and get personalized insurance recommendations"""
    try:
        # Calculate risk score based on input
        score = 0
        
        # Business type risk factors
        business_risk = {
            'manufacturing': 25,
            'retail': 15,
            'services': 10,
            'digital': 20,
            'e-commerce': 18
        }
        score += business_risk.get(business_type, 15)
        
        # Employee count factor
        if employee_count > 100:
            score += 20
        elif employee_count > 50:
            score += 15
        elif employee_count > 10:
            score += 10
        else:
            score += 5
        
        # Risk concerns factor
        score += len(risk_concerns) * 5
        
        # Annual revenue factor
        if annual_revenue:
            if annual_revenue > 50000000:  # 5 Cr+
                score += 15
            elif annual_revenue > 10000000:  # 1 Cr+
                score += 10
            else:
                score += 5
        
        # Determine risk level
        if score >= 70:
            risk_level = "Critical"
        elif score >= 50:
            risk_level = "High"
        elif score >= 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        risk_score = min(score, 100)
        
        return {
            "success": True,
            "risk_assessment": {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "business_type": business_type,
                "industry": industry,
                "identified_risks": risk_concerns,
                "recommendations_count": len(risk_concerns) + 2
            },
            "message": f"Risk assessment completed. Your business has a {risk_level} risk profile with a score of {risk_score}/100."
        }
        
    except Exception as e:
        print(f"❌ Risk assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit risk assessment: {str(e)}")

@app.get("/insurance/recommendations")
async def get_insurance_recommendations(
    business_type: Optional[str] = None,
    risk_level: Optional[str] = None
):
    """Get personalized insurance recommendations"""
    try:
        # Enhanced recommendations with more detailed info
        all_recommendations = [
            {
                "template_id": 1,
                "policy_name": "Professional Indemnity Insurance",
                "policy_type": "professional_indemnity",
                "provider_name": "HDFC ERGO",
                "coverage_description": "Protection against professional errors, omissions, and negligence claims from clients",
                "recommended_coverage": 1000000,
                "estimated_premium": 15000,
                "legal_compliance": True,
                "compliance_authority": "IRDAI",
                "irdai_approval_number": "IRDAI/PI/2024/001",
                "risk_match_score": 95,
                "suitable_for": ["technology", "consulting", "professional_services"],
                "features": {
                    "errors_omissions_cover": True,
                    "legal_defense_costs": True,
                    "retroactive_cover": False,
                    "worldwide_jurisdiction": False
                },
                "optional_addons": {
                    "cyber_liability_extension": 5000,
                    "contract_indemnity": 3000,
                    "fidelity_guarantee": 2000
                },
                "exclusions": ["criminal acts", "bodily injury", "property damage"],
                "key_benefits": [
                    "Covers legal costs up to policy limit",
                    "24/7 claims support hotline",
                    "Pre-approved legal panel"
                ]
            },
            {
                "template_id": 2,
                "policy_name": "Cyber Liability Insurance",
                "policy_type": "cyber_liability",
                "provider_name": "ICICI Lombard",
                "coverage_description": "Comprehensive protection against cyber attacks, data breaches, and digital fraud",
                "recommended_coverage": 2000000,
                "estimated_premium": 25000,
                "legal_compliance": True,
                "compliance_authority": "IRDAI",
                "irdai_approval_number": "IRDAI/CY/2024/002",
                "risk_match_score": 90,
                "suitable_for": ["technology", "e-commerce", "digital", "financial_services"],
                "features": {
                    "data_breach_response": True,
                    "cyber_extortion_cover": True,
                    "business_interruption": True,
                    "forensic_investigation": True
                },
                "optional_addons": {
                    "social_engineering_fraud": 8000,
                    "regulatory_fines": 10000,
                    "reputation_management": 15000
                },
                "exclusions": ["war and terrorism", "prior known breaches", "unencrypted data"],
                "key_benefits": [
                    "Incident response team available 24/7",
                    "Coverage for regulatory fines",
                    "Business interruption compensation"
                ]
            },
            {
                "template_id": 3,
                "policy_name": "Public Liability Insurance",
                "policy_type": "public_liability",
                "provider_name": "New India Assurance",
                "coverage_description": "Coverage for third-party bodily injury and property damage claims",
                "recommended_coverage": 500000,
                "estimated_premium": 12000,
                "legal_compliance": True,
                "compliance_authority": "IRDAI",
                "irdai_approval_number": "IRDAI/PL/2024/003",
                "risk_match_score": 85,
                "suitable_for": ["retail", "manufacturing", "hospitality", "services"],
                "features": {
                    "third_party_injury": True,
                    "property_damage_cover": True,
                    "legal_expenses": True,
                    "products_liability": False
                },
                "optional_addons": {
                    "products_liability_extension": 6000,
                    "contractual_liability": 4000,
                    "cross_liability": 3000
                },
                "exclusions": ["employee injuries", "professional indemnity", "motor accidents"],
                "key_benefits": [
                    "Unlimited legal representation",
                    "Emergency legal advice helpline",
                    "Automatic coverage for new locations"
                ]
            },
            {
                "template_id": 4,
                "policy_name": "Employee Health Insurance",
                "policy_type": "health",
                "provider_name": "Star Health",
                "coverage_description": "Comprehensive health coverage for employees and their families",
                "recommended_coverage": 500000,
                "estimated_premium": 8000,
                "legal_compliance": True,
                "compliance_authority": "IRDAI",
                "irdai_approval_number": "IRDAI/HI/2024/006",
                "risk_match_score": 80,
                "suitable_for": ["all_business_types"],
                "features": {
                    "cashless_treatment": True,
                    "pre_existing_diseases": True,
                    "maternity_cover": True,
                    "dental_vision_cover": False
                },
                "optional_addons": {
                    "critical_illness_cover": 12000,
                    "outpatient_treatment": 8000,
                    "wellness_programs": 5000
                },
                "exclusions": ["cosmetic surgery", "experimental treatments", "war injuries"],
                "key_benefits": [
                    "Nationwide cashless network",
                    "Annual health check-ups",
                    "Mental health support"
                ]
            },
            {
                "template_id": 5,
                "policy_name": "Directors & Officers Insurance",
                "policy_type": "directors_officers",
                "provider_name": "Tata AIG",
                "coverage_description": "Protection for company directors and officers against management liability claims",
                "recommended_coverage": 5000000,
                "estimated_premium": 35000,
                "legal_compliance": True,
                "compliance_authority": "IRDAI",
                "irdai_approval_number": "IRDAI/DO/2024/005",
                "risk_match_score": 75,
                "suitable_for": ["technology", "finance", "manufacturing", "healthcare"],
                "features": {
                    "management_liability": True,
                    "legal_costs_cover": True,
                    "regulatory_investigations": True,
                    "entity_coverage": True
                },
                "optional_addons": {
                    "employment_practices": 18000,
                    "fiduciary_liability": 15000,
                    "crime_coverage": 12000
                },
                "exclusions": ["criminal acts", "personal profit", "prior claims"],
                "key_benefits": [
                    "Side A, B, and C coverage",
                    "Run-off coverage available",
                    "Advancement of defense costs"
                ]
            },
            {
                "template_id": 6,
                "policy_name": "Fire & Asset Protection Insurance",
                "policy_type": "asset_protection",
                "provider_name": "Oriental Insurance",
                "coverage_description": "Protection against fire, theft, and burglary of business assets and inventory",
                "recommended_coverage": 1500000,
                "estimated_premium": 10000,
                "legal_compliance": True,
                "compliance_authority": "IRDAI",
                "irdai_approval_number": "IRDAI/FT/2024/007",
                "risk_match_score": 88,
                "suitable_for": ["retail", "manufacturing", "warehousing"],
                "features": {
                    "fire_damage_cover": True,
                    "theft_burglary_cover": True,
                    "vandalism_cover": True,
                    "business_interruption": False
                },
                "optional_addons": {
                    "business_interruption": 15000,
                    "machinery_breakdown": 8000,
                    "transit_coverage": 6000
                },
                "exclusions": ["natural disasters", "terrorism", "nuclear risks"],
                "key_benefits": [
                    "Replacement cost coverage",
                    "Emergency repairs covered",
                    "Loss of rent compensation"
                ]
            }
        ]
        
        # Filter recommendations based on business type if provided
        if business_type:
            recommendations = [r for r in all_recommendations 
                            if business_type in r["suitable_for"] or "all_business_types" in r["suitable_for"]]
        else:
            recommendations = all_recommendations
        
        # Adjust recommendations based on risk level
        if risk_level:
            for rec in recommendations:
                if risk_level == "Critical":
                    rec["recommended_coverage"] *= 1.5
                    rec["estimated_premium"] *= 1.4
                elif risk_level == "High":
                    rec["recommended_coverage"] *= 1.3
                    rec["estimated_premium"] *= 1.2
                elif risk_level == "Low":
                    rec["recommended_coverage"] *= 0.8
                    rec["estimated_premium"] *= 0.9
        
        return {
            "success": True,
            "recommendations": recommendations[:6],  # Limit to top 6
            "total_available": len(all_recommendations),
            "message": "IRDAI-approved insurance recommendations tailored for MSMEs"
        }
        
    except Exception as e:
        print(f"❌ Get recommendations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@app.post("/insurance/policies")
async def add_insurance_policy(
    policy_name: str,
    policy_type: str,
    provider_name: str,
    coverage_amount: float,
    premium_amount: float,
    policy_number: Optional[str] = None,
    start_date: str = None,
    expiry_date: str = None,
    current_user: str = Depends(get_current_user)
):
    """Add a new insurance policy to user's portfolio"""
    try:
        # For demo, store in mock format since database tables may not exist
        policy_data = {
            "policy_id": f"POL_{current_user}_{len(policy_name)}",
            "user_id": current_user,
            "policy_name": policy_name,
            "policy_type": policy_type,
            "provider_name": provider_name,
            "coverage_amount": coverage_amount,
            "premium_amount": premium_amount,
            "policy_number": policy_number or f"POL-{current_user}-{policy_type.upper()[:3]}",
            "start_date": start_date or datetime.now().strftime("%Y-%m-%d"),
            "expiry_date": expiry_date or (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        try:
            # Try to insert into database if tables exist
            result = supabase.table('insurance_policies').insert(policy_data).execute()
            if result.data:
                return {
                    "success": True,
                    "policy_id": result.data[0].get('policy_id', policy_data['policy_id']),
                    "message": "Insurance policy added successfully to your portfolio"
                }
        except Exception:
            # Database table doesn't exist, return mock success
            pass
        
        return {
            "success": True,
            "policy_id": policy_data['policy_id'],
            "message": "Insurance policy added successfully (demo mode - setup database for persistence)",
            "policy_data": policy_data
        }
        
    except Exception as e:
        print(f"❌ Add policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add policy: {str(e)}")

@app.get("/insurance/policies")
async def get_user_policies(current_user: str = Depends(get_current_user)):
    """Get all insurance policies for the current user"""
    try:
        try:
            # Try to get from database first
            result = supabase.table('insurance_policies')\
                .select('*')\
                .eq('user_id', current_user)\
                .order('created_at', desc=True)\
                .execute()
            
            if result.data:
                policies = result.data
                # Add days until expiry for each policy
                for policy in policies:
                    if policy.get('expiry_date'):
                        expiry_date = datetime.fromisoformat(policy['expiry_date']).date()
                        days_until_expiry = (expiry_date - date.today()).days
                        policy['days_until_expiry'] = days_until_expiry
                        
                        if days_until_expiry <= 30:
                            policy['renewal_status'] = 'urgent'
                        elif days_until_expiry <= 60:
                            policy['renewal_status'] = 'warning'
                        else:
                            policy['renewal_status'] = 'normal'
                
                return {
                    "success": True,
                    "policies": policies,
                    "total_policies": len(policies),
                    "active_policies": len([p for p in policies if p.get('status') == 'active']),
                    "expiring_soon": len([p for p in policies if p.get('days_until_expiry', 999) <= 30])
                }
        except Exception:
            # Database table doesn't exist, return sample policies
            pass
        
        # Return sample policies for demonstration
        sample_policies = [
            {
                "policy_id": f"POL_{current_user}_001",
                "user_id": current_user,
                "policy_name": "Professional Indemnity Insurance",
                "policy_type": "professional_indemnity",
                "provider_name": "HDFC ERGO",
                "coverage_amount": 1000000,
                "premium_amount": 15000,
                "policy_number": "HDFC-PI-2024-001",
                "start_date": "2024-01-15",
                "expiry_date": "2025-01-15",
                "status": "active",
                "days_until_expiry": 150,
                "renewal_status": "normal",
                "document_filename": "professional_indemnity_policy.pdf",
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "policy_id": f"POL_{current_user}_002",
                "user_id": current_user,
                "policy_name": "Cyber Liability Insurance",
                "policy_type": "cyber_liability",
                "provider_name": "ICICI Lombard",
                "coverage_amount": 2000000,
                "premium_amount": 25000,
                "policy_number": "ICICI-CY-2024-002",
                "start_date": "2024-02-01",
                "expiry_date": "2025-02-01",
                "status": "active",
                "days_until_expiry": 167,
                "renewal_status": "normal",
                "document_filename": "cyber_liability_policy.pdf",
                "created_at": "2024-02-01T14:20:00Z"
            },
            {
                "policy_id": f"POL_{current_user}_003",
                "user_id": current_user,
                "policy_name": "Public Liability Insurance",
                "policy_type": "public_liability",
                "provider_name": "New India Assurance",
                "coverage_amount": 500000,
                "premium_amount": 12000,
                "policy_number": "NIA-PL-2024-003",
                "start_date": "2024-08-01",
                "expiry_date": "2024-12-01",
                "status": "active",
                "days_until_expiry": 15,
                "renewal_status": "urgent",
                "document_filename": "public_liability_policy.pdf",
                "created_at": "2024-08-01T09:15:00Z"
            }
        ]
        
        return {
            "success": True,
            "policies": sample_policies,
            "total_policies": len(sample_policies),
            "active_policies": len([p for p in sample_policies if p['status'] == 'active']),
            "expiring_soon": len([p for p in sample_policies if p['days_until_expiry'] <= 30]),
            "message": "Sample policies shown (setup database for real data)"
        }
        
    except Exception as e:
        print(f"❌ Get policies error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get policies: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Nexora Credit Score API with Supabase Database...")
    uvicorn.run("combined_api:app", host="0.0.0.0", port=8001, reload=True)
