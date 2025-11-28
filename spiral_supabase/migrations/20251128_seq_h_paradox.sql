-- Sequence H: The Paradox Layer Migration

-- 1. Paradox Events: detection log
CREATE TABLE IF NOT EXISTS paradox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paradox_kind TEXT NOT NULL,
    entity_a_type TEXT NOT NULL,
    entity_a_id UUID NOT NULL,
    entity_b_type TEXT NOT NULL,
    entity_b_id UUID NOT NULL,
    severity FLOAT NOT NULL CHECK (severity >= 0.0 AND severity <= 1.0),
    strategy TEXT, -- reconcile / prioritize / purge (may be NULL until decided)
    status TEXT NOT NULL DEFAULT 'open', -- open / resolved / ignored
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_paradox_events_status
    ON paradox_events (status);

CREATE INDEX IF NOT EXISTS idx_paradox_events_kind
    ON paradox_events (paradox_kind);


-- 2. Paradox Resolutions: outcome log
CREATE TABLE IF NOT EXISTS paradox_resolutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paradox_event_id UUID NOT NULL REFERENCES paradox_events(id) ON DELETE CASCADE,
    strategy TEXT NOT NULL, -- reconcile / prioritize / purge
    before_state JSONB NOT NULL,
    after_state JSONB NOT NULL,
    coherence_before FLOAT,
    coherence_after FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_paradox_resolutions_event
    ON paradox_resolutions (paradox_event_id);


-- 3. Optional: Governance/Proposal Flags (non-breaking)
-- We use DO block to avoid errors if columns already exist (idempotency)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'governance_proposals' AND column_name = 'consistency_score') THEN
        ALTER TABLE governance_proposals ADD COLUMN consistency_score FLOAT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'governance_proposals' AND column_name = 'paradox_flag') THEN
        ALTER TABLE governance_proposals ADD COLUMN paradox_flag BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_governance_proposals_paradox_flag
    ON governance_proposals (paradox_flag);
