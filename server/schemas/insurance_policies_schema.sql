-- Insurance Policies Management Schema
-- Run this SQL in your Supabase SQL editor after running the main supabase_schema.sql

-- Create insurance_policies table as requested by the user
CREATE TABLE IF NOT EXISTS public.insurance_policies (
    policy_id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(100) NOT NULL, -- 'health', 'liability', 'asset', 'cyber', 'professional_indemnity', etc.
    provider_name VARCHAR(255) NOT NULL,
    coverage_amount DECIMAL(15,2) NOT NULL,
    premium_amount DECIMAL(15,2) NOT NULL,
    premium_range VARCHAR(50), -- 'Low', 'Medium', 'High' or specific range
    legal_compliance BOOLEAN DEFAULT TRUE, -- true if IRDAI-approved or region-compliant
    compliance_authority VARCHAR(100) DEFAULT 'IRDAI', -- 'IRDAI', 'FCA', 'NAIC', etc.
    compliance_regions TEXT[] DEFAULT ARRAY['India'], -- ['India', 'Europe', 'USA']
    policy_number VARCHAR(255),
    start_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    renewal_date DATE, -- for reminder notifications
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'expired', 'cancelled', 'pending_renewal'
    document_url TEXT, -- link to uploaded policy document (PDF/scan)
    document_filename VARCHAR(255),
    coverage_details JSONB, -- detailed coverage information
    exclusions JSONB, -- what is not covered
    optional_addons JSONB, -- extra coverage options
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create insurance_templates table (enhanced version for recommendations)
CREATE TABLE IF NOT EXISTS public.insurance_templates (
    template_id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(100) NOT NULL,
    provider_name VARCHAR(255) NOT NULL,
    business_types TEXT[] NOT NULL, -- ['manufacturing', 'services', 'retail', 'digital', 'e-commerce']
    target_industries TEXT[] NOT NULL, -- ['technology', 'healthcare', 'finance', 'manufacturing']
    min_coverage_amount DECIMAL(15,2) NOT NULL,
    max_coverage_amount DECIMAL(15,2) NOT NULL,
    base_premium DECIMAL(15,2) NOT NULL,
    premium_calculation_factors JSONB, -- factors that affect premium calculation
    coverage_description TEXT NOT NULL,
    exclusions_description TEXT,
    legal_compliance BOOLEAN DEFAULT TRUE,
    compliance_authority VARCHAR(100) DEFAULT 'IRDAI',
    compliance_regions TEXT[] DEFAULT ARRAY['India'],
    irdai_approval_number VARCHAR(255), -- official IRDAI approval reference
    risk_categories TEXT[], -- ['theft', 'cyber_fraud', 'fire', 'employee_welfare', 'liability']
    optional_addons JSONB,
    features JSONB, -- key features and benefits
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create business_risk_assessments table
CREATE TABLE IF NOT EXISTS public.business_risk_assessments (
    assessment_id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES public.businesses(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    assessment_data JSONB NOT NULL, -- complete risk assessment responses
    risk_score INTEGER NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) NOT NULL, -- 'Low', 'Medium', 'High', 'Critical'
    identified_risks TEXT[], -- ['cyber_security', 'fire_hazard', 'theft', 'liability']
    recommended_policies TEXT[], -- policy types recommended based on assessment
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE, -- mark latest assessment
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create policy_reminders table for renewal notifications
CREATE TABLE IF NOT EXISTS public.policy_reminders (
    reminder_id SERIAL PRIMARY KEY,
    policy_id INTEGER NOT NULL REFERENCES public.insurance_policies(policy_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    reminder_type VARCHAR(50) NOT NULL, -- 'renewal', 'payment_due', 'document_expiry'
    reminder_date DATE NOT NULL,
    notification_sent BOOLEAN DEFAULT FALSE,
    email_sent BOOLEAN DEFAULT FALSE,
    notification_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_insurance_policies_user_id ON public.insurance_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_business_id ON public.insurance_policies(business_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_policy_type ON public.insurance_policies(policy_type);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_expiry_date ON public.insurance_policies(expiry_date);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_status ON public.insurance_policies(status);

CREATE INDEX IF NOT EXISTS idx_insurance_templates_policy_type ON public.insurance_templates(policy_type);
CREATE INDEX IF NOT EXISTS idx_insurance_templates_business_types ON public.insurance_templates USING GIN(business_types);
CREATE INDEX IF NOT EXISTS idx_insurance_templates_risk_categories ON public.insurance_templates USING GIN(risk_categories);

CREATE INDEX IF NOT EXISTS idx_business_risk_assessments_user_id ON public.business_risk_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_business_risk_assessments_business_id ON public.business_risk_assessments(business_id);
CREATE INDEX IF NOT EXISTS idx_business_risk_assessments_risk_level ON public.business_risk_assessments(risk_level);

CREATE INDEX IF NOT EXISTS idx_policy_reminders_user_id ON public.policy_reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_policy_reminders_reminder_date ON public.policy_reminders(reminder_date);
CREATE INDEX IF NOT EXISTS idx_policy_reminders_notification_sent ON public.policy_reminders(notification_sent);

-- Create updated_at triggers
CREATE TRIGGER update_insurance_policies_updated_at 
    BEFORE UPDATE ON public.insurance_policies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insurance_templates_updated_at 
    BEFORE UPDATE ON public.insurance_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS for all insurance tables
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

-- Insert sample IRDAI-approved insurance templates
INSERT INTO public.insurance_templates (
    policy_name, policy_type, provider_name, business_types, target_industries,
    min_coverage_amount, max_coverage_amount, base_premium, coverage_description,
    legal_compliance, compliance_authority, irdai_approval_number, risk_categories, features
) VALUES 
    ('Professional Indemnity Insurance', 'professional_indemnity', 'HDFC ERGO',
     ARRAY['services', 'consulting', 'digital'], ARRAY['technology', 'consulting', 'professional_services'],
     500000, 10000000, 15000, 'Protection against professional errors, omissions, and negligence claims',
     TRUE, 'IRDAI', 'IRDAI/PI/2024/001', ARRAY['professional_liability', 'errors_omissions'],
     '{"errors_omissions": true, "legal_costs": true, "defense_costs": true, "retrospective_cover": false}'::jsonb),
    
    ('Cyber Liability Insurance', 'cyber_liability', 'ICICI Lombard',
     ARRAY['digital', 'e-commerce', 'services'], ARRAY['technology', 'finance', 'healthcare'],
     1000000, 50000000, 25000, 'Comprehensive protection against cyber attacks, data breaches, and digital fraud',
     TRUE, 'IRDAI', 'IRDAI/CY/2024/002', ARRAY['cyber_security', 'data_breach', 'digital_fraud'],
     '{"data_breach": true, "cyber_extortion": true, "business_interruption": true, "forensic_costs": true}'::jsonb),
    
    ('Public Liability Insurance', 'public_liability', 'New India Assurance',
     ARRAY['retail', 'manufacturing', 'services'], ARRAY['retail', 'hospitality', 'manufacturing'],
     200000, 5000000, 12000, 'Coverage for third-party bodily injury and property damage claims',
     TRUE, 'IRDAI', 'IRDAI/PL/2024/003', ARRAY['third_party_injury', 'property_damage', 'public_liability'],
     '{"third_party_injury": true, "property_damage": true, "legal_expenses": true, "products_liability": false}'::jsonb),
    
    ('Product Liability Insurance', 'product_liability', 'Bajaj Allianz',
     ARRAY['manufacturing', 'retail'], ARRAY['manufacturing', 'food_beverage', 'pharmaceuticals'],
     500000, 20000000, 18000, 'Protection against claims arising from defective products',
     TRUE, 'IRDAI', 'IRDAI/PL/2024/004', ARRAY['product_defects', 'manufacturing_defects', 'design_flaws'],
     '{"product_defects": true, "recall_costs": true, "legal_defense": true, "worldwide_cover": false}'::jsonb),
    
    ('Directors & Officers Insurance', 'directors_officers', 'Tata AIG',
     ARRAY['services', 'manufacturing', 'digital'], ARRAY['technology', 'finance', 'healthcare'],
     2000000, 100000000, 35000, 'Protection for company directors and officers against management liability claims',
     TRUE, 'IRDAI', 'IRDAI/DO/2024/005', ARRAY['management_liability', 'regulatory_investigations', 'employment_practices'],
     '{"management_liability": true, "legal_costs": true, "regulatory_investigations": true, "entity_coverage": true}'::jsonb),
    
    ('Employee Health Insurance', 'health', 'Star Health',
     ARRAY['services', 'manufacturing', 'retail', 'digital'], ARRAY['all'],
     100000, 2000000, 8000, 'Comprehensive health coverage for employees and their families',
     TRUE, 'IRDAI', 'IRDAI/HI/2024/006', ARRAY['employee_welfare', 'medical_emergencies'],
     '{"cashless_treatment": true, "pre_existing_diseases": true, "maternity_cover": true, "dental_vision": false}'::jsonb),
    
    ('Fire & Theft Insurance', 'asset_protection', 'Oriental Insurance',
     ARRAY['retail', 'manufacturing'], ARRAY['retail', 'manufacturing', 'warehousing'],
     300000, 15000000, 10000, 'Protection against fire, theft, and burglary of business assets',
     TRUE, 'IRDAI', 'IRDAI/FT/2024/007', ARRAY['fire_hazard', 'theft', 'burglary', 'vandalism'],
     '{"fire_damage": true, "theft_burglary": true, "vandalism": true, "business_interruption": false}'::jsonb)
ON CONFLICT DO NOTHING;

-- Insert sample business risk assessment data
INSERT INTO public.businesses (user_id, business_name, business_type, industry, location_country, location_state, location_city) VALUES 
    (1, 'TechStart Solutions', 'services', 'technology', 'India', 'Karnataka', 'Bangalore'),
    (2, 'Digital Marketing Hub', 'digital', 'marketing', 'India', 'Maharashtra', 'Mumbai')
ON CONFLICT (user_id) DO NOTHING;
