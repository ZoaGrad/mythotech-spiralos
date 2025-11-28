-- Sequence J-D: Sequential Autopoiesis Path Migration

-- 1. Proposal Pattern Log (J1 learning corpus)
CREATE TABLE IF NOT EXISTS proposal_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES structural_change_requests(id),
    heuristic JSONB NOT NULL,
    tau_score FLOAT NOT NULL,
    complexity_delta FLOAT NOT NULL,
    coherence_delta FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Execution History (J2)
CREATE TABLE IF NOT EXISTS autopoiesis_execution_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation TEXT NOT NULL,
    payload JSONB NOT NULL,
    whitelist_key TEXT,
    coherence_delta FLOAT,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Full Autopoiesis Tables (J3)
CREATE TABLE IF NOT EXISTS autopoiesis_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal JSONB NOT NULL,
    decision TEXT NOT NULL,
    tau_score FLOAT NOT NULL,
    complexity_delta FLOAT NOT NULL,
    coherence_delta FLOAT NOT NULL,
    executed BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rollback_journal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID REFERENCES structural_change_requests(id),
    snapshot_before JSONB NOT NULL,
    snapshot_after JSONB,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teleology_weights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    weight_vector JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
