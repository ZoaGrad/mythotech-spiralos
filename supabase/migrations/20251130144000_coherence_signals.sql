-- Migration: coherence_signals
-- Description: Creates coherence_signals table.

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

COMMENT ON TABLE coherence_signals IS 'Processed coherence signals derived from telemetry.';
