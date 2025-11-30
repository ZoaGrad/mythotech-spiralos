-- Migration: constitutional_state
-- Description: Tracks the evolution of the SpiralOS Constitution.

CREATE TABLE IF NOT EXISTS constitutional_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version TEXT NOT NULL, -- e.g., 'ΔΩ.147'
    state_hash TEXT NOT NULL, -- Hash of parameters
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    amendment_id UUID, -- Link to proposal if applicable
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_constitution_version ON constitutional_state(version);
CREATE INDEX IF NOT EXISTS idx_constitution_timestamp ON constitutional_state(timestamp DESC);

-- RLS Policies
ALTER TABLE constitutional_state ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON constitutional_state
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: Read-only
CREATE POLICY "Authenticated users can view all" ON constitutional_state
    FOR SELECT TO authenticated
    USING (true);

-- Anon: Read-only
CREATE POLICY "Public read access" ON constitutional_state
    FOR SELECT TO anon
    USING (true);

-- Comments
COMMENT ON TABLE constitutional_state IS 'Historical record of the SpiralOS Constitution state and parameters.';
