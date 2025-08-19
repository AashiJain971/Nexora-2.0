"""
Insurance Hub API Endpoints
Handles insurance recommendations, policy management, and compliance tracking
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, date
import json

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

# Add these endpoints to your combined_api.py

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
        
    except Exception as e:
        print(f"❌ Risk assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@app.get("/insurance/recommendations/{assessment_id}")
async def get_saved_recommendations(assessment_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get previously saved insurance recommendations"""
    try:
        user_id = verify_token(credentials.credentials)
        
        result = supabase.table('business_risk_assessments')\
            .select('*')\
            .eq('id', assessment_id)\
            .eq('user_id', user_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        return {"success": True, "data": result.data[0]}
        
    except Exception as e:
        print(f"❌ Get recommendations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

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
        
    except Exception as e:
        print(f"❌ Add policy error: {e}")
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
        
    except Exception as e:
        print(f"❌ Get policies error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get policies: {str(e)}")

@app.put("/insurance/policies/{policy_id}")
async def update_insurance_policy(policy_id: int, policy_update: InsurancePolicyUpdate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update an existing insurance policy"""
    try:
        user_id = verify_token(credentials.credentials)
        
        # Filter out None values
        update_data = {k: v for k, v in policy_update.dict().items() if v is not None}
        
        result = supabase.table('insurance_policies')\
            .update(update_data)\
            .eq('id', policy_id)\
            .eq('user_id', user_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return {"success": True, "message": "Policy updated successfully", "policy": result.data[0]}
        
    except Exception as e:
        print(f"❌ Update policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update policy: {str(e)}")

@app.delete("/insurance/policies/{policy_id}")
async def delete_insurance_policy(policy_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete an insurance policy"""
    try:
        user_id = verify_token(credentials.credentials)
        
        result = supabase.table('insurance_policies')\
            .delete()\
            .eq('id', policy_id)\
            .eq('user_id', user_id)\
            .execute()
        
        return {"success": True, "message": "Policy deleted successfully"}
        
    except Exception as e:
        print(f"❌ Delete policy error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete policy: {str(e)}")

@app.get("/insurance/expiring")
async def get_expiring_policies(days: int = 30, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get policies expiring within specified days"""
    try:
        user_id = verify_token(credentials.credentials)
        
        from datetime import datetime, timedelta
        expiry_threshold = (datetime.now() + timedelta(days=days)).date()
        
        result = supabase.table('insurance_policies')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('status', 'active')\
            .lte('expiry_date', expiry_threshold.isoformat())\
            .order('expiry_date')\
            .execute()
        
        return {"success": True, "expiring_policies": result.data, "days": days}
        
    except Exception as e:
        print(f"❌ Get expiring policies error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get expiring policies: {str(e)}")

@app.get("/insurance/templates")
async def get_insurance_templates(business_type: Optional[str] = None, policy_type: Optional[str] = None):
    """Get available insurance templates for recommendations"""
    try:
        query = supabase.table('insurance_templates').select('*')
        
        if business_type:
            query = query.contains('business_types', [business_type])
        
        if policy_type:
            query = query.eq('policy_type', policy_type)
        
        result = query.execute()
        
        return {"success": True, "templates": result.data}
        
    except Exception as e:
        print(f"❌ Get templates error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

# Helper functions
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
        print(f"❌ Get recommendations error: {e}")
        return []

def get_priority_risks(risk_concerns: List[str]) -> List[str]:
    """Get top 3 priority risks based on severity"""
    risk_priorities = {
        'fire': 10, 'cyber': 9, 'liability': 8, 'theft': 7,
        'employee_welfare': 6, 'natural_disasters': 9, 'transport': 5
    }
    
    sorted_risks = sorted(risk_concerns, key=lambda x: risk_priorities.get(x.lower(), 1), reverse=True)
    return sorted_risks[:3]
