#!/usr/bin/env python3
"""
Setup insurance tables in Supabase database
"""
import sys
import json
from supabase import create_client

# Supabase configuration
SUPABASE_URL = "https://yhfdwzizydowbiphdgap.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InloZmR3eml6eWRvd2JpcGhkZ2FwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzc1OTA5OSwiZXhwIjoyMDQ5MzM1MDk5fQ.f-X9kSWagBKVHQBAiJ2yV7uRnkkW4sDIlbIqe1OUo6w"

def main():
    """Main setup function"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase")
        
        # Test connection with a simple query
        result = supabase.table('users').select('id').limit(1).execute()
        print("✅ Database connection verified")
        
        # Insurance templates data
        insurance_templates = [
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
        
        # Try to insert insurance templates
        print(f"📝 Inserting {len(insurance_templates)} insurance templates...")
        try:
            # Clear existing templates first
            supabase.table('insurance_templates').delete().neq('template_id', 0).execute()
            print("🧹 Cleared existing templates")
        except Exception as e:
            print(f"ℹ️ Could not clear existing templates (table might not exist): {e}")
        
        # Insert new templates
        try:
            result = supabase.table('insurance_templates').insert(insurance_templates).execute()
            if result.data:
                print(f"✅ Successfully inserted {len(result.data)} insurance templates")
                for template in result.data[:3]:  # Show first 3
                    print(f"   - {template['policy_name']} (ID: {template['template_id']})")
                if len(result.data) > 3:
                    print(f"   ... and {len(result.data) - 3} more")
            else:
                print("❌ No data returned from insert operation")
                
        except Exception as e:
            print(f"❌ Error inserting templates: {e}")
            print("📋 This might mean the insurance_templates table doesn't exist yet.")
            print("📋 Please create the table structure in Supabase dashboard first.")
            
            # Show the required table structure
            print("\n📋 Required table structure for 'insurance_templates':")
            print("CREATE TABLE insurance_templates (")
            print("  template_id SERIAL PRIMARY KEY,")
            print("  policy_name VARCHAR(255) NOT NULL,")
            print("  policy_type VARCHAR(100) NOT NULL,")
            print("  provider_name VARCHAR(255) NOT NULL,")
            print("  business_types TEXT[],")
            print("  target_industries TEXT[],")
            print("  min_coverage_amount DECIMAL(15,2),")
            print("  max_coverage_amount DECIMAL(15,2),")
            print("  base_premium DECIMAL(15,2),")
            print("  coverage_description TEXT,")
            print("  legal_compliance BOOLEAN DEFAULT TRUE,")
            print("  compliance_authority VARCHAR(100) DEFAULT 'IRDAI',")
            print("  irdai_approval_number VARCHAR(255),")
            print("  risk_categories TEXT[],")
            print("  features JSONB,")
            print("  is_active BOOLEAN DEFAULT TRUE")
            print(");")
            
            return False
        
        # Verify the data
        try:
            verification = supabase.table('insurance_templates').select('template_id, policy_name').execute()
            print(f"✅ Verification: Found {len(verification.data)} templates in database")
            return True
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
