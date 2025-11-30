-- Migration: telemetry
-- Description: Defines tables for system telemetry and coherence signals.

-- ============================================================================
-- TELEMETRY EVENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS telemetry_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type TEXT NOT NULL, -- 'github_webhook', 'gateway_pulse', 'guardian_heartbeat'
    source TEXT NOT NULL, -- 'GitHub', 'Discord', 'PID_Controller'
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_type ON telemetry_events(event_type);
CREATE INDEX IF NOT EXISTS idx_telemetry_source ON telemetry_events(source);

-- RLS Policies
ALTER TABLE telemetry_events ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON telemetry_events
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: Read-only (Transparency)
CREATE POLICY "Authenticated users can view all" ON telemetry_events
    FOR SELECT TO authenticated
    USING (true);

-- Anon: Read-only
CREATE POLICY "Public read access" ON telemetry_events
    FOR SELECT TO anon
    USING (true);

-- ============================================================================
-- COHERENCE SIGNALS
-- ============================================================================

CREATE TABLE IF NOT EXISTS coherence_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telemetry_event_id UUID REFERENCES telemetry_events(id),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scarindex_value NUMERIC,
    panic_frame_triggered BOOLEAN DEFAULT FALSE,
    control_action_taken TEXT, -- 'PID_adjustment', 'alert_guardian'
    signal_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_coherence_timestamp ON coherence_signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_coherence_scarindex ON coherence_signals(scarindex_value);

-- RLS Policies
ALTER TABLE coherence_signals ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON coherence_signals
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: Read-only
CREATE POLICY "Authenticated users can view all" ON coherence_signals
    FOR SELECT TO authenticated
    USING (true);

-- Anon: Read-only
CREATE POLICY "Public read access" ON coherence_signals
    FOR SELECT TO anon
    USING (true);

-- ============================================================================
-- LINK WITNESS ENTRIES
-- ============================================================================

-- Add FK constraint to witness_entries now that telemetry_events exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'witness_entries') THEN
        ALTER TABLE witness_entries 
        ADD CONSTRAINT fk_witness_event 
        FOREIGN KEY (related_event_id) 
        REFERENCES telemetry_events(id);
    END IF;
END $$;

-- Comments
COMMENT ON TABLE telemetry_events IS 'Raw telemetry data ingested from various sources.';
COMMENT ON TABLE coherence_signals IS 'Processed coherence signals derived from telemetry.';
