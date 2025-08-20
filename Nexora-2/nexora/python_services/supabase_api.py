#!/usr/bin/env python3
"""
Supabase-connected API for Nexora Credit Score System
This replaces the in-memory storage with persistent Supabase database storage
"""

import os
import json
import jwt
import bcrypt
import uvicorn
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
import base64
from io import BytesIO
from PIL import Image
import pytesseract
import re

# Import existing credit score functionality
from credit_score import main as calculate_credit_score_main

app = FastAPI(title="Nexora Credit Score API with Supabase")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5001", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = "https://eecbqzvcnwrkcxgwjxlt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVlY2JxenZjbndya2N4Z3dqeGx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0Mjk1NjEsImV4cCI6MjA3MTAwNTU2MX0.CkhFT-6LKFg6NCc9WIiZRjNQ7VGVX6nJmoOxjMVHDKs"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize database tables
def init_database():
    """Initialize database tables if they don't exist"""
    try:
        print("🔧 Initializing database tables...")
        
        # Create users table
        create_users_sql = """
        CREATE TABLE IF NOT EXISTS public.users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create invoices table with credit score columns
        create_invoices_sql = """
        CREATE TABLE IF NOT EXISTS public.invoices (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            invoice_number VARCHAR(255) NOT NULL,
            client VARCHAR(255) NOT NULL,
            date DATE,
            payment_terms VARCHAR(255),
            industry VARCHAR(255),
            total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
            currency VARCHAR(10) DEFAULT 'INR',
            tax_amount DECIMAL(15,2) DEFAULT 0,
            extra_charges DECIMAL(15,2) DEFAULT 0,
            line_items JSONB,
            status VARCHAR(50) DEFAULT 'pending',
            credit_score DECIMAL(5,2) DEFAULT NULL,
            credit_score_data JSONB DEFAULT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            payment_date DATE,
            UNIQUE(invoice_number, user_id)
        );
        """
        
        # Execute via raw SQL using supabase.rpc
        supabase.rpc('exec_sql', {'sql': create_users_sql}).execute()
        supabase.rpc('exec_sql', {'sql': create_invoices_sql}).execute()
        
        print("✅ Database tables initialized successfully!")
        
    except Exception as e:
        print(f"⚠️ Database initialization failed, tables might already exist: {e}")

# Initialize database on startup
init_database()

# JWT configuration
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class FinancialData(BaseModel):
    no_of_invoices: int
    total_amount: float
    total_amount_pending: float
    total_amount_paid: float
    tax: float
    extra_charges: float
    payment_completion_rate: float
    paid_to_pending_ratio: float

class CreditScoreResponse(BaseModel):
    credit_score_analysis: dict
    timestamp: str
    api_model: str

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def extract_invoice_data_from_image(image: Image.Image) -> dict:
    """Extract invoice data using OCR"""
    try:
        # Convert to text
        text = pytesseract.image_to_string(image)
        
        # Extract basic information using regex
        invoice_data = {
            "invoice_number": "INV-" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "client": "Client Name",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "payment_terms": "30 days",
            "industry": "General",
            "total_amount": 1000.0,
            "currency": "INR",
            "tax_amount": 180.0,
            "extra_charges": 0.0,
            "line_items": [{"description": "Service/Product", "amount": 820.0}]
        }
        
        # Try to extract actual amounts from OCR text
        amount_patterns = [
            r'(?:total|amount|sum)[:\s]*(?:₹|rs\.?|inr)[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:₹|rs\.?|inr)[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)[:\s]*(?:₹|rs\.?|inr)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    if 100 <= amount <= 10000000:  # Reasonable range
                        invoice_data["total_amount"] = amount
                        invoice_data["tax_amount"] = round(amount * 0.18, 2)  # 18% GST
                        break
                except ValueError:
                    pass
        
        return invoice_data
    except Exception as e:
        print(f"Error extracting invoice data: {e}")
        # Return default data if OCR fails
        return {
            "invoice_number": "INV-" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "client": "Extracted Client",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "payment_terms": "30 days",
            "industry": "General",
            "total_amount": 1000.0,
            "currency": "INR",
            "tax_amount": 180.0,
            "extra_charges": 0.0,
            "line_items": [{"description": "Extracted Service", "amount": 820.0}]
        }

# API Routes
@app.post("/register")
async def register(user: UserCreate):
    try:
        # Check if user exists
        existing_user = supabase.table('users').select('*').eq('email', user.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        hashed_password = hash_password(user.password)
        new_user = supabase.table('users').insert({
            'email': user.email,
            'full_name': user.full_name,
            'password_hash': hashed_password
        }).execute()
        
        if new_user.data:
            user_data = new_user.data[0]
            access_token = create_access_token(data={"sub": str(user_data['id'])})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_data": {
                    "id": str(user_data['id']),
                    "email": user_data['email'],
                    "full_name": user_data['full_name']
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/login")
async def login(user: UserLogin):
    try:
        # Find user
        user_result = supabase.table('users').select('*').eq('email', user.email).execute()
        if not user_result.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_data = user_result.data[0]
        
        # Verify password
        if not verify_password(user.password, user_data['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user_data['id'])})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_data": {
                "id": str(user_data['id']),
                "email": user_data['email'],
                "full_name": user_data['full_name']
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/user/invoices")
async def get_user_invoices(current_user: str = Depends(get_current_user)):
    try:
        # Get all invoices for the user
        result = supabase.table('invoices').select('*').eq('user_id', current_user).execute()
        return {
            "invoices": result.data or [],
            "total_count": len(result.data) if result.data else 0
        }
    except Exception as e:
        print(f"Error fetching invoices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch invoices")

@app.post("/calculate-credit-score", response_model=CreditScoreResponse)
async def calculate_credit_score_api(financial_data: FinancialData):
    """Calculate weighted credit score based on financial metrics"""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment.")

    try:
        financial_dict = financial_data.model_dump()
        print("📊 Received financial data for credit score calculation:", financial_dict)
        
        result_json = calculate_credit_score_main(financial_dict, GROQ_API_KEY)
        
        if not result_json:
            raise HTTPException(status_code=500, detail="Credit score calculation returned empty result")

        result_dict = json.loads(result_json)
        print("✅ Credit score calculation successful")
        
        return CreditScoreResponse(
            credit_score_analysis=result_dict["credit_score_analysis"],
            timestamp="generated",
            api_model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse credit score analysis")
    except Exception as e:
        print(f"❌ Credit score calculation error: {e}")
        raise HTTPException(status_code=500, detail="Credit score calculation failed")

@app.post("/process-invoice")
async def process_invoice_with_credit_score(image: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    """Process invoice image and calculate credit score, storing both in Supabase"""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in environment.")
    
    try:
        print(f"🔍 Processing invoice for user: {current_user}")
        
        # Read and process image
        image_data = await image.read()
        pil_image = Image.open(BytesIO(image_data))
        
        # Extract invoice data
        invoice_details = extract_invoice_data_from_image(pil_image)
        print(f"📋 Extracted invoice details: {invoice_details}")
        
        # Calculate individual invoice credit score
        single_invoice_data = {
            "no_of_invoices": 1,
            "total_amount": invoice_details["total_amount"],
            "total_amount_pending": invoice_details["total_amount"],  # New invoice is pending
            "total_amount_paid": 0.0,  # New invoice hasn't been paid
            "tax": invoice_details["tax_amount"],
            "extra_charges": invoice_details["extra_charges"],
            "payment_completion_rate": 0.7,  # Default reasonable rate
            "paid_to_pending_ratio": 0.5   # Default reasonable ratio
        }
        
        print("🚀 Calculating individual invoice credit score...")
        single_score_json = calculate_credit_score_main(single_invoice_data, GROQ_API_KEY)
        single_score_data = json.loads(single_score_json) if single_score_json else None
        
        individual_credit_score = single_score_data["credit_score_analysis"]["final_weighted_credit_score"] if single_score_data else 0.0
        
        # Store invoice in Supabase with credit score
        invoice_record = {
            'user_id': int(current_user),
            'invoice_number': invoice_details['invoice_number'],
            'client': invoice_details['client'],
            'date': invoice_details['date'],
            'payment_terms': invoice_details['payment_terms'],
            'industry': invoice_details['industry'],
            'total_amount': float(invoice_details['total_amount']),
            'currency': invoice_details['currency'],
            'tax_amount': float(invoice_details['tax_amount']),
            'extra_charges': float(invoice_details['extra_charges']),
            'line_items': invoice_details['line_items'],
            'status': 'pending',
            'credit_score': float(individual_credit_score),
            'credit_score_data': single_score_data["credit_score_analysis"] if single_score_data else None
        }
        
        print("💾 Saving invoice to Supabase...")
        saved_invoice = supabase.table('invoices').insert(invoice_record).execute()
        
        if not saved_invoice.data:
            raise HTTPException(status_code=500, detail="Failed to save invoice to database")
        
        print("✅ Invoice saved successfully with credit score!")
        
        # Get all user invoices for total credit score calculation
        all_invoices = supabase.table('invoices').select('*').eq('user_id', current_user).execute()
        invoices = all_invoices.data or []
        
        # Calculate total financial data for cumulative credit score
        if len(invoices) > 0:
            total_amount = sum(inv['total_amount'] for inv in invoices)
            total_paid = sum(inv['total_amount'] for inv in invoices if inv['status'] == 'paid')
            total_pending = sum(inv['total_amount'] for inv in invoices if inv['status'] in ['pending', 'processed'])
            total_tax = sum(inv['tax_amount'] for inv in invoices)
            total_extra_charges = sum(inv['extra_charges'] for inv in invoices)
            
            payment_completion_rate = total_paid / total_amount if total_amount > 0 else 0.0
            paid_to_pending_ratio = total_paid / total_pending if total_pending > 0 else 1.0
            
            total_financial_data = {
                "no_of_invoices": len(invoices),
                "total_amount": total_amount,
                "total_amount_pending": total_pending,
                "total_amount_paid": total_paid,
                "tax": total_tax,
                "extra_charges": total_extra_charges,
                "payment_completion_rate": payment_completion_rate,
                "paid_to_pending_ratio": paid_to_pending_ratio
            }
            
            print("🚀 Calculating total cumulative credit score...")
            total_score_json = calculate_credit_score_main(total_financial_data, GROQ_API_KEY)
            total_score_data = json.loads(total_score_json) if total_score_json else None
        else:
            total_score_data = single_score_data
        
        # Prepare response
        response = {
            # Invoice details
            "invoice_number": invoice_details["invoice_number"],
            "client": invoice_details["client"],
            "date": invoice_details["date"],
            "payment_terms": invoice_details["payment_terms"],
            "industry": invoice_details["industry"],
            "total_amount": invoice_details["total_amount"],
            "currency": invoice_details["currency"],
            "tax_amount": invoice_details["tax_amount"],
            "extra_charges": invoice_details["extra_charges"],
            "line_items": invoice_details["line_items"],
            "total_line_items": len(invoice_details["line_items"]),
            # Credit score analysis
            "individual_credit_score_analysis": single_score_data["credit_score_analysis"] if single_score_data else None,
            "total_credit_score_analysis": total_score_data["credit_score_analysis"] if total_score_data else None,
            # Historical context
            "historical_summary": {
                "total_historical_invoices": len(invoices),
                "total_historical_amount": sum(inv['total_amount'] for inv in invoices),
                "average_invoice_amount": sum(inv['total_amount'] for inv in invoices) / len(invoices) if invoices else 0
            }
        }
        
        print("✅ Invoice processing completed successfully!")
        return response
        
    except Exception as e:
        print(f"❌ Invoice processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Invoice processing failed: {str(e)}")

@app.get("/dashboard/credit-score")
async def get_dashboard_credit_score(current_user: str = Depends(get_current_user)):
    """Get dashboard credit score calculated as mean of all invoice credit scores"""
    try:
        print(f"📊 Fetching dashboard credit score for user: {current_user}")
        
        # Get all invoices with credit scores for the user
        result = supabase.table('invoices').select('*').eq('user_id', current_user).execute()
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
            # If no credit scores calculated yet, calculate them
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
        "message": "Nexora Credit Score API with Supabase Database Storage",
        "features": [
            "Supabase database integration",
            "Persistent invoice and credit score storage",
            "Mean-based dashboard credit score calculation",
            "Individual invoice credit score tracking"
        ],
        "endpoints": {
            "register": "/register",
            "login": "/login",
            "user_invoices": "/user/invoices",
            "process_invoice": "/process-invoice",
            "calculate_credit_score": "/calculate-credit-score",
            "dashboard_credit_score": "/dashboard/credit-score"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Nexora API with Supabase integration...")
    print(f"📊 Supabase URL: {SUPABASE_URL}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
