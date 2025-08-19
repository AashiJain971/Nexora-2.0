-- Insurance Hub Database Schema
-- Add these tables to your existing Supabase database

-- Insurance templates/plans available for recommendation
CREATE TABLE IF NOT EXISTS public.insurance_templates (
    id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(100) NOT NULL, -- 'liability', 'health', 'asset', 'cyber', 'fire', 'transport'
    provider_name VARCHAR(255) NOT NULL,
    business_types TEXT[], -- ['manufacturing', 'retail', 'services', 'digital']
    coverage_description TEXT NOT NULL,
    base_coverage_amount DECIMAL(15,2) NOT NULL,
    premium_range_min DECIMAL(10,2) NOT NULL,
    premium_range_max DECIMAL(10,2) NOT NULL,
    premium_percentage DECIMAL(5,2), -- percentage of coverage amount
    legal_compliance BOOLEAN DEFAULT true, -- IRDAI approved or equivalent
    compliance_authority VARCHAR(100) DEFAULT 'IRDAI', -- IRDAI, FCA, etc.
    coverage_features JSONB, -- detailed coverage breakdown
    exclusions TEXT[],
    optional_addons JSONB,
    risk_categories TEXT[], -- ['theft', 'fire', 'cyber', 'employee_welfare']
    min_business_size INTEGER DEFAULT 1, -- minimum employees/turnover
    max_business_size INTEGER, -- maximum coverage limit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User's insurance policies (purchased or tracked)
CREATE TABLE IF NOT EXISTS public.insurance_policies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    business_id INTEGER REFERENCES public.businesses(id) ON DELETE CASCADE,
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(100) NOT NULL,
    provider_name VARCHAR(255),
    coverage_amount DECIMAL(15,2) NOT NULL,
    premium_amount DECIMAL(10,2),
    premium_frequency VARCHAR(50) DEFAULT 'annual', -- 'monthly', 'quarterly', 'annual'
    start_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    policy_number VARCHAR(255),
    legal_compliance BOOLEAN DEFAULT true,
    compliance_authority VARCHAR(100) DEFAULT 'IRDAI',
    document_url VARCHAR(500), -- uploaded policy document
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'expired', 'cancelled', 'pending'
    renewal_reminder_sent BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Business risk assessments for insurance recommendations
CREATE TABLE IF NOT EXISTS public.business_risk_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    business_id INTEGER REFERENCES public.businesses(id) ON DELETE CASCADE,
    assessment_data JSONB NOT NULL, -- risk categories, asset values, employee count
    recommended_policies JSONB, -- array of recommended policy IDs with scores
    risk_score INTEGER, -- overall risk score 1-100
    priority_risks TEXT[], -- top 3 risk categories
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_insurance_templates_policy_type ON public.insurance_templates(policy_type);
CREATE INDEX IF NOT EXISTS idx_insurance_templates_business_types ON public.insurance_templates USING GIN(business_types);
CREATE INDEX IF NOT EXISTS idx_insurance_templates_risk_categories ON public.insurance_templates USING GIN(risk_categories);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_user_id ON public.insurance_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_expiry_date ON public.insurance_policies(expiry_date);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_status ON public.insurance_policies(status);
CREATE INDEX IF NOT EXISTS idx_business_risk_assessments_user_id ON public.business_risk_assessments(user_id);

-- Add triggers for updated_at
CREATE TRIGGER update_insurance_templates_updated_at 
    BEFORE UPDATE ON public.insurance_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insurance_policies_updated_at 
    BEFORE UPDATE ON public.insurance_policies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_business_risk_assessments_updated_at 
    BEFORE UPDATE ON public.business_risk_assessments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.insurance_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.insurance_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_risk_assessments ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Insurance templates are public" ON public.insurance_templates
    FOR SELECT USING (true);

CREATE POLICY "Users can view their own insurance policies" ON public.insurance_policies
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own insurance policies" ON public.insurance_policies
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own insurance policies" ON public.insurance_policies
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own insurance policies" ON public.insurance_policies
    FOR DELETE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can view their own risk assessments" ON public.business_risk_assessments
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own risk assessments" ON public.business_risk_assessments
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own risk assessments" ON public.business_risk_assessments
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Insert sample insurance templates
INSERT INTO public.insurance_templates (
    policy_name, policy_type, provider_name, business_types, coverage_description,
    base_coverage_amount, premium_range_min, premium_range_max, premium_percentage,
    coverage_features, exclusions, optional_addons, risk_categories
) VALUES 
-- General Liability Insurance
('MSME General Liability Pro', 'liability', 'HDFC ERGO', 
 ARRAY['manufacturing', 'retail', 'services'], 
 'Comprehensive third-party liability coverage for property damage, bodily injury, and legal costs',
 1000000.00, 15000.00, 25000.00, 2.5,
 '{"property_damage": 500000, "bodily_injury": 500000, "legal_costs": 100000, "product_liability": true}',
 ARRAY['intentional acts', 'criminal activities', 'professional errors'],
 '{"extended_coverage": {"cost": 5000, "coverage": 200000}, "cyber_addon": {"cost": 8000, "coverage": 300000}}',
 ARRAY['liability', 'property_damage', 'legal_costs']),

-- Fire and Allied Perils
('Business Fire Shield', 'fire', 'ICICI Lombard', 
 ARRAY['manufacturing', 'retail', 'warehouse'], 
 'Protection against fire, explosion, lightning, and allied perils for business premises and stock',
 2000000.00, 12000.00, 20000.00, 1.0,
 '{"building_coverage": 1000000, "stock_coverage": 800000, "machinery_coverage": 200000}',
 ARRAY['war risks', 'nuclear perils', 'terrorism'],
 '{"earthquake_addon": {"cost": 10000, "coverage": 500000}, "flood_addon": {"cost": 8000, "coverage": 300000}}',
 ARRAY['fire', 'natural_disasters', 'asset_protection']),

-- Cyber Security Insurance
('Cyber Safe Pro', 'cyber', 'Bajaj Allianz', 
 ARRAY['digital', 'services', 'retail'], 
 'Comprehensive cyber security coverage including data breach, cyber fraud, and business interruption',
 5000000.00, 25000.00, 45000.00, 0.8,
 '{"data_breach": 2000000, "cyber_fraud": 1000000, "business_interruption": 1000000, "legal_costs": 1000000}',
 ARRAY['physical theft', 'employee dishonesty', 'war cyber attacks'],
 '{"social_engineering": {"cost": 15000, "coverage": 500000}, "reputation_management": {"cost": 12000, "coverage": 300000}}',
 ARRAY['cyber', 'data_breach', 'business_interruption']),

-- Employee Health Insurance
('Group Health Advantage', 'health', 'Star Health Insurance', 
 ARRAY['manufacturing', 'services', 'retail', 'digital'], 
 'Group health insurance for employees covering hospitalization, OPD, and preventive care',
 500000.00, 8000.00, 15000.00, 3.0,
 '{"hospitalization": 400000, "opd_coverage": 50000, "preventive_care": 25000, "ambulance": 25000}',
 ARRAY['pre-existing conditions (first year)', 'cosmetic treatments', 'dental (basic plan)'],
 '{"maternity_addon": {"cost": 5000, "coverage": 100000}, "dental_addon": {"cost": 3000, "coverage": 50000}}',
 ARRAY['employee_welfare', 'health_coverage']),

-- Marine/Transport Insurance
('Goods Transit Pro', 'transport', 'Oriental Insurance', 
 ARRAY['manufacturing', 'retail', 'export'], 
 'Coverage for goods in transit by road, rail, air, or sea against theft, damage, and loss',
 1500000.00, 10000.00, 18000.00, 1.2,
 '{"theft_coverage": 600000, "damage_coverage": 600000, "delay_compensation": 300000}',
 ARRAY['inherent vice', 'ordinary leakage', 'war risks'],
 '{"warehouse_addon": {"cost": 7000, "coverage": 200000}, "cold_chain": {"cost": 12000, "coverage": 400000}}',
 ARRAY['transport', 'theft', 'goods_damage'])

ON CONFLICT DO NOTHING;
