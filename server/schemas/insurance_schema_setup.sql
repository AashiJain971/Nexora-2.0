
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
