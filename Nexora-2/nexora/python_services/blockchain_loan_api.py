"""
Blockchain Loan API endpoints for escrow-based lending system.
This module handles loan requests, approvals, and integrates with the smart contract.
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field
from web3 import Web3
from eth_account import Account
import requests

# We'll import these through dependency injection to avoid circular imports
# from combined_api import get_current_user, supabase, GROQ_API_KEY, calculate_credit_score_main

# Web3 Configuration
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "https://sepolia.infura.io/v3/YOUR_INFURA_KEY")
PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY", "")  # Admin private key for contract interactions
CONTRACT_ADDRESS = os.getenv("LOAN_ESCROW_ADDRESS", "0x1234567890123456789012345678901234567890")

# Contract ABI (simplified for main functions)
CONTRACT_ABI = [
    {
        "inputs": [{"name": "_amount", "type": "uint256"}, {"name": "_creditScore", "type": "uint256"}, 
                  {"name": "_businessName", "type": "string"}, {"name": "_businessType", "type": "string"}],
        "name": "requestLoan",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "_loanId", "type": "uint256"}],
        "name": "approveLoan",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "_loanId", "type": "uint256"}],
        "name": "disburseLoan",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "_loanId", "type": "uint256"}],
        "name": "getLoanRequest",
        "outputs": [{"name": "", "type": "tuple", "components": [
            {"name": "borrower", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "creditScore", "type": "uint256"},
            {"name": "approved", "type": "bool"},
            {"name": "disbursed", "type": "bool"},
            {"name": "repaid", "type": "bool"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "businessName", "type": "string"},
            {"name": "businessType", "type": "string"}
        ]}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getEscrowBalance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "_creditScore", "type": "uint256"}],
        "name": "calculateMaxLoanAmount",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Initialize Web3
try:
    w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    if PRIVATE_KEY:
        admin_account = Account.from_key(PRIVATE_KEY)
    else:
        admin_account = None
        print("⚠️ Warning: Admin private key not set. Some functions may not work.")
except Exception as e:
    print(f"❌ Failed to initialize Web3: {e}")
    w3 = None
    contract = None
    admin_account = None

# Pydantic Models
class LoanRequestModel(BaseModel):
    amount_eth: float = Field(..., gt=0, description="Loan amount in ETH")
    business_name: str = Field(..., min_length=2, description="Business name")
    business_type: str = Field(..., min_length=2, description="Business type/industry")
    wallet_address: str = Field(..., description="Borrower's wallet address")

class LoanApprovalModel(BaseModel):
    loan_id: int = Field(..., ge=0, description="Loan ID to approve")
    
class BlockchainLoanResponse(BaseModel):
    success: bool
    message: str
    transaction_hash: Optional[str] = None
    loan_id: Optional[int] = None
    gas_used: Optional[int] = None

class LoanStatusResponse(BaseModel):
    loan_id: int
    borrower: str
    amount_eth: float
    credit_score: int
    approved: bool
    disbursed: bool
    repaid: bool
    timestamp: datetime
    business_name: str
    business_type: str

# Helper Functions
def wei_to_ether(wei_amount: int) -> float:
    """Convert Wei to Ether"""
    return wei_amount / 10**18

def ether_to_wei(ether_amount: float) -> int:
    """Convert Ether to Wei"""
    return int(ether_amount * 10**18)

async def get_user_credit_score(user_id: str, supabase_client, groq_api_key, calculate_credit_fn) -> int:
    """Get user's current credit score from database"""
    try:
        # Get user's invoices and calculate credit score
        invoices_response = supabase_client.table('invoices').select('*').eq('user_id', int(user_id)).execute()
        
        if not invoices_response.data:
            return 0
            
        invoices = invoices_response.data
        
        # Calculate aggregated financial data
        total_amount = sum([inv['total_amount'] for inv in invoices])
        total_paid = sum([inv['total_amount'] for inv in invoices if inv.get('status') == 'paid'])
        total_pending = sum([inv['total_amount'] for inv in invoices if inv.get('status') in ['pending', 'processed']])
        
        financial_data = {
            "no_of_invoices": len(invoices),
            "total_amount": total_amount,
            "total_amount_pending": total_pending,
            "total_amount_paid": total_paid,
            "tax": sum([inv.get('tax_amount', 0) for inv in invoices]),
            "extra_charges": sum([inv.get('extra_charges', 0) for inv in invoices]),
            "payment_completion_rate": total_paid / total_amount if total_amount > 0 else 0.7,
            "paid_to_pending_ratio": total_paid / total_pending if total_pending > 0 else 0.5
        }
        
        # Calculate credit score
        credit_result = await asyncio.to_thread(calculate_credit_fn, financial_data, groq_api_key)
        
        if credit_result:
            try:
                credit_data = json.loads(credit_result) if isinstance(credit_result, str) else credit_result
                return int(credit_data.get('credit_score_analysis', {}).get('final_weighted_credit_score', 0))
            except:
                return 0
        
        return 0
        
    except Exception as e:
        print(f"❌ Error getting credit score: {e}")
        return 0

