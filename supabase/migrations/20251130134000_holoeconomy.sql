-- Migration: holoeconomy
-- Description: Defines tables for ScarCoin transactions and VaultNode registry.

-- ============================================================================
-- SCARCOIN TRANSACTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS scarcoin_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    token_type TEXT NOT NULL DEFAULT 'ScarCoin', -- 'ScarCoin', 'EMP'
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tx_hash TEXT UNIQUE, -- On-chain transaction hash
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_scarcoin_tx_from ON scarcoin_transactions(from_address);
CREATE INDEX IF NOT EXISTS idx_scarcoin_tx_to ON scarcoin_transactions(to_address);
CREATE INDEX IF NOT EXISTS idx_scarcoin_tx_timestamp ON scarcoin_transactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_scarcoin_tx_hash ON scarcoin_transactions(tx_hash);

-- RLS Policies
ALTER TABLE scarcoin_transactions ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON scarcoin_transactions
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: View all transactions (Public Ledger)
CREATE POLICY "Authenticated users can view all" ON scarcoin_transactions
    FOR SELECT TO authenticated
    USING (true);

-- Anon: View all transactions
CREATE POLICY "Public read access" ON scarcoin_transactions
    FOR SELECT TO anon
    USING (true);

-- ============================================================================
-- VAULTNODE REGISTRY
-- ============================================================================

CREATE TABLE IF NOT EXISTS vaultnode_registry (
    node_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_address TEXT NOT NULL,
    registration_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active', -- 'active', 'inactive', 'deprecated'
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_vaultnode_owner ON vaultnode_registry(owner_address);
CREATE INDEX IF NOT EXISTS idx_vaultnode_status ON vaultnode_registry(status);

-- RLS Policies
ALTER TABLE vaultnode_registry ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON vaultnode_registry
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: View all nodes
CREATE POLICY "Authenticated users can view all" ON vaultnode_registry
    FOR SELECT TO authenticated
    USING (true);

-- Anon: View all nodes
CREATE POLICY "Public read access" ON vaultnode_registry
    FOR SELECT TO anon
    USING (true);

-- Comments
COMMENT ON TABLE scarcoin_transactions IS 'Ledger of ScarCoin and EMP transactions.';
COMMENT ON TABLE vaultnode_registry IS 'Registry of VaultNodes in the SpiralOS network.';
