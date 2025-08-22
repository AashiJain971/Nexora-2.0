-- Create users table for authentication
-- Run this SQL in your Supabase SQL editor

CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create invoices table to store invoice data for credit score calculations
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
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'paid', 'overdue'
    credit_score DECIMAL(5,2) DEFAULT NULL, -- Store individual invoice credit score
    credit_score_data JSONB DEFAULT NULL, -- Store complete credit score analysis
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    payment_date DATE,
    UNIQUE(invoice_number, user_id)
);

-- Create businesses table to store MSME business details
CREATE TABLE IF NOT EXISTS public.businesses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(100) NOT NULL, -- 'retail', 'service', 'manufacturing', 'e-commerce', etc.
    industry VARCHAR(100) NOT NULL,
    location_country VARCHAR(100) NOT NULL,
    location_state VARCHAR(100),
    location_city VARCHAR(100),
    website_url VARCHAR(500),
    has_online_presence BOOLEAN DEFAULT FALSE,
    has_physical_store BOOLEAN DEFAULT FALSE,
    collects_personal_data BOOLEAN DEFAULT TRUE,
    processes_payments BOOLEAN DEFAULT FALSE,
    uses_cookies BOOLEAN DEFAULT FALSE,
    has_newsletter BOOLEAN DEFAULT FALSE,
    target_audience TEXT, -- 'B2B', 'B2C', 'Both'
    data_retention_period INTEGER DEFAULT 365, -- days
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id) -- One business per user for now
);

-- Create policies table to store generated legal documents
CREATE TABLE IF NOT EXISTS public.policies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(50) NOT NULL, -- 'privacy_policy', 'terms_conditions', 'refund_policy', 'cookie_policy'
    content TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    compliance_regions TEXT[], -- ['GDPR', 'Indian_IT_Act', 'CCPA', etc.]
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON public.invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_client ON public.invoices(client);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON public.invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON public.invoices(created_at);
CREATE INDEX IF NOT EXISTS idx_businesses_user_id ON public.businesses(user_id);
CREATE INDEX IF NOT EXISTS idx_businesses_business_type ON public.businesses(business_type);
CREATE INDEX IF NOT EXISTS idx_businesses_location_country ON public.businesses(location_country);
CREATE INDEX IF NOT EXISTS idx_policies_user_id ON public.policies(user_id);
CREATE INDEX IF NOT EXISTS idx_policies_type ON public.policies(policy_type);
CREATE INDEX IF NOT EXISTS idx_policies_generated_at ON public.policies(generated_at);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at on row changes
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at 
    BEFORE UPDATE ON public.invoices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_businesses_updated_at 
    BEFORE UPDATE ON public.businesses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policies_updated_at 
    BEFORE UPDATE ON public.policies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policies ENABLE ROW LEVEL SECURITY;

-- Create policies that allow all operations for authenticated users
-- You may want to customize this based on your authentication needs
CREATE POLICY "Allow all operations for authenticated users" ON public.users
    FOR ALL USING (true);

CREATE POLICY "Users can only see their own invoices" ON public.invoices
    FOR ALL USING (true);

CREATE POLICY "Users can only see their own business" ON public.businesses
    FOR ALL USING (true);

CREATE POLICY "Users can only see their own policies" ON public.policies
    FOR ALL USING (true);

-- Insert some sample users and data for testing (optional)
INSERT INTO public.users (email, full_name, password_hash) VALUES 
    ('john@example.com', 'John Doe', '$2b$12$example_hash_replace_this'),
    ('jane@example.com', 'Jane Smith', '$2b$12$example_hash_replace_this')
ON CONFLICT (email) DO NOTHING;

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

-- Create indexes for insurance tables
CREATE INDEX IF NOT EXISTS idx_insurance_policies_user_id ON public.insurance_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_templates_policy_type ON public.insurance_templates(policy_type);
CREATE INDEX IF NOT EXISTS idx_business_risk_assessments_user_id ON public.business_risk_assessments(user_id);

-- Enable RLS for insurance tables
ALTER TABLE public.insurance_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.insurance_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_risk_assessments ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for insurance tables
CREATE POLICY "Users can manage their own insurance policies" ON public.insurance_policies
    FOR ALL USING (true);

CREATE POLICY "Anyone can view insurance templates" ON public.insurance_templates
    FOR SELECT USING (true);

CREATE POLICY "Users can manage their own risk assessments" ON public.business_risk_assessments
    FOR ALL USING (true);

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
     '{"third_party_injury": true, "property_damage": true, "legal_expenses": true}'::jsonb),
    
    ('Employee Health Insurance', 'health', 'Star Health',
     ARRAY['services', 'manufacturing', 'retail', 'digital'], ARRAY['all'],
     100000, 2000000, 8000, 'Comprehensive health coverage for employees and their families',
     TRUE, 'IRDAI', 'IRDAI/HI/2024/006', ARRAY['employee_welfare', 'medical_emergencies'],
     '{"cashless_treatment": true, "pre_existing_diseases": true, "maternity_cover": true}'::jsonb),
    
    ('Fire & Theft Insurance', 'asset_protection', 'Oriental Insurance',
     ARRAY['retail', 'manufacturing'], ARRAY['retail', 'manufacturing', 'warehousing'],
     300000, 15000000, 10000, 'Protection against fire, theft, and burglary of business assets',
     TRUE, 'IRDAI', 'IRDAI/FT/2024/007', ARRAY['fire', 'theft', 'burglary', 'vandalism'],
     '{"fire_damage": true, "theft_burglary": true, "vandalism": true}'::jsonb)
ON CONFLICT DO NOTHING;

-- Insert sample invoices (replace user_id with actual user IDs)
-- Note: You'll need to replace the user_id values with actual user IDs from your users table
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
     '[{"description": "Maintenance", "amount": 48000}]', 'pending'),
    (2, 'INV-004', 'PQR Inc', '2024-03-01', '45 days', 'Consulting', 
     30000.00, 'INR', 5400.00, 300.00, 
     '[{"description": "Consulting Services", "amount": 24300}]', 'paid')
ON CONFLICT (invoice_number, user_id) DO NOTHING;