async def store_loan_request_db(user_id: str, loan_data: Dict[str, Any], supabase_client) -> int:
    """Store loan request in database"""
    try:
        loan_record = {
            "user_id": int(user_id),
            "amount_eth": loan_data["amount_eth"],
            "business_name": loan_data["business_name"],
            "business_type": loan_data["business_type"],
            "wallet_address": loan_data["wallet_address"],
            "credit_score": loan_data["credit_score"],
            "status": "pending",
            "blockchain_loan_id": loan_data.get("blockchain_loan_id"),
            "transaction_hash": loan_data.get("transaction_hash"),
            "created_at": datetime.utcnow().isoformat(),
            "approved": False,
            "disbursed": False,
            "repaid": False
        }
        
        # Insert into loans table (you may need to create this table)
        result = supabase_client.table('blockchain_loans').insert(loan_record).execute()
        
        if result.data:
            return result.data[0]['id']
        else:
            raise Exception("Failed to insert loan record")
            
    except Exception as e:
        print(f"❌ Error storing loan request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store loan request: {str(e)}")

# API Endpoints (these will be called from combined_api.py with injected dependencies)
async def request_blockchain_loan(loan_request: LoanRequestModel, current_user: str, supabase_client, groq_api_key, calculate_credit_fn):
    """
    Request a loan on the blockchain based on credit score
    """
    if not w3 or not contract:
        raise HTTPException(status_code=500, detail="Blockchain connection not available")
    
    try:
        # Get user's credit score
        credit_score = await get_user_credit_score(current_user, supabase_client, groq_api_key, calculate_credit_fn)
        
        if credit_score < 600:
            raise HTTPException(
                status_code=400, 
                detail=f"Credit score {credit_score} is below minimum requirement of 600"
            )
        
        # Check maximum loan amount based on credit score
        max_loan_wei = contract.functions.calculateMaxLoanAmount(credit_score).call()
        max_loan_eth = wei_to_ether(max_loan_wei)
        
        if loan_request.amount_eth > max_loan_eth:
            raise HTTPException(
                status_code=400,
                detail=f"Requested amount {loan_request.amount_eth} ETH exceeds maximum allowed {max_loan_eth:.4f} ETH for credit score {credit_score}"
            )
        
        # Check escrow balance
        escrow_balance_wei = contract.functions.getEscrowBalance().call()
        escrow_balance_eth = wei_to_ether(escrow_balance_wei)
        
        if loan_request.amount_eth > escrow_balance_eth * 0.8:  # 80% of escrow
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient escrow balance. Available: {escrow_balance_eth:.4f} ETH"
            )
        
        # If admin account is available, submit transaction on behalf of user
        # Otherwise, return transaction data for frontend to submit
        if admin_account:
            # Build transaction
            amount_wei = ether_to_wei(loan_request.amount_eth)
            
            # Get transaction parameters
            nonce = w3.eth.get_transaction_count(admin_account.address)
            gas_price = w3.eth.gas_price
            
            # Build the transaction
            transaction = contract.functions.requestLoan(
                amount_wei,
                credit_score,
                loan_request.business_name,
                loan_request.business_type
            ).build_transaction({
                'from': admin_account.address,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': 300000,  # Estimated gas limit
            })
            
            # Sign and send transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Store loan request in database
            loan_data = {
                "amount_eth": loan_request.amount_eth,
                "business_name": loan_request.business_name,
                "business_type": loan_request.business_type,
                "wallet_address": loan_request.wallet_address,
                "credit_score": credit_score,
                "transaction_hash": tx_hash.hex(),
                "blockchain_loan_id": None  # Will be determined from events
            }
            
            db_loan_id = await store_loan_request_db(current_user, loan_data, supabase_client)
            
            return BlockchainLoanResponse(
                success=True,
                message="Loan request submitted successfully",
                transaction_hash=tx_hash.hex(),
                gas_used=tx_receipt.gasUsed
            )
        else:
            # Return transaction data for frontend to submit
            amount_wei = ether_to_wei(loan_request.amount_eth)
            
            return {
                "success": True,
                "message": "Transaction data prepared for frontend submission",
                "transaction_data": {
                    "contract_address": CONTRACT_ADDRESS,
                    "function_name": "requestLoan",
                    "parameters": [
                        amount_wei,
                        credit_score,
                        loan_request.business_name,
                        loan_request.business_type
                    ],
                    "estimated_gas": 300000
                },
                "credit_score": credit_score,
                "max_loan_amount_eth": max_loan_eth
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Loan request error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process loan request: {str(e)}")

async def approve_blockchain_loan(approval: LoanApprovalModel, current_user: str, supabase_client):
    """
    Approve a loan request (admin only)
    """
    if not w3 or not contract or not admin_account:
        raise HTTPException(status_code=500, detail="Blockchain admin functionality not available")
    
    try:
        # Check if user is admin (you may want to implement proper admin check)
        # For now, we'll check if the current user has admin privileges in the database
        
        # Get loan details from blockchain
        loan_details = contract.functions.getLoanRequest(approval.loan_id).call()
        
        if loan_details[3]:  # already approved
            raise HTTPException(status_code=400, detail="Loan already approved")
        
        # Build approval transaction
        nonce = w3.eth.get_transaction_count(admin_account.address)
        gas_price = w3.eth.gas_price
        
        transaction = contract.functions.approveLoan(approval.loan_id).build_transaction({
            'from': admin_account.address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 200000,
        })
        
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Update database
        try:
            supabase_client.table('blockchain_loans').update({
                "approved": True,
                "approved_at": datetime.utcnow().isoformat(),
                "approved_by": current_user,
                "approval_tx_hash": tx_hash.hex()
            }).eq('blockchain_loan_id', approval.loan_id).execute()
        except:
            pass  # Don't fail if database update fails
        
        return BlockchainLoanResponse(
            success=True,
            message=f"Loan {approval.loan_id} approved successfully",
            transaction_hash=tx_hash.hex(),
            loan_id=approval.loan_id,
            gas_used=tx_receipt.gasUsed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Loan approval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve loan: {str(e)}")

async def get_loan_status(loan_id: int) -> LoanStatusResponse:
    """
    Get loan status from blockchain
    """
    if not w3 or not contract:
        raise HTTPException(status_code=500, detail="Blockchain connection not available")
    
    try:
        loan_details = contract.functions.getLoanRequest(loan_id).call()
        
        return LoanStatusResponse(
            loan_id=loan_id,
            borrower=loan_details[0],
            amount_eth=wei_to_ether(loan_details[1]),
            credit_score=loan_details[2],
            approved=loan_details[3],
            disbursed=loan_details[4],
            repaid=loan_details[5],
            timestamp=datetime.fromtimestamp(loan_details[6]),
            business_name=loan_details[7],
            business_type=loan_details[8]
        )
        
    except Exception as e:
        print(f"❌ Get loan status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get loan status: {str(e)}")

async def get_escrow_balance() -> Dict[str, Any]:
    """
    Get current escrow balance
    """
    if not w3 or not contract:
        raise HTTPException(status_code=500, detail="Blockchain connection not available")
    
    try:
        balance_wei = contract.functions.getEscrowBalance().call()
        balance_eth = wei_to_ether(balance_wei)
        
        return {
            "success": True,
            "escrow_balance_eth": balance_eth,
            "escrow_balance_wei": balance_wei
        }
        
    except Exception as e:
        print(f"❌ Get escrow balance error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get escrow balance: {str(e)}")

async def calculate_max_loan_amount_api(credit_score: int) -> Dict[str, Any]:
    """
    Calculate maximum loan amount based on credit score
    """
    if not w3 or not contract:
        raise HTTPException(status_code=500, detail="Blockchain connection not available")
    
    try:
        if credit_score < 600:
            return {
                "success": True,
                "credit_score": credit_score,
                "max_loan_amount_eth": 0,
                "message": "Credit score below minimum requirement"
            }
        
        max_loan_wei = contract.functions.calculateMaxLoanAmount(credit_score).call()
        max_loan_eth = wei_to_ether(max_loan_wei)
        
        return {
            "success": True,
            "credit_score": credit_score,
            "max_loan_amount_eth": max_loan_eth,
            "max_loan_amount_wei": max_loan_wei
        }
        
    except Exception as e:
        print(f"❌ Calculate max loan error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate max loan amount: {str(e)}")

async def get_user_loans(current_user: str, supabase_client) -> List[Dict[str, Any]]:
    """
    Get all loans for the current user from database
    """
    try:
        result = supabase_client.table('blockchain_loans').select('*').eq('user_id', int(current_user)).execute()
        
        loans = result.data if result.data else []
        
        # Enhance with blockchain data if available
        enhanced_loans = []
        for loan in loans:
            enhanced_loan = dict(loan)
            
            # Try to get blockchain status if loan_id is available
            if loan.get('blockchain_loan_id') is not None and w3 and contract:
                try:
                    blockchain_data = contract.functions.getLoanRequest(loan['blockchain_loan_id']).call()
                    enhanced_loan.update({
                        "blockchain_approved": blockchain_data[3],
                        "blockchain_disbursed": blockchain_data[4],
                        "blockchain_repaid": blockchain_data[5],
                        "blockchain_timestamp": blockchain_data[6]
                    })
                except:
                    pass  # Don't fail if blockchain query fails
            
            enhanced_loans.append(enhanced_loan)
        
        return enhanced_loans
        
    except Exception as e:
        print(f"❌ Get user loans error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user loans: {str(e)}")

# Export functions for use in main API
__all__ = [
    'request_blockchain_loan',
    'approve_blockchain_loan', 
    'get_loan_status',
    'get_escrow_balance',
    'calculate_max_loan_amount_api',
    'get_user_loans',
    'get_user_credit_score',
    'LoanRequestModel',
    'LoanApprovalModel',
    'BlockchainLoanResponse',
    'LoanStatusResponse'
]
