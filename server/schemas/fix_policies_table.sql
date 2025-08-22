-- Drop and recreate policies table to match the expected schema
DROP TABLE IF EXISTS public.policies CASCADE;

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

-- Create indexes for the policies table
CREATE INDEX IF NOT EXISTS idx_policies_user_id ON public.policies(user_id);
CREATE INDEX IF NOT EXISTS idx_policies_type ON public.policies(policy_type);
CREATE INDEX IF NOT EXISTS idx_policies_generated_at ON public.policies(generated_at);

-- Create trigger for policies table
CREATE TRIGGER update_policies_updated_at 
    BEFORE UPDATE ON public.policies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS for policies
ALTER TABLE public.policies ENABLE ROW LEVEL SECURITY;

-- Create policy for policies table
CREATE POLICY "Users can only see their own policies" ON public.policies
    FOR ALL USING (true);
