"""
Enhanced Insurance Hub API for MSMEs
Provides comprehensive insurance discovery, comparison, and management functionality
with IRDAI compliance and legal validation
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json

# Import the existing dependencies
from combined_api import supabase, get_current_user

router = APIRouter(prefix="/insurance", tags=["Insurance Hub"])

class BusinessRiskAssessment(BaseModel):
    business_type: str  # 'manufacturing', 'services', 'retail', 'digital', 'e-commerce'
    industry: str
    employee_count: int
    annual_revenue: Optional[float] = None
    assets: Dict[str, float]  # {'machinery': 500000, 'inventory': 200000, 'digital_infrastructure': 100000}
    risk_concerns: List[str]  # ['theft', 'cyber_fraud', 'fire', 'employee_welfare', 'liability']
    has_existing_insurance: bool = False
    existing_policies: List[str] = []
    location_country: str = "India"
    location_state: Optional[str] = None

class InsuranceRecommendation(BaseModel):
    template_id: int
    policy_name: str
    policy_type: str
    provider_name: str
    coverage_description: str
    recommended_coverage: float
    estimated_premium: float
    legal_compliance: bool
    compliance_authority: str
    irdai_approval_number: Optional[str]
    risk_match_score: int
    features: Dict[str, Any]
    optional_addons: Optional[Dict[str, Any]] = None

class PolicyManagement(BaseModel):
    policy_name: str
    policy_type: str
    provider_name: str
    coverage_amount: float
    premium_amount: float
    policy_number: Optional[str]
    start_date: date
    expiry_date: date
    document_filename: Optional[str] = None

def calculate_risk_score(assessment: BusinessRiskAssessment) -> tuple[int, str]:
    """Calculate risk score based on business assessment"""
    score = 0
    
    # Business type risk factors
    business_risk = {
        'manufacturing': 25,
        'retail': 15,
        'services': 10,
        'digital': 20,
        'e-commerce': 18
    }
    score += business_risk.get(assessment.business_type, 15)
    
    # Employee count factor
    if assessment.employee_count > 100:
        score += 20
    elif assessment.employee_count > 50:
        score += 15
    elif assessment.employee_count > 10:
        score += 10
    else:
        score += 5
    
    # Asset value factor
    total_assets = sum(assessment.assets.values())
    if total_assets > 10000000:  # 1 Cr+
        score += 25
    elif total_assets > 5000000:  # 50L+
        score += 20
    elif total_assets > 1000000:  # 10L+
        score += 15
    else:
        score += 10
    
    # Risk concerns factor
    score += len(assessment.risk_concerns) * 5
    
    # Annual revenue factor
    if assessment.annual_revenue:
        if assessment.annual_revenue > 50000000:  # 5 Cr+
            score += 15
        elif assessment.annual_revenue > 10000000:  # 1 Cr+
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
    
    return min(score, 100), risk_level

@router.post("/risk-assessment")
async def submit_risk_assessment(
    assessment: BusinessRiskAssessment,
    current_user: str = Depends(get_current_user)
):
    """Submit business risk assessment and get risk score"""
    try:
        # Calculate risk score
        risk_score, risk_level = calculate_risk_score(assessment)
        
        # Get or create business record
        business_result = supabase.table('businesses').select('id').eq('user_id', current_user).execute()
        if not business_result.data:
            # Create business record if it doesn't exist
            business_data = {
                'user_id': int(current_user),
                'business_name': f"Business_{current_user}",
                'business_type': assessment.business_type,
                'industry': assessment.industry,
                'location_country': assessment.location_country,
                'location_state': assessment.location_state or 'Unknown'
            }
            business_result = supabase.table('businesses').insert(business_data).execute()
        
        business_id = business_result.data[0]['id']
        
        # Store risk assessment
        assessment_data = {
            'business_id': business_id,
            'user_id': int(current_user),
            'assessment_data': assessment.dict(),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'identified_risks': assessment.risk_concerns,
            'is_current': True
        }
        
        # Mark previous assessments as not current
        supabase.table('business_risk_assessments').update({'is_current': False}).eq('user_id', current_user).execute()
        
        result = supabase.table('business_risk_assessments').insert(assessment_data).execute()
        
        return {
            "success": True,
            "assessment_id": result.data[0]['assessment_id'],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "identified_risks": assessment.risk_concerns,
            "message": f"Risk assessment completed. Your business has a {risk_level} risk profile with a score of {risk_score}/100."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit risk assessment: {str(e)}")

@router.get("/risk-assessment/{assessment_id}")
async def get_risk_assessment(
    assessment_id: int,
    current_user: str = Depends(get_current_user)
):
    """Get specific risk assessment details"""
    try:
        result = supabase.table('business_risk_assessments')\
            .select('*')\
            .eq('assessment_id', assessment_id)\
            .eq('user_id', current_user)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Risk assessment not found")
        
        return {"success": True, "assessment": result.data[0]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk assessment: {str(e)}")

@router.get("/recommendations")
async def get_insurance_recommendations(
    current_user: str = Depends(get_current_user)
):
    """Get personalized insurance recommendations based on risk assessment"""
    try:
        # Get latest risk assessment
        assessment_result = supabase.table('business_risk_assessments')\
            .select('*')\
            .eq('user_id', current_user)\
            .eq('is_current', True)\
            .order('assessment_date', desc=True)\
            .limit(1)\
            .execute()
        
        if not assessment_result.data:
            # Return default recommendations if no assessment
            templates_result = supabase.table('insurance_templates')\
                .select('*')\
                .eq('is_active', True)\
                .limit(5)\
                .execute()
            
            recommendations = []
            for template in templates_result.data:
                recommendations.append({
                    "template_id": template['template_id'],
                    "policy_name": template['policy_name'],
                    "policy_type": template['policy_type'],
                    "provider_name": template['provider_name'],
                    "coverage_description": template['coverage_description'],
                    "recommended_coverage": template['min_coverage_amount'],
                    "estimated_premium": template['base_premium'],
                    "legal_compliance": template['legal_compliance'],
                    "compliance_authority": template['compliance_authority'],
                    "irdai_approval_number": template.get('irdai_approval_number'),
                    "risk_match_score": 50,  # Default score
                    "features": template.get('features', {}),
                    "optional_addons": template.get('optional_addons', {})
                })
            
            return {
                "success": True,
                "recommendations": recommendations[:5],
                "message": "General recommendations. Complete risk assessment for personalized suggestions."
            }
        
        assessment = assessment_result.data[0]
        business_type = assessment['assessment_data']['business_type']
        risk_concerns = assessment['identified_risks']
        risk_score = assessment['risk_score']
        
        # Get matching templates
        templates_result = supabase.table('insurance_templates')\
            .select('*')\
            .contains('business_types', [business_type])\
            .eq('is_active', True)\
            .execute()
        
        recommendations = []
        for template in templates_result.data:
            # Calculate risk match score
            template_risks = template.get('risk_categories', [])
            risk_match_score = len(set(risk_concerns) & set(template_risks)) * 20
            risk_match_score = min(risk_match_score + 20, 100)  # Base score + matches
            
            # Adjust coverage based on risk score
            base_coverage = template['min_coverage_amount']
            if risk_score >= 70:
                recommended_coverage = template['max_coverage_amount']
                premium_multiplier = 1.5
            elif risk_score >= 50:
                recommended_coverage = (template['min_coverage_amount'] + template['max_coverage_amount']) / 2
                premium_multiplier = 1.2
            else:
                recommended_coverage = template['min_coverage_amount']
                premium_multiplier = 1.0
            
            estimated_premium = template['base_premium'] * premium_multiplier
            
            recommendations.append({
                "template_id": template['template_id'],
                "policy_name": template['policy_name'],
                "policy_type": template['policy_type'],
                "provider_name": template['provider_name'],
                "coverage_description": template['coverage_description'],
                "recommended_coverage": recommended_coverage,
                "estimated_premium": estimated_premium,
                "legal_compliance": template['legal_compliance'],
                "compliance_authority": template['compliance_authority'],
                "irdai_approval_number": template.get('irdai_approval_number'),
                "risk_match_score": risk_match_score,
                "features": template.get('features', {}),
                "optional_addons": template.get('optional_addons', {})
            })
        
        # Sort by risk match score
        recommendations.sort(key=lambda x: x['risk_match_score'], reverse=True)
        
        return {
            "success": True,
            "recommendations": recommendations[:6],
            "risk_profile": {
                "risk_score": risk_score,
                "risk_level": assessment['risk_level'],
                "identified_risks": risk_concerns
            },
            "message": f"Personalized recommendations based on your {assessment['risk_level']} risk profile"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/policies")
async def add_insurance_policy(
    policy: PolicyManagement,
    current_user: str = Depends(get_current_user)
):
    """Add a new insurance policy to track"""
    try:
        # Get business ID
        business_result = supabase.table('businesses').select('id').eq('user_id', current_user).execute()
        if not business_result.data:
            raise HTTPException(status_code=400, detail="Business profile not found. Complete risk assessment first.")
        
        business_id = business_result.data[0]['id']
        
        # Calculate renewal date (30 days before expiry)
        renewal_date = policy.expiry_date - timedelta(days=30)
        
        policy_data = {
            'business_id': business_id,
            'user_id': int(current_user),
            'policy_name': policy.policy_name,
            'policy_type': policy.policy_type,
            'provider_name': policy.provider_name,
            'coverage_amount': policy.coverage_amount,
            'premium_amount': policy.premium_amount,
            'policy_number': policy.policy_number,
            'start_date': policy.start_date.isoformat(),
            'expiry_date': policy.expiry_date.isoformat(),
            'renewal_date': renewal_date.isoformat(),
            'document_filename': policy.document_filename,
            'status': 'active'
        }
        
        result = supabase.table('insurance_policies').insert(policy_data).execute()
        
        # Create renewal reminder
        reminder_data = {
            'policy_id': result.data[0]['policy_id'],
            'user_id': int(current_user),
            'reminder_type': 'renewal',
            'reminder_date': renewal_date.isoformat(),
            'notification_message': f"Policy '{policy.policy_name}' expires on {policy.expiry_date}. Please renew."
        }
        supabase.table('policy_reminders').insert(reminder_data).execute()
        
        return {
            "success": True,
            "policy_id": result.data[0]['policy_id'],
            "message": "Insurance policy added successfully with renewal reminder set"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add policy: {str(e)}")

@router.get("/policies")
async def get_user_policies(current_user: str = Depends(get_current_user)):
    """Get all insurance policies for the current user"""
    try:
        result = supabase.table('insurance_policies')\
            .select('*')\
            .eq('user_id', current_user)\
            .order('created_at', desc=True)\
            .execute()
        
        policies = result.data or []
        
        # Add days until expiry for each policy
        for policy in policies:
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
            "active_policies": len([p for p in policies if p['status'] == 'active']),
            "expiring_soon": len([p for p in policies if p.get('days_until_expiry', 999) <= 30])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get policies: {str(e)}")

@router.put("/policies/{policy_id}")
async def update_policy(
    policy_id: int,
    policy: PolicyManagement,
    current_user: str = Depends(get_current_user)
):
    """Update an existing insurance policy"""
    try:
        # Check if policy belongs to user
        existing = supabase.table('insurance_policies')\
            .select('policy_id')\
            .eq('policy_id', policy_id)\
            .eq('user_id', current_user)\
            .execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Calculate new renewal date
        renewal_date = policy.expiry_date - timedelta(days=30)
        
        update_data = {
            'policy_name': policy.policy_name,
            'policy_type': policy.policy_type,
            'provider_name': policy.provider_name,
            'coverage_amount': policy.coverage_amount,
            'premium_amount': policy.premium_amount,
            'policy_number': policy.policy_number,
            'start_date': policy.start_date.isoformat(),
            'expiry_date': policy.expiry_date.isoformat(),
            'renewal_date': renewal_date.isoformat(),
            'document_filename': policy.document_filename
        }
        
        result = supabase.table('insurance_policies')\
            .update(update_data)\
            .eq('policy_id', policy_id)\
            .execute()
        
        # Update renewal reminder
        supabase.table('policy_reminders')\
            .update({
                'reminder_date': renewal_date.isoformat(),
                'notification_sent': False,
                'notification_message': f"Policy '{policy.policy_name}' expires on {policy.expiry_date}. Please renew."
            })\
            .eq('policy_id', policy_id)\
            .execute()
        
        return {"success": True, "message": "Policy updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update policy: {str(e)}")

@router.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: int,
    current_user: str = Depends(get_current_user)
):
    """Delete an insurance policy"""
    try:
        # Check if policy belongs to user
        existing = supabase.table('insurance_policies')\
            .select('policy_id')\
            .eq('policy_id', policy_id)\
            .eq('user_id', current_user)\
            .execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Delete policy and associated reminders
        supabase.table('policy_reminders').delete().eq('policy_id', policy_id).execute()
        supabase.table('insurance_policies').delete().eq('policy_id', policy_id).execute()
        
        return {"success": True, "message": "Policy deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete policy: {str(e)}")

@router.get("/reminders")
async def get_renewal_reminders(current_user: str = Depends(get_current_user)):
    """Get upcoming renewal reminders"""
    try:
        # Get reminders for next 90 days
        ninety_days_from_now = (date.today() + timedelta(days=90)).isoformat()
        
        result = supabase.table('policy_reminders')\
            .select('*, insurance_policies(policy_name, provider_name, expiry_date)')\
            .eq('user_id', current_user)\
            .lte('reminder_date', ninety_days_from_now)\
            .order('reminder_date')\
            .execute()
        
        return {
            "success": True,
            "reminders": result.data,
            "total_reminders": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reminders: {str(e)}")

@router.post("/upload-document/{policy_id}")
async def upload_policy_document(
    policy_id: int,
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload policy document (PDF/scan)"""
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only PDF and image files are allowed")
        
        # Check if policy belongs to user
        existing = supabase.table('insurance_policies')\
            .select('policy_id')\
            .eq('policy_id', policy_id)\
            .eq('user_id', current_user)\
            .execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # In a real implementation, you would:
        # 1. Save file to cloud storage (AWS S3, Supabase Storage, etc.)
        # 2. Get the public URL
        # 3. Update the policy record with document_url
        
        # For now, just save filename
        filename = f"policy_{policy_id}_{file.filename}"
        
        supabase.table('insurance_policies')\
            .update({
                'document_filename': filename,
                'document_url': f"/documents/{filename}"  # Placeholder URL
            })\
            .eq('policy_id', policy_id)\
            .execute()
        
        return {
            "success": True,
            "message": "Document uploaded successfully",
            "filename": filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.get("/compare")
async def compare_policies(
    policy_ids: str,  # Comma-separated policy IDs
    current_user: str = Depends(get_current_user)
):
    """Compare multiple insurance policies side by side"""
    try:
        policy_id_list = [int(id.strip()) for id in policy_ids.split(',')]
        
        if len(policy_id_list) > 4:
            raise HTTPException(status_code=400, detail="Maximum 4 policies can be compared")
        
        # Get policies
        policies = []
        for policy_id in policy_id_list:
            result = supabase.table('insurance_policies')\
                .select('*')\
                .eq('policy_id', policy_id)\
                .eq('user_id', current_user)\
                .execute()
            
            if result.data:
                policies.append(result.data[0])
        
        if not policies:
            raise HTTPException(status_code=404, detail="No policies found for comparison")
        
        return {
            "success": True,
            "comparison": {
                "policies": policies,
                "comparison_date": date.today().isoformat(),
                "total_coverage": sum(p['coverage_amount'] for p in policies),
                "total_premiums": sum(p['premium_amount'] for p in policies)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare policies: {str(e)}")

# Add these endpoints to the main combined_api.py file
