-- Migration: witness_entries
-- Description: Stores witness submissions and attestations.

CREATE TABLE IF NOT EXISTS witness_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    witness_id TEXT NOT NULL, -- UUID or address of the witness
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    attestation_hash TEXT UNIQUE, -- From AttestationManager.sol
    entry_data JSONB NOT NULL DEFAULT '{}'::jsonb, -- Content from submission form
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'attested', 'challenged'
    related_event_id UUID, -- FK to telemetry_events (to be added later)
    blockchain_tx_hash TEXT, -- On-chain transaction hash
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_witness_entries_witness_id ON witness_entries(witness_id);
CREATE INDEX IF NOT EXISTS idx_witness_entries_status ON witness_entries(status);
CREATE INDEX IF NOT EXISTS idx_witness_entries_attestation_hash ON witness_entries(attestation_hash);
CREATE INDEX IF NOT EXISTS idx_witness_entries_timestamp ON witness_entries(timestamp DESC);

-- RLS Policies
ALTER TABLE witness_entries ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON witness_entries
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: Can insert their own entries (assuming witness_id matches auth.uid, or just allow insert for now)
-- For now, we allow authenticated users to insert. We might refine this to check witness_id against auth.uid() later.
CREATE POLICY "Authenticated users can insert" ON witness_entries
    FOR INSERT TO authenticated
    WITH CHECK (true);

-- Authenticated Users: Can view all entries
CREATE POLICY "Authenticated users can view all" ON witness_entries
    FOR SELECT TO authenticated
    USING (true);

-- Anon: Read-only access (for public transparency)
CREATE POLICY "Public read access" ON witness_entries
    FOR SELECT TO anon
    USING (true);

-- Comments
COMMENT ON TABLE witness_entries IS 'Stores witness submissions and attestations for the SpiralOS governance.';
COMMENT ON COLUMN witness_entries.witness_id IS 'Identifier of the witness (UUID or address).';
COMMENT ON COLUMN witness_entries.attestation_hash IS 'Unique hash from the AttestationManager smart contract.';
COMMENT ON COLUMN witness_entries.entry_data IS 'JSON data containing the witness narrative and evidence.';
