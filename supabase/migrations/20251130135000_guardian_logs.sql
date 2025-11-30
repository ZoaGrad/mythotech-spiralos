-- Migration: guardian_logs
-- Description: Logs actions taken by Guardian agents and bots.

CREATE TABLE IF NOT EXISTS guardian_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent_id TEXT NOT NULL, -- 'GuardianBot', 'DynamicAuditor'
    action TEXT NOT NULL, -- 'post_message', 'run_audit', 'sync_data'
    target TEXT, -- 'Discord', 'GitHub', 'Supabase_Table'
    result TEXT, -- 'success', 'failure'
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_guardian_logs_timestamp ON guardian_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_guardian_logs_agent ON guardian_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_guardian_logs_action ON guardian_logs(action);

-- RLS Policies
ALTER TABLE guardian_logs ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access" ON guardian_logs
    FOR ALL USING (auth.role() = 'service_role');

-- Authenticated Users: Read-only (Transparency)
CREATE POLICY "Authenticated users can view all" ON guardian_logs
    FOR SELECT TO authenticated
    USING (true);

-- Anon: Read-only
CREATE POLICY "Public read access" ON guardian_logs
    FOR SELECT TO anon
    USING (true);

-- Comments
COMMENT ON TABLE guardian_logs IS 'Audit log of all actions performed by Guardian agents.';
