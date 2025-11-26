-- PHASE 1: SWPS STREAM Witness Protocol
-- Stream variant defaults: 3 witnesses, 24h window, no narratives, decaying ancestry edges

-- ENUMS
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'witness_mode') THEN
        CREATE TYPE witness_mode AS ENUM ('STREAM', 'CRUCIBLE', 'COUNCIL');
    END IF;
END$$;

-- CORE TABLES
CREATE TABLE IF NOT EXISTS public.witness_claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    initiator_id UUID,
    target_id UUID,
    mode witness_mode NOT NULL DEFAULT 'STREAM',
    payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    resonance NUMERIC NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','assessing','finalized','rejected')),
    required_witnesses INT NOT NULL DEFAULT 3,
    decay_rate NUMERIC NOT NULL DEFAULT 0.003,
    emp_multiplier NUMERIC NOT NULL DEFAULT 1.0,
    semantic_median NUMERIC,
    emotional_median NUMERIC,
    contextual_median NUMERIC,
    rho_sigma NUMERIC,
    emp_queued BOOLEAN DEFAULT FALSE,
    window_expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.witness_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES public.witness_claims(id) ON DELETE CASCADE,
    witness_id UUID NOT NULL,
    status TEXT NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned','submitted','expired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    UNIQUE (claim_id, witness_id)
);

CREATE TABLE IF NOT EXISTS public.witness_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES public.witness_claims(id) ON DELETE CASCADE,
    witness_id UUID NOT NULL,
    semantic NUMERIC NOT NULL,
    emotional NUMERIC NOT NULL,
    contextual NUMERIC NOT NULL,
    rho_sigma NUMERIC,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (claim_id, witness_id)
);

CREATE TABLE IF NOT EXISTS public.ancestry_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_claim UUID REFERENCES public.witness_claims(id) ON DELETE SET NULL,
    child_claim UUID NOT NULL REFERENCES public.witness_claims(id) ON DELETE CASCADE,
    weight NUMERIC NOT NULL DEFAULT 1,
    decay_rate NUMERIC NOT NULL DEFAULT 0.003,
    permanence BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- EMP LEDGER + QUEUE (soul-bound)
CREATE TABLE IF NOT EXISTS public.emp_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    claim_id UUID NOT NULL REFERENCES public.witness_claims(id) ON DELETE CASCADE,
    amount NUMERIC NOT NULL,
    rho_sigma NUMERIC,
    transferable BOOLEAN NOT NULL DEFAULT FALSE,
    origin_variant TEXT NOT NULL DEFAULT 'STREAM',
    minted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE TABLE IF NOT EXISTS public.emp_mint_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES public.witness_claims(id) ON DELETE CASCADE,
    user_id UUID,
    amount NUMERIC,
    rho_sigma NUMERIC,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','queued','minted','rejected')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::JSONB
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_witness_claims_mode ON public.witness_claims(mode);
CREATE INDEX IF NOT EXISTS idx_witness_claims_status ON public.witness_claims(status);
CREATE INDEX IF NOT EXISTS idx_witness_assessments_claim ON public.witness_assessments(claim_id);
CREATE INDEX IF NOT EXISTS idx_witness_assignments_claim ON public.witness_assignments(claim_id);
CREATE INDEX IF NOT EXISTS idx_ancestry_edges_parent ON public.ancestry_edges(parent_claim);
CREATE INDEX IF NOT EXISTS idx_emp_mint_queue_status ON public.emp_mint_queue(status);

-- VIEWS
CREATE OR REPLACE VIEW public.witness_reputation_view AS
SELECT
    wa.witness_id,
    COUNT(*) AS assessments,
    AVG(wa.semantic) AS semantic_avg,
    AVG(wa.emotional) AS emotional_avg,
    AVG(wa.contextual) AS contextual_avg,
    AVG(COALESCE(wa.rho_sigma, (wa.semantic + wa.emotional + wa.contextual) / 3)) AS rho_sigma_avg,
    MAX(wa.created_at) AS last_assessed_at
FROM public.witness_assessments wa
GROUP BY wa.witness_id;

CREATE OR REPLACE VIEW public.witness_stream_pending_view AS
SELECT
    wc.id AS claim_id,
    wc.initiator_id,
    wc.target_id,
    wc.payload,
    wc.status,
    wc.required_witnesses,
    wc.window_expires_at,
    COALESCE(ac.completed, 0) AS assessments_completed
FROM public.witness_claims wc
LEFT JOIN (
    SELECT claim_id, COUNT(*) AS completed FROM public.witness_assessments GROUP BY claim_id
) ac ON ac.claim_id = wc.id
WHERE wc.mode = 'STREAM' AND wc.status IN ('pending', 'assessing');

CREATE OR REPLACE VIEW public.witness_stream_complete_view AS
SELECT
    wc.id AS claim_id,
    wc.initiator_id,
    wc.target_id,
    wc.payload,
    wc.status,
    wc.semantic_median,
    wc.emotional_median,
    wc.contextual_median,
    wc.rho_sigma,
    wc.emp_queued,
    wc.updated_at
FROM public.witness_claims wc
WHERE wc.mode = 'STREAM' AND wc.status = 'finalized';
