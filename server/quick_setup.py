#!/usr/bin/env python3
"""
Quick setup script to create essential tables for login/register functionality
This creates just the basic tables needed for authentication to work
"""

import os
import sys

def main():
    print("🔧 Creating essential SQL for Supabase tables...")
    print("\n📋 Please copy and run this SQL in your Supabase SQL Editor:")
    print("   Go to: https://supabase.com/dashboard/project/yhfdwzizydowbiphdgap/sql")
    print("\n" + "="*60)
    
    essential_sql = '''
-- Essential tables for authentication and basic functionality
-- Copy and paste this SQL into Supabase SQL Editor

-- Create users table for authentication
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create invoices table for credit score
CREATE TABLE IF NOT EXISTS public.invoices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    invoice_number VARCHAR(255) NOT NULL,
    client VARCHAR(255) NOT NULL,
    date DATE,
    payment_terms VARCHAR(255),
    industry VARCHAR(255),
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    currency VARCHAR(20) DEFAULT 'INR',
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

-- Create insurance_templates table for Insurance Hub
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

-- Enable RLS (Row Level Security)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.insurance_templates ENABLE ROW LEVEL SECURITY;

-- Create simple RLS policies (allow all for now)
CREATE POLICY "Allow all operations for authenticated users" ON public.users
    FOR ALL USING (true);

CREATE POLICY "Users can access invoices" ON public.invoices
    FOR ALL USING (true);

CREATE POLICY "Anyone can view insurance templates" ON public.insurance_templates
    FOR SELECT USING (true);

-- Insert a test user for login
INSERT INTO public.users (email, full_name, password_hash) VALUES 
    ('demo@nexora.com', 'Demo User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNi7GPlLyrs/2')
ON CONFLICT (email) DO NOTHING;

-- Insert insurance templates
INSERT INTO public.insurance_templates (
    policy_name, policy_type, provider_name, business_types, target_industries,
    min_coverage_amount, max_coverage_amount, base_premium, coverage_description,
    legal_compliance, compliance_authority, irdai_approval_number, risk_categories, features
) VALUES 
    ('Professional Indemnity Insurance', 'professional_indemnity', 'HDFC ERGO',
     ARRAY['services', 'consulting', 'digital'], ARRAY['technology', 'consulting', 'professional_services'],
     500000, 10000000, 15000, 'Protection against professional errors, omissions, and negligence claims',
     TRUE, 'IRDAI', 'IRDAI/PI/2024/001', ARRAY['professional_liability', 'errors_omissions'],
     '{"errors_omissions": true, "legal_costs": true, "defense_costs": true}'::jsonb),
    
    ('Cyber Liability Insurance', 'cyber_liability', 'ICICI Lombard',
     ARRAY['digital', 'e-commerce', 'services'], ARRAY['technology', 'finance', 'healthcare'],
     1000000, 50000000, 25000, 'Comprehensive protection against cyber attacks, data breaches, and digital fraud',
     TRUE, 'IRDAI', 'IRDAI/CY/2024/002', ARRAY['cyber', 'data_breach', 'digital_fraud'],
     '{"data_breach": true, "cyber_extortion": true, "business_interruption": true}'::jsonb),
    
    ('Public Liability Insurance', 'public_liability', 'New India Assurance',
     ARRAY['retail', 'manufacturing', 'services'], ARRAY['retail', 'hospitality', 'manufacturing'],
     200000, 5000000, 12000, 'Coverage for third-party bodily injury and property damage claims',
     TRUE, 'IRDAI', 'IRDAI/PL/2024/003', ARRAY['liability', 'third_party_injury', 'property_damage'],
     '{"third_party_injury": true, "property_damage": true, "legal_expenses": true}'::jsonb)
ON CONFLICT DO NOTHING;

-- Insert sample invoice data
INSERT INTO public.invoices (
    user_id, invoice_number, client, date, payment_terms, industry, 
    total_amount, currency, tax_amount, extra_charges, 
    line_items, status
) VALUES 
    (1, 'INV-001', 'ABC Corp', '2024-01-15', '30 days', 'Technology', 
     50000.00, 'INR', 9000.00, 1000.00, 
     '[{"description": "Software License", "amount": 40000}]', 'paid'),
    (1, 'INV-002', 'XYZ Ltd', '2024-02-01', '15 days', 'Manufacturing', 
     75000.00, 'INR', 13500.00, 500.00, 
     '[{"description": "Equipment", "amount": 61000}]', 'paid'),
    (1, 'INV-003', 'ABC Corp', '2024-02-15', '30 days', 'Technology', 
     60000.00, 'INR', 10800.00, 1200.00, 
     '[{"description": "Maintenance", "amount": 48000}]', 'pending')
ON CONFLICT (invoice_number, user_id) DO NOTHING;
'''
    
    print(essential_sql)
    print("="*60)
    print("\n✅ After running this SQL:")
    print("   - Login with: demo@nexora.com / password")
    print("   - Credit Score will work")  
    print("   - Insurance Hub will work")
    print("   - Invoice upload will work")
    print("\n🔄 Then restart your backend server to see the changes")

if __name__ == "__main__":
    main()
