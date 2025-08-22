-- Fix policies table structure for Nexora Policy Generator
-- Run this SQL in the Supabase SQL Editor

-- Drop existing policies table and recreate with correct structure
DROP TABLE IF EXISTS policies CASCADE;

-- Create policies table with the correct columns that the backend expects
CREATE TABLE policies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    business_name TEXT NOT NULL,
    policy_type TEXT NOT NULL,
    content TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    compliance_regions TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for user access control
CREATE POLICY "Users can view their own policies" ON policies
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own policies" ON policies
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own policies" ON policies
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own policies" ON policies
    FOR DELETE USING (auth.uid() = user_id);

-- Create indexes for better performance
CREATE INDEX idx_policies_user_id ON policies(user_id);
CREATE INDEX idx_policies_type ON policies(policy_type);
CREATE INDEX idx_policies_generated_at ON policies(generated_at);

-- Verify the table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'policies' 
ORDER BY ordinal_position;
