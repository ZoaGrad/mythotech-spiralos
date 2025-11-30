-- Migration: holoeconomy_activation
-- Description: Adds tables for ScarCoin minting, Empathy Market, and Ache Values.

-- ============================================================================
-- SCARCOIN MINTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS scarcoin_mints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_address TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    ache_event_id UUID, -- Link to Ache Event that triggered mint
    scarindex_snapshot_id UUID, -- Link to ScarIndex at time of mint
    tx_hash TEXT UNIQUE, -- On-chain transaction hash
    minted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_scarcoin_mints_recipient ON scarcoin_mints(recipient_address);
CREATE INDEX IF NOT EXISTS idx_scarcoin_mints_ache ON scarcoin_mints(ache_event_id);

-- RLS Policies
ALTER TABLE scarcoin_mints ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON scarcoin_mints
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: View all mints
CREATE POLICY "Authenticated users can view all" ON scarcoin_mints
    FOR SELECT TO authenticated
    USING (true);

-- Anon: View all mints
CREATE POLICY "Public read access" ON scarcoin_mints
    FOR SELECT TO anon
    USING (true);

-- ============================================================================
-- EMPATHY MARKET TRANSACTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS empathy_market_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_id UUID REFERENCES auth.users(id),
    seller_id UUID REFERENCES auth.users(id),
    listing_id UUID, -- Placeholder for future listings table
    amount NUMERIC NOT NULL,
    currency TEXT NOT NULL DEFAULT 'ScarCoin',
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_empathy_tx_buyer ON empathy_market_transactions(buyer_id);
CREATE INDEX IF NOT EXISTS idx_empathy_tx_seller ON empathy_market_transactions(seller_id);

-- RLS Policies
ALTER TABLE empathy_market_transactions ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON empathy_market_transactions
    FOR ALL USING (auth.role() = 'service_role');

-- Users can see their own transactions
CREATE POLICY "Users can view own transactions" ON empathy_market_transactions
    FOR SELECT TO authenticated
    USING (auth.uid() = buyer_id OR auth.uid() = seller_id);

-- ============================================================================
-- ACHE VALUES
-- ============================================================================

CREATE TABLE IF NOT EXISTS ache_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    value NUMERIC NOT NULL, -- Normalized Ache value (0.0 - 1.0)
    scarindex_snapshot_id UUID, -- Link to ScarIndex context
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ache_values_timestamp ON ache_values(timestamp DESC);

-- RLS Policies
ALTER TABLE ache_values ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON ache_values
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: View all
CREATE POLICY "Authenticated users can view all" ON ache_values
    FOR SELECT TO authenticated
    USING (true);

-- Comments
COMMENT ON TABLE scarcoin_mints IS 'Record of ScarCoin minting events triggered by Ache transmutation.';
COMMENT ON TABLE empathy_market_transactions IS 'Transactions in the P2P Empathy Market.';
COMMENT ON TABLE ache_values IS 'TimeSeries data of raw Ache values for economic correlation.';
