#!/usr/bin/env python3
"""
Test the Insurance Hub functionality end-to-end.
"""
import requests
import json

def test_insurance_assessment():
    """Test the insurance assessment endpoint"""
    
    # First, we need to register/login to get a token
    print("🔐 Testing authentication...")
    
    # Register a test user
    register_data = {
        "email": "test@insurance.com",
        "password": "testpassword123",
        "full_name": "Insurance Test User"
    }
    
    try:
        response = requests.post("http://localhost:8001/register", json=register_data)
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            print("✅ User registered successfully")
        else:
            # Try login instead
            login_data = {"email": register_data["email"], "password": register_data["password"]}
            response = requests.post("http://localhost:8001/login", json=login_data)
            if response.status_code == 200:
                auth_data = response.json()
                token = auth_data.get("access_token")
                print("✅ User logged in successfully")
            else:
                print(f"❌ Authentication failed: {response.text}")
                return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test insurance assessment
    print("\n🧪 Testing insurance assessment...")
    
    assessment_data = {
        "business_type": "services",
        "assets": {
            "machinery": 250000,
            "inventory": 150000,
            "equipment": 100000,
            "building": 500000
        },
        "workforce_size": 25,
        "risk_concerns": ["cyber", "professional_liability", "employee_welfare", "fire"],
        "region": "India",
        "annual_revenue": 5000000,
        "preferences": {
            "focus": "employee_welfare",
            "budget_level": "medium"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post("http://localhost:8001/insurance/assess", 
                               json=assessment_data, 
                               headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Insurance assessment successful!")
            print(f"📊 Risk Score: {result.get('risk_score')}/100 ({result.get('risk_level')})")
            print(f"🏢 Business Size: {result.get('business_size')}")
            print(f"💼 Recommendations: {result.get('count')} policies found")
            
            recommendations = result.get('recommendations', [])
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                print(f"\n🛡️ Recommendation {i}: {rec.get('policy_name')}")
                print(f"   Provider: {rec.get('provider_name')}")
                print(f"   Coverage: ₹{rec.get('estimated_coverage_amount'):,}")
                print(f"   Premium: ₹{rec.get('premium_estimate'):,}/year")
                print(f"   Match Score: {rec.get('match_score', 0)}")
                print(f"   Compliance: {rec.get('compliance_badge')}")
                if rec.get('reason'):
                    print(f"   Why: {rec.get('reason')}")
            
            print(f"\n🎉 Insurance Hub is working correctly!")
            print(f"✅ Generated {len(recommendations)} recommendations")
            
            return True
            
        else:
            print(f"❌ Assessment failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Assessment error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Insurance Hub Functionality")
    print("=" * 50)
    success = test_insurance_assessment()
    if success:
        print("\n✅ All tests passed! Insurance Hub is ready to use.")
    else:
        print("\n❌ Tests failed. Check backend logs for details.")
