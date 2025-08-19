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
