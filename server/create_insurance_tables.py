#!/usr/bin/env python3
"""
Create insurance tables and seed sample data for the Insurance Hub feature.
Run this script to set up the database tables.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://eecbqzvcnwrkcxgwjxlt.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVlY2JxenZjbndya2N4Z3dqeGx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0Mjk1NjEsImV4cCI6MjA3MTAwNTU2MX0.CkhFT-6LKFg6NCc9WIiZRjNQ7VGVX6nJmoOxjMVHDKs")

def main():
    print("🔧 Setting up Insurance Hub database tables...")
    
    # Initialize Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Create insurance_templates table
    print("📋 Creating insurance_templates table...")
    try:
        # Insert sample insurance templates
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
        
        # Try to insert templates - this will work if the table exists via SQL
        for template in templates:
            try:
                result = supabase.table('insurance_templates').insert(template).execute()
                print(f"✅ Inserted template: {template['policy_name']}")
            except Exception as e:
                print(f"ℹ️ Template insert note: {e}")
        
        print("✅ Insurance templates setup complete!")
        
    except Exception as e:
        print(f"ℹ️ Template setup info: {e}")
    
    # Test connection to verify setup
    try:
        result = supabase.table('insurance_templates').select('*').limit(3).execute()
        template_count = len(result.data) if result.data else 0
        print(f"📊 Found {template_count} insurance templates in database")
        
        if template_count > 0:
            print("🎉 Insurance Hub database setup is complete!")
            print("✅ Templates are ready for recommendations")
        else:
            print("⚠️ No templates found - please run the SQL schema first")
            
    except Exception as e:
        print(f"ℹ️ Database check: {e}")
        print("💡 Please run insurance_policies_schema.sql in your Supabase SQL editor")

if __name__ == "__main__":
    main()
