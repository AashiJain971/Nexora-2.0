-- Migration to fix currency column length
-- Run this in your Supabase SQL editor to update the existing table

ALTER TABLE public.invoices 
ALTER COLUMN currency TYPE VARCHAR(20);

-- Verify the change
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'invoices' 
AND column_name = 'currency';
