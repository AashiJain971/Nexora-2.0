-- Create blockchain_loans table for storing loan requests and their status
CREATE TABLE IF NOT EXISTS blockchain_loans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount_eth DECIMAL(18, 8) NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(255) NOT NULL,
    wallet_address VARCHAR(42) NOT NULL,
    credit_score INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    blockchain_loan_id INTEGER,
    transaction_hash VARCHAR(66),
    approved BOOLEAN DEFAULT FALSE,
    disbursed BOOLEAN DEFAULT FALSE,
    repaid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by INTEGER,
    approval_tx_hash VARCHAR(66),
    disbursed_at TIMESTAMP,
    disbursement_tx_hash VARCHAR(66),
    repaid_at TIMESTAMP,
    repayment_tx_hash VARCHAR(66),
    
    -- Add foreign key constraint if users table exists
    -- FOREIGN KEY (user_id) REFERENCES users(id),
    -- FOREIGN KEY (approved_by) REFERENCES users(id),
    
    -- Add indexes for better query performance
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_blockchain_loan_id (blockchain_loan_id),
    INDEX idx_created_at (created_at)
);

-- Create policy_reminders table if it doesn't exist (mentioned in the API)
CREATE TABLE IF NOT EXISTS policy_reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    policy_id INTEGER,
    reminder_date DATE NOT NULL,
    reminder_type VARCHAR(50) DEFAULT 'renewal',
    message TEXT,
    sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_reminder_date (reminder_date),
    INDEX idx_policy_id (policy_id)
);

-- Create lender_deposits table for tracking lender deposits
CREATE TABLE IF NOT EXISTS lender_deposits (
    id SERIAL PRIMARY KEY,
    lender_address VARCHAR(42) NOT NULL,
    lender_name VARCHAR(255) NOT NULL,
    amount_eth DECIMAL(18, 8) NOT NULL,
    transaction_hash VARCHAR(66) NOT NULL UNIQUE,
    block_number INTEGER,
    status VARCHAR(50) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_lender_address (lender_address),
    INDEX idx_transaction_hash (transaction_hash),
    INDEX idx_created_at (created_at)
);

-- Create loan_events table for tracking all loan-related blockchain events
CREATE TABLE IF NOT EXISTS loan_events (
    id SERIAL PRIMARY KEY,
    loan_id INTEGER,
    event_type VARCHAR(50) NOT NULL, -- 'requested', 'approved', 'disbursed', 'repaid'
    transaction_hash VARCHAR(66) NOT NULL,
    block_number INTEGER,
    borrower_address VARCHAR(42),
    amount_eth DECIMAL(18, 8),
    credit_score INTEGER,
    gas_used INTEGER,
    event_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_loan_id (loan_id),
    INDEX idx_event_type (event_type),
    INDEX idx_transaction_hash (transaction_hash),
    INDEX idx_borrower_address (borrower_address)
);

-- Add some useful views for analytics
CREATE VIEW loan_statistics AS
SELECT 
    COUNT(*) as total_loans,
    SUM(amount_eth) as total_amount_requested,
    AVG(amount_eth) as average_loan_amount,
    AVG(credit_score) as average_credit_score,
    COUNT(CASE WHEN approved = TRUE THEN 1 END) as approved_loans,
    COUNT(CASE WHEN disbursed = TRUE THEN 1 END) as disbursed_loans,
    COUNT(CASE WHEN repaid = TRUE THEN 1 END) as repaid_loans,
    SUM(CASE WHEN approved = TRUE THEN amount_eth ELSE 0 END) as total_approved_amount,
    SUM(CASE WHEN disbursed = TRUE THEN amount_eth ELSE 0 END) as total_disbursed_amount
FROM blockchain_loans;

CREATE VIEW user_loan_summary AS
SELECT 
    user_id,
    COUNT(*) as total_loan_requests,
    SUM(amount_eth) as total_requested_amount,
    AVG(credit_score) as average_credit_score,
    COUNT(CASE WHEN approved = TRUE THEN 1 END) as approved_loans,
    COUNT(CASE WHEN disbursed = TRUE THEN 1 END) as active_loans,
    COUNT(CASE WHEN repaid = TRUE THEN 1 END) as repaid_loans,
    MAX(created_at) as last_request_date
FROM blockchain_loans
GROUP BY user_id;
