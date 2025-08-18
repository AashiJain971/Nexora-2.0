#!/usr/bin/env python3
"""
Nexora Credit Score API - Supabase Database Only
This version uses only Supabase database, no in-memory storage
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
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://eecbqzvcnwrkcxgwjxlt.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVlY2JxenZjbndya2N4Z3dqeGx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0Mjk1NjEsImV4cCI6MjA3MTAwNTU2MX0.CkhFT-6LKFg6NCc9WIiZRjNQ7VGVX6nJmoOxjMVHDKs")

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
        invoice_result = await asyncio.to_thread(extract_invoice_main, temp_file_path)
        
        if not invoice_result.get("success", False):
            raise HTTPException(status_code=400, detail=f"Invoice extraction failed: {invoice_result.get('error', 'Unknown error')}")
        
        invoice_details = invoice_result["invoice_details"]
        print(f"✅ Invoice extracted: {invoice_details['invoice_number']}")
        
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
            "total_amount_pending": float(invoice_details['total_amount']),  # New invoice is pending
            "total_amount_paid": total_amount - float(invoice_details['total_amount']),
            "tax": float(invoice_details.get('tax_amount', 0)),
            "extra_charges": float(invoice_details.get('extra_charges', 0)),
            "payment_completion_rate": 0.8,  # Default assumption
            "paid_to_pending_ratio": 0.6     # Default assumption
        }
        
        credit_score_result = await asyncio.to_thread(calculate_credit_score_main, credit_score_data)
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
            "currency": invoice_details.get("currency", "INR"),
            "tax_amount": float(invoice_details.get("tax_amount", 0)),
            "extra_charges": float(invoice_details.get("extra_charges", 0)),
            "line_items": invoice_details.get("line_items", []),
            "status": "pending",
            "credit_score": individual_credit_score,
            "credit_score_data": credit_score_result.get('credit_score_analysis', {})
        }
        
        # Insert invoice into database
        print("💾 Saving invoice to Supabase...")
        result = supabase.table("invoices").insert(invoice_db_data).execute()
        
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
        result = await asyncio.to_thread(calculate_credit_score_main, credit_data)
        print("✅ Single invoice credit score calculated")
        return result
    except Exception as e:
        print(f"❌ Single invoice credit score calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Credit score calculation failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Nexora Credit Score API with Supabase Database...")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
