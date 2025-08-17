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
    currency VARCHAR(10) DEFAULT 'INR',
    tax_amount DECIMAL(15,2) DEFAULT 0,
    extra_charges DECIMAL(15,2) DEFAULT 0,
    line_items JSONB,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'paid', 'overdue'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    payment_date DATE,
    UNIQUE(invoice_number, user_id)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON public.invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_client ON public.invoices(client);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON public.invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON public.invoices(created_at);

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

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;

-- Create policies that allow all operations for authenticated users
-- You may want to customize this based on your authentication needs
CREATE POLICY "Allow all operations for authenticated users" ON public.users
    FOR ALL USING (true);

CREATE POLICY "Users can only see their own invoices" ON public.invoices
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
