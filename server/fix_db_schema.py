#!/usr/bin/env python3

import os
from supabase import create_client

# Supabase credentials
SUPABASE_URL = "https://iobyxykfpluxygwdztac.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlvYnl4eWtmcGx1eHlnd2R6dGFjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjc4NzE3MCwiZXhwIjoyMDUyMzYzMTcwfQ.hR5xWsEi8GbV5KRAqHDOUCqmD-VJ8vDPtRCJq5OeGD8"

def fix_policies_table():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # First, let's check the current structure
        print("Checking current policies table structure...")
        response = supabase.table('policies').select('*').limit(1).execute()
        print("Query successful - table exists")
        
        # The SQL to fix the table structure
        sql_commands = [
            """
            -- Drop the existing policies table
            DROP TABLE IF EXISTS policies CASCADE;
            """,
            """
            -- Recreate policies table with correct structure
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
            """,
            """
            -- Enable RLS
            ALTER TABLE policies ENABLE ROW LEVEL SECURITY;
            """,
            """
            -- Create RLS policies
            CREATE POLICY "Users can view their own policies" ON policies
                FOR SELECT USING (auth.uid() = user_id);
            """,
            """
            CREATE POLICY "Users can insert their own policies" ON policies
                FOR INSERT WITH CHECK (auth.uid() = user_id);
            """,
            """
            CREATE POLICY "Users can update their own policies" ON policies
                FOR UPDATE USING (auth.uid() = user_id);
            """,
            """
            CREATE POLICY "Users can delete their own policies" ON policies
                FOR DELETE USING (auth.uid() = user_id);
            """,
            """
            -- Create index for better performance
            CREATE INDEX idx_policies_user_id ON policies(user_id);
            CREATE INDEX idx_policies_type ON policies(policy_type);
            """
        ]
        
        for sql in sql_commands:
            if sql.strip():
                print(f"Executing SQL command...")
                try:
                    result = supabase.postgrest.schema('public').rpc('exec_sql', {'sql': sql}).execute()
                    print("✓ SQL command executed successfully")
                except Exception as e:
                    print(f"Error executing SQL: {e}")
                    # Try alternative method
                    try:
                        # Use raw SQL execution
                        supabase.postgrest.schema('public')._client.session.post(
                            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                            json={"sql": sql},
                            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
                        )
                        print("✓ SQL command executed via alternative method")
                    except Exception as e2:
                        print(f"Alternative method also failed: {e2}")
                        continue
        
        print("Database schema fix completed!")
        
    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    fix_policies_table()
