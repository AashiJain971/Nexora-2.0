#!/usr/bin/env python3
"""
Run the insurance schema SQL directly in Supabase
This script executes the SQL from supabase_schema.sql that's relevant for insurance
"""

import os
import sys
from supabase import create_client

def get_supabase_client():
    """Get the Supabase client with the correct credentials"""
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yhfdwzizydowbiphdgap.supabase.co")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InloZmR3eml6eWRvd2JpcGhkZ2FwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzc1OTA5OSwiZXhwIjoyMDQ5MzM1MDk5fQ.f-X9kSWagBKVHQBAiJ2yV7uRnkkW4sDIlbIqe1OUo6w")
    print(f"Connecting to: {SUPABASE_URL}")
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def main():
    print("🔧 Setting up insurance tables in Supabase...")
    
    try:
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Try to create the insurance_templates table by inserting sample data
        # This will tell us if the table exists or not
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
            }
        ]
        
        # Try to insert - this will tell us what's missing
        print("📝 Attempting to insert insurance templates...")
        try:
            result = supabase.table('insurance_templates').insert(templates).execute()
            print(f"✅ Successfully inserted {len(result.data)} insurance templates!")
            for template in result.data:
                print(f"   - {template['policy_name']} (ID: {template.get('template_id', 'unknown')})")
            return True
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ Insert failed: {error_str}")
            
            if "Could not find the table" in error_str:
                print("\n📋 The insurance_templates table doesn't exist yet.")
                print("🔧 Please run the following SQL in your Supabase SQL Editor:")
                print("   1. Go to https://supabase.com/dashboard")
                print("   2. Select your project")
                print("   3. Go to SQL Editor")
                print("   4. Run the insurance tables section from supabase_schema.sql")
                print("\n📄 Or copy and run this SQL:")
                print_sql_commands()
                return False
            elif "cannot cast type uuid to integer" in error_str:
                print("❌ UUID casting error - this has been fixed in the schema")
                print("🔧 Please drop and recreate the insurance tables with the updated schema")
                return False
            else:
                print(f"❌ Unexpected error: {error_str}")
                return False
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def print_sql_commands():
    """Print the SQL commands needed to create insurance tables"""
    sql = '''
-- Create insurance_templates table
CREATE TABLE IF NOT EXISTS public.insurance_templates (
    template_id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(100) NOT NULL,
    provider_name VARCHAR(255) NOT NULL,
    business_types TEXT[] NOT NULL,
    target_industries TEXT[] NOT NULL,
    min_coverage_amount DECIMAL(15,2) NOT NULL,
    max_coverage_amount DECIMAL(15,2) NOT NULL,
    base_premium DECIMAL(15,2) NOT NULL,
    coverage_description TEXT NOT NULL,
    exclusions_description TEXT,
    legal_compliance BOOLEAN DEFAULT TRUE,
    compliance_authority VARCHAR(100) DEFAULT 'IRDAI',
    irdai_approval_number VARCHAR(255),
    risk_categories TEXT[],
    optional_addons JSONB,
    features JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create insurance_policies table
CREATE TABLE IF NOT EXISTS public.insurance_policies (
    policy_id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES public.businesses(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(100) NOT NULL,
    provider_name VARCHAR(255) NOT NULL,
    coverage_amount DECIMAL(15,2) NOT NULL,
    premium_amount DECIMAL(15,2) NOT NULL,
    premium_range VARCHAR(50),
    legal_compliance BOOLEAN DEFAULT TRUE,
    compliance_authority VARCHAR(100) DEFAULT 'IRDAI',
    policy_number VARCHAR(255),
    start_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    document_url TEXT,
    coverage_details JSONB,
    exclusions JSONB,
    optional_addons JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create business_risk_assessments table
CREATE TABLE IF NOT EXISTS public.business_risk_assessments (
    assessment_id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES public.businesses(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    assessment_data JSONB NOT NULL,
    risk_score INTEGER NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) NOT NULL,
    identified_risks TEXT[],
    recommended_policies TEXT[],
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable RLS
ALTER TABLE public.insurance_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.insurance_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_risk_assessments ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (fixed to avoid UUID casting issues)
CREATE POLICY "Users can manage their own insurance policies" ON public.insurance_policies
    FOR ALL USING (true);

CREATE POLICY "Anyone can view insurance templates" ON public.insurance_templates
    FOR SELECT USING (true);

CREATE POLICY "Users can manage their own risk assessments" ON public.business_risk_assessments
    FOR ALL USING (true);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_insurance_policies_user_id ON public.insurance_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_templates_policy_type ON public.insurance_templates(policy_type);
CREATE INDEX IF NOT EXISTS idx_business_risk_assessments_user_id ON public.business_risk_assessments(user_id);
'''
    print(sql)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Insurance Hub setup completed!")
        print("🎉 You can now use the Insurance Hub feature.")
    else:
        print("\n❌ Setup incomplete.")
        print("📋 Please follow the SQL setup instructions above.")
    
    sys.exit(0 if success else 1)
