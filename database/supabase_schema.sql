-- ============================================
-- Supabase Database Schema for Fraud Detection System
-- ============================================
-- Run this script in your Supabase SQL Editor
-- Dashboard -> SQL Editor -> New Query -> Paste and Run
-- ============================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. TRANSACTIONS TABLE
-- ============================================
-- Stores all transaction predictions and details
CREATE TABLE IF NOT EXISTS transactions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Transaction Details
    amt FLOAT NOT NULL,
    category TEXT NOT NULL,
    merchant TEXT NOT NULL,
    state TEXT NOT NULL,
    customer_age INTEGER NOT NULL,
    
    -- Prediction Results
    fraud_probability FLOAT NOT NULL,
    fraud_prediction INTEGER NOT NULL CHECK (fraud_prediction IN (0, 1)),
    decision TEXT NOT NULL CHECK (decision IN ('ALLOW', 'REVIEW', 'BLOCK')),
    
    -- Additional Transaction Metadata (optional fields for advanced features)
    city_pop FLOAT,
    lat FLOAT,
    long FLOAT,
    merch_lat FLOAT,
    merch_long FLOAT,
    distance_km FLOAT,
    txn_time_gap FLOAT,
    txn_count_1h INTEGER,
    avg_amt_per_card FLOAT,
    amt_deviation FLOAT,
    txn_hour INTEGER CHECK (txn_hour >= 0 AND txn_hour <= 23),
    is_weekend INTEGER CHECK (is_weekend IN (0, 1)),
    gender TEXT CHECK (gender IN ('M', 'F')),
    cc_num TEXT
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_decision ON transactions(decision);
CREATE INDEX IF NOT EXISTS idx_transactions_fraud_prediction ON transactions(fraud_prediction);

-- ============================================
-- 2. FLAGGED TRANSACTIONS TABLE
-- ============================================
-- Stores high-risk transactions that need review or were blocked
CREATE TABLE IF NOT EXISTS flagged_transactions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign Key to transactions table
    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    
    -- Risk Classification
    risk_level TEXT NOT NULL CHECK (risk_level IN ('HIGH', 'CRITICAL')),
    
    -- Review Status
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewer_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_flagged_transactions_transaction_id ON flagged_transactions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_flagged_transactions_reviewed ON flagged_transactions(reviewed);
CREATE INDEX IF NOT EXISTS idx_flagged_transactions_risk_level ON flagged_transactions(risk_level);

-- ============================================
-- 3. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================
-- Enable RLS on both tables
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE flagged_transactions ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users to INSERT transactions (for logging from backend)
CREATE POLICY "Allow anonymous insert on transactions"
ON transactions
FOR INSERT
TO anon
WITH CHECK (true);

-- Allow anonymous users to SELECT transactions (for viewing history)
CREATE POLICY "Allow anonymous select on transactions"
ON transactions
FOR SELECT
TO anon
USING (true);

-- Allow anonymous users to INSERT flagged transactions
CREATE POLICY "Allow anonymous insert on flagged_transactions"
ON flagged_transactions
FOR INSERT
TO anon
WITH CHECK (true);

-- Allow anonymous users to SELECT flagged transactions
CREATE POLICY "Allow anonymous select on flagged_transactions"
ON flagged_transactions
FOR SELECT
TO anon
USING (true);

-- Allow anonymous users to UPDATE flagged transactions (for review status)
CREATE POLICY "Allow anonymous update on flagged_transactions"
ON flagged_transactions
FOR UPDATE
TO anon
USING (true)
WITH CHECK (true);

-- ============================================
-- 4. HELPFUL VIEWS (OPTIONAL)
-- ============================================

-- View to get fraud statistics
CREATE OR REPLACE VIEW fraud_statistics AS
SELECT 
    COUNT(*) as total_transactions,
    SUM(CASE WHEN fraud_prediction = 1 THEN 1 ELSE 0 END) as fraud_count,
    ROUND(
        (SUM(CASE WHEN fraud_prediction = 1 THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100), 
        2
    ) as fraud_rate_percent,
    SUM(CASE WHEN decision = 'ALLOW' THEN 1 ELSE 0 END) as allowed_count,
    SUM(CASE WHEN decision = 'REVIEW' THEN 1 ELSE 0 END) as review_count,
    SUM(CASE WHEN decision = 'BLOCK' THEN 1 ELSE 0 END) as blocked_count
FROM transactions;

-- View to get recent flagged transactions with details
CREATE OR REPLACE VIEW recent_flagged_transactions AS
SELECT 
    ft.id as flagged_id,
    ft.transaction_id,
    ft.risk_level,
    ft.reviewed,
    ft.created_at as flagged_at,
    t.amt,
    t.merchant,
    t.category,
    t.fraud_probability,
    t.decision
FROM flagged_transactions ft
JOIN transactions t ON ft.transaction_id = t.id
ORDER BY ft.created_at DESC;

-- ============================================
-- SETUP COMPLETE!
-- ============================================
-- You can now verify the setup by running:
-- SELECT * FROM transactions LIMIT 10;
-- SELECT * FROM flagged_transactions LIMIT 10;
-- SELECT * FROM fraud_statistics;
-- ============================================
