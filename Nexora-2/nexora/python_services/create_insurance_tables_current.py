#!/usr/bin/env python3
"""
Create insurance tables in the current Supabase instance
This script will create the required tables for the Insurance Hub feature
"""

import os
import sys
from supabase import create_client

def get_supabase_client():
    """Get the Supabase client with the same credentials as the main app"""
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yhfdwzizydowbiphdgap.supabase.co")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InloZmR3eml6eWRvd2JpcGhkZ2FwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzc1OTA5OSwiZXhwIjoyMDQ5MzM1MDk5fQ.f-X9kSWagBKVHQBAiJ2yV7uRnkkW4sDIlbIqe1OUo6w")
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def main():
    print("🔧 Creating insurance tables in current Supabase instance...")
    
    try:
        supabase = get_supabase_client()
        
        # Test connection
        test_result = supabase.table('users').select('id').limit(1).execute()
        print("✅ Connected to Supabase successfully")
        
        # Insurance templates data to insert
        templates = [
            {
                'policy_name': 'Professional Indemnity Insurance',
                'policy_type': 'professional_indemnity',
                'provider_name': 'HDFC ERGO',
                'business_types': ['services', 'consulting', 'digital'],
                'target_industries': ['technology', 'consulting', 'professional_services'],
                'min_coverage_amount': 500000.00,
                'max_coverage_amount': 10000000.00,
                'base_premium': 15000.00,
                'coverage_description': 'Protection against professional errors, omissions, and negligence claims',
                'legal_compliance': True,
                'compliance_authority': 'IRDAI',
                'irdai_approval_number': 'IRDAI/PI/2024/001',
                'risk_categories': ['professional_liability', 'errors_omissions'],
                'features': {"errors_omissions": True, "legal_costs": True, "defense_costs": True},
                'is_active': True
            },
            {
                'policy_name': 'Cyber Liability Insurance',
                'policy_type': 'cyber_liability',
                'provider_name': 'ICICI Lombard',
                'business_types': ['digital', 'e-commerce', 'services'],
                'target_industries': ['technology', 'finance', 'healthcare'],
                'min_coverage_amount': 1000000.00,
                'max_coverage_amount': 50000000.00,
                'base_premium': 25000.00,
                'coverage_description': 'Comprehensive protection against cyber attacks, data breaches, and digital fraud',
                'legal_compliance': True,
                'compliance_authority': 'IRDAI',
                'irdai_approval_number': 'IRDAI/CY/2024/002',
                'risk_categories': ['cyber', 'data_breach', 'digital_fraud'],
                'features': {"data_breach": True, "cyber_extortion": True, "business_interruption": True},
                'is_active': True
            },
            {
                'policy_name': 'Public Liability Insurance',
                'policy_type': 'public_liability',
                'provider_name': 'New India Assurance',
                'business_types': ['retail', 'manufacturing', 'services'],
                'target_industries': ['retail', 'hospitality', 'manufacturing'],
                'min_coverage_amount': 200000.00,
                'max_coverage_amount': 5000000.00,
                'base_premium': 12000.00,
                'coverage_description': 'Coverage for third-party bodily injury and property damage claims',
                'legal_compliance': True,
                'compliance_authority': 'IRDAI',
                'irdai_approval_number': 'IRDAI/PL/2024/003',
                'risk_categories': ['liability', 'third_party_injury', 'property_damage'],
                'features': {"third_party_injury": True, "property_damage": True, "legal_expenses": True},
                'is_active': True
            },
            {
                'policy_name': 'Employee Health Insurance',
                'policy_type': 'health',
                'provider_name': 'Star Health',
                'business_types': ['services', 'manufacturing', 'retail', 'digital'],
                'target_industries': ['all'],
                'min_coverage_amount': 100000.00,
                'max_coverage_amount': 2000000.00,
                'base_premium': 8000.00,
                'coverage_description': 'Comprehensive health coverage for employees and their families',
                'legal_compliance': True,
                'compliance_authority': 'IRDAI',
                'irdai_approval_number': 'IRDAI/HI/2024/006',
                'risk_categories': ['employee_welfare', 'medical_emergencies'],
                'features': {"cashless_treatment": True, "pre_existing_diseases": True, "maternity_cover": True},
                'is_active': True
            },
            {
                'policy_name': 'Fire & Theft Insurance',
                'policy_type': 'asset_protection',
                'provider_name': 'Oriental Insurance',
                'business_types': ['retail', 'manufacturing'],
                'target_industries': ['retail', 'manufacturing', 'warehousing'],
                'min_coverage_amount': 300000.00,
                'max_coverage_amount': 15000000.00,
                'base_premium': 10000.00,
                'coverage_description': 'Protection against fire, theft, and burglary of business assets',
                'legal_compliance': True,
                'compliance_authority': 'IRDAI',
                'irdai_approval_number': 'IRDAI/FT/2024/007',
                'risk_categories': ['fire', 'theft', 'burglary', 'vandalism'],
                'features': {"fire_damage": True, "theft_burglary": True, "vandalism": True},
                'is_active': True
            }
        ]
        
        print(f"📝 Inserting {len(templates)} insurance templates...")
        
        try:
            # Try to insert templates - this will work if the table exists
            result = supabase.table('insurance_templates').insert(templates).execute()
            if result.data:
                print(f"✅ Successfully inserted {len(result.data)} insurance templates")
                for template in result.data[:3]:
                    print(f"   - {template['policy_name']}")
                return True
            else:
                print("❌ Insert returned no data")
                return False
                
        except Exception as e:
            error_msg = str(e)
            if "Could not find the table" in error_msg or "insurance_templates" in error_msg:
                print("❌ The insurance_templates table doesn't exist in Supabase")
                print("\n📋 Manual Setup Required:")
                print("1. Go to your Supabase dashboard: https://supabase.com/dashboard")
                print("2. Navigate to SQL Editor")
                print("3. Run this SQL to create the table:\n")
                
                # Show the SQL needed
                sql = '''
CREATE TABLE IF NOT EXISTS public.insurance_templates (
    template_id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(100) NOT NULL,
    provider_name VARCHAR(255) NOT NULL,
    business_types TEXT[],
    target_industries TEXT[],
    min_coverage_amount DECIMAL(15,2),
    max_coverage_amount DECIMAL(15,2),
    base_premium DECIMAL(15,2),
    coverage_description TEXT,
    legal_compliance BOOLEAN DEFAULT TRUE,
    compliance_authority VARCHAR(100) DEFAULT 'IRDAI',
    irdai_approval_number VARCHAR(255),
    risk_categories TEXT[],
    features JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS
ALTER TABLE public.insurance_templates ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access to templates
CREATE POLICY "Anyone can view insurance templates" ON public.insurance_templates
    FOR SELECT USING (true);

-- Create policy to allow authenticated users to insert templates (if needed)
CREATE POLICY "Authenticated users can manage templates" ON public.insurance_templates
    FOR ALL USING (auth.role() = 'authenticated');
'''
                print(sql)
                print("\n4. After creating the table, run this script again to insert the templates")
                return False
            else:
                print(f"❌ Unexpected error: {error_msg}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("Make sure your internet connection is working and Supabase is accessible")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Insurance Hub setup completed successfully!")
        print("You can now use the Insurance Hub feature in your application.")
    else:
        print("\n❌ Setup incomplete. Please follow the manual setup instructions above.")
    
    sys.exit(0 if success else 1)
