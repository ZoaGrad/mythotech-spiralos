-- Migration: governance_protocol
-- Description: Establishes Three-Branch Governance tables.

-- ============================================================================
-- GOVERNANCE PROPOSALS
-- ============================================================================

CREATE TABLE IF NOT EXISTS governance_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    proposer_id TEXT NOT NULL, -- Discord ID or Wallet Address
    proposal_type TEXT NOT NULL, -- 'constitutional_amendment', 'parameter_change', 'judicial_review'
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'active', 'passed', 'rejected', 'executed'
    payload JSONB DEFAULT '{}'::jsonb, -- Structured data for the proposal (e.g., new weights)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    execution_result JSONB
);

CREATE INDEX IF NOT EXISTS idx_proposals_status ON governance_proposals(status);

-- ============================================================================
-- GOVERNANCE VOTES
-- ============================================================================

CREATE TABLE IF NOT EXISTS governance_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID REFERENCES governance_proposals(id),
    voter_id TEXT NOT NULL,
    vote_choice TEXT NOT NULL, -- 'yes', 'no', 'abstain'
    vote_power NUMERIC DEFAULT 1.0,
    reason TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_votes_proposal ON governance_votes(proposal_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_votes_unique ON governance_votes(proposal_id, voter_id);

-- ============================================================================
-- JUDICIAL ACTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS judicial_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_type TEXT NOT NULL, -- 'freeze_operations', 'force_rebalance', 'impeach_guardian'
    trigger_event_id UUID, -- Reference to a PanicFrame or Anomaly (stored as UUID, no strict FK to allow flexibility)
    executor_id TEXT NOT NULL, -- 'F2_Judge_Bot', 'System_Automator'
    justification TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'executed',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE governance_proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE governance_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE judicial_actions ENABLE ROW LEVEL SECURITY;

-- Service Role: Full Access
CREATE POLICY "Service role full access proposals" ON governance_proposals FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access votes" ON governance_votes FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access judicial" ON judicial_actions FOR ALL USING (auth.role() = 'service_role');

-- Public Read Access
CREATE POLICY "Public read proposals" ON governance_proposals FOR SELECT TO anon USING (true);
CREATE POLICY "Public read votes" ON governance_votes FOR SELECT TO anon USING (true);
CREATE POLICY "Public read judicial" ON judicial_actions FOR SELECT TO anon USING (true);

-- Authenticated Insert (for voting and proposing)
CREATE POLICY "Auth insert proposals" ON governance_proposals FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Auth insert votes" ON governance_votes FOR INSERT TO authenticated WITH CHECK (true);
