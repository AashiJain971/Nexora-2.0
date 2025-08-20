#!/usr/bin/env python3
"""
Execute insurance schema SQL and seed data for Insurance Hub.
This will create all required tables and populate sample data.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://eecbqzvcnwrkcxgwjxlt.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVlY2JxenZjbndya2N4Z3dqeGx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0Mjk1NjEsImV4cCI6MjA3MTAwNTU2MX0.CkhFT-6LKFg6NCc9WIiZRjNQ7VGVX6nJmoOxjMVHDKs")

def create_tables_via_rpc():
    """Create insurance tables using Supabase RPC (requires service role key)"""
    print("🔧 Creating insurance tables via direct SQL...")
    
    # Core insurance schema SQL
    insurance_sql = """
-- Insurance Hub Tables for Nexora MSME Platform

-- Create insurance_templates table for policy recommendations
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
    premium_calculation_factors JSONB,
    coverage_description TEXT NOT NULL,
    exclusions_description TEXT,
    legal_compliance BOOLEAN DEFAULT TRUE,
    compliance_authority VARCHAR(100) DEFAULT 'IRDAI',
    compliance_regions TEXT[] DEFAULT ARRAY['India'],
    irdai_approval_number VARCHAR(255),
    risk_categories TEXT[],
    optional_addons JSONB,
    features JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create insurance_policies table for user policies
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
    compliance_regions TEXT[] DEFAULT ARRAY['India'],
    policy_number VARCHAR(255),
    start_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    renewal_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    document_url TEXT,
    document_filename VARCHAR(255),
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
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create policy_reminders table
CREATE TABLE IF NOT EXISTS public.policy_reminders (
    reminder_id SERIAL PRIMARY KEY,
    policy_id INTEGER NOT NULL REFERENCES public.insurance_policies(policy_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    reminder_type VARCHAR(50) NOT NULL,
    reminder_date DATE NOT NULL,
    notification_sent BOOLEAN DEFAULT FALSE,
    email_sent BOOLEAN DEFAULT FALSE,
    notification_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_insurance_policies_user_id ON public.insurance_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_templates_policy_type ON public.insurance_templates(policy_type);
CREATE INDEX IF NOT EXISTS idx_business_risk_assessments_user_id ON public.business_risk_assessments(user_id);

-- Enable RLS
ALTER TABLE public.insurance_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.insurance_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_risk_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policy_reminders ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can manage their own insurance policies" ON public.insurance_policies
    FOR ALL USING (user_id = auth.uid()::integer);

CREATE POLICY "Anyone can view insurance templates" ON public.insurance_templates
    FOR SELECT USING (true);

CREATE POLICY "Users can manage their own risk assessments" ON public.business_risk_assessments
    FOR ALL USING (user_id = auth.uid()::integer);

CREATE POLICY "Users can manage their own policy reminders" ON public.policy_reminders
    FOR ALL USING (user_id = auth.uid()::integer);
"""

    print("📋 Insurance schema SQL prepared")
    print("💡 To create tables, run this SQL in your Supabase SQL Editor:")
    print("-" * 60)
    print(insurance_sql)
    print("-" * 60)
    
    return insurance_sql

def seed_sample_templates():
    """Seed sample insurance templates"""
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    templates = [
        {
            'policy_name': 'Professional Indemnity Insurance',
            'policy_type': 'professional_indemnity',
            'provider_name': 'HDFC ERGO',
            'business_types': ['services', 'consulting', 'digital'],
            'target_industries': ['technology', 'consulting', 'professional_services'],
            'min_coverage_amount': 500000,
            'max_coverage_amount': 10000000,
            'base_premium': 15000,
            'coverage_description': 'Protection against professional errors, omissions, and negligence claims',
            'legal_compliance': True,
            'compliance_authority': 'IRDAI',
            'irdai_approval_number': 'IRDAI/PI/2024/001',
            'risk_categories': ['professional_liability', 'errors_omissions'],
            'features': {
                "errors_omissions": True,
                "legal_costs": True,
                "defense_costs": True,
                "retrospective_cover": False
            },
            'optional_addons': {
                "extended_reporting": "Available for additional premium",
                "worldwide_cover": "Geographic extension available"
            },
            'is_active': True
        },
        {
            'policy_name': 'Cyber Liability Insurance',
            'policy_type': 'cyber_liability',
            'provider_name': 'ICICI Lombard',
            'business_types': ['digital', 'e-commerce', 'services'],
            'target_industries': ['technology', 'finance', 'healthcare'],
            'min_coverage_amount': 1000000,
            'max_coverage_amount': 50000000,
            'base_premium': 25000,
            'coverage_description': 'Comprehensive protection against cyber attacks, data breaches, and digital fraud',
            'legal_compliance': True,
            'compliance_authority': 'IRDAI',
            'irdai_approval_number': 'IRDAI/CY/2024/002',
            'risk_categories': ['cyber', 'data_breach', 'digital_fraud'],
            'features': {
                "data_breach": True,
                "cyber_extortion": True,
                "business_interruption": True,
                "forensic_costs": True
            },
            'optional_addons': {
                "social_media_liability": "Coverage for social media risks",
                "cyber_crime": "Enhanced cyber crime protection"
            },
            'is_active': True
        },
        {
            'policy_name': 'Public Liability Insurance',
            'policy_type': 'public_liability',
            'provider_name': 'New India Assurance',
            'business_types': ['retail', 'manufacturing', 'services'],
            'target_industries': ['retail', 'hospitality', 'manufacturing'],
            'min_coverage_amount': 200000,
            'max_coverage_amount': 5000000,
            'base_premium': 12000,
            'coverage_description': 'Coverage for third-party bodily injury and property damage claims',
            'legal_compliance': True,
            'compliance_authority': 'IRDAI',
            'irdai_approval_number': 'IRDAI/PL/2024/003',
            'risk_categories': ['liability', 'third_party_injury', 'property_damage'],
            'features': {
                "third_party_injury": True,
                "property_damage": True,
                "legal_expenses": True,
                "products_liability": False
            },
            'optional_addons': {
                "products_liability": "Coverage for product-related claims",
                "employers_liability": "Protection against employee claims"
            },
            'is_active': True
        },
        {
            'policy_name': 'Fire & Theft Insurance',
            'policy_type': 'asset_protection',
            'provider_name': 'Oriental Insurance',
            'business_types': ['retail', 'manufacturing'],
            'target_industries': ['retail', 'manufacturing', 'warehousing'],
            'min_coverage_amount': 300000,
            'max_coverage_amount': 15000000,
            'base_premium': 10000,
            'coverage_description': 'Protection against fire, theft, and burglary of business assets',
            'legal_compliance': True,
            'compliance_authority': 'IRDAI',
            'irdai_approval_number': 'IRDAI/FT/2024/007',
            'risk_categories': ['fire', 'theft', 'burglary', 'vandalism'],
            'features': {
                "fire_damage": True,
                "theft_burglary": True,
                "vandalism": True,
                "business_interruption": False
            },
            'optional_addons': {
                "business_interruption": "Loss of income coverage",
                "machinery_breakdown": "Equipment breakdown protection"
            },
            'is_active': True
        },
        {
            'policy_name': 'Employee Health Insurance',
            'policy_type': 'health',
            'provider_name': 'Star Health',
            'business_types': ['services', 'manufacturing', 'retail', 'digital'],
            'target_industries': ['all'],
            'min_coverage_amount': 100000,
            'max_coverage_amount': 2000000,
            'base_premium': 8000,
            'coverage_description': 'Comprehensive health coverage for employees and their families',
            'legal_compliance': True,
            'compliance_authority': 'IRDAI',
            'irdai_approval_number': 'IRDAI/HI/2024/006',
            'risk_categories': ['employee_welfare', 'medical_emergencies'],
            'features': {
                "cashless_treatment": True,
                "pre_existing_diseases": True,
                "maternity_cover": True,
                "dental_vision": False
            },
            'optional_addons': {
                "dental_vision": "Dental and vision coverage",
                "critical_illness": "Enhanced critical illness benefits"
            },
            'is_active': True
        }
    ]
    
    print("🌱 Seeding insurance templates...")
    
    success_count = 0
    for template in templates:
        try:
            result = supabase.table('insurance_templates').insert(template).execute()
            print(f"✅ Seeded: {template['policy_name']}")
            success_count += 1
        except Exception as e:
            print(f"ℹ️ {template['policy_name']}: {e}")
    
    if success_count > 0:
        print(f"🎉 Successfully seeded {success_count} insurance templates!")
    else:
        print("⚠️ No templates were seeded - tables may not exist yet")
    
    return success_count

def main():
    print("🚀 Insurance Hub Database Setup")
    print("=" * 50)
    
    # First, show the SQL schema
    schema_sql = create_tables_via_rpc()
    
    # Try to seed templates (will fail if tables don't exist)
    print("\n🌱 Attempting to seed sample templates...")
    seeded_count = seed_sample_templates()
    
    if seeded_count > 0:
        print("\n✅ Database setup complete!")
        print("🎯 Insurance Hub is ready for recommendations")
    else:
        print("\n📝 Next Steps:")
        print("1. Copy the SQL schema above")
        print("2. Run it in your Supabase SQL Editor")
        print("3. Run this script again to seed templates")
        
        # Write SQL to file for easy copying
        with open('insurance_schema_setup.sql', 'w') as f:
            f.write(schema_sql)
        print("💾 Schema saved to: insurance_schema_setup.sql")

if __name__ == "__main__":
    main()
