-- 1) Divergence Ledger: council_divergences

CREATE TABLE IF NOT EXISTS public.council_divergences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

    -- Core linkage
    claim_id UUID NOT NULL,
    witness_id TEXT NOT NULL,                   -- Discord user ID or mapped identity
    council_judgment_id UUID,                  -- Optional link to council_judgments if present

    -- Snapshots at time of divergence
    council_snapshot JSONB NOT NULL,           -- Full 7-mind council JSON
    aggregate_snapshot JSONB NOT NULL,         -- Aggregate block from council-router

    -- Verdicts
    council_recommended_verdict TEXT NOT NULL, -- e.g. 'verified' | 'rejected' | 'flagged'
    witness_verdict TEXT NOT NULL,             -- actual verdict from /witness
    divergence_type TEXT NOT NULL CHECK (
        divergence_type IN ('council_overruled', 'witness_overruled', 'aligned')
    ),

    -- Weights & confidence at that moment
    sovereign_confidence NUMERIC,              -- from aggregate.sovereign_confidence
    ache_weight NUMERIC,                       -- from aggregate.ache_weight (if available)

    -- Resolution info (filled later if we can evaluate outcome)
    resolved_outcome TEXT CHECK (
        resolved_outcome IN ('witness_correct', 'council_correct', 'uncertain')
    ),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,

    -- Meta
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- RLS: allow public read; writes handled via service key or backend functions
ALTER TABLE public.council_divergences ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "council_divergences_public_read" ON public.council_divergences;
CREATE POLICY "council_divergences_public_read"
ON public.council_divergences
FOR SELECT
USING (true);

DROP POLICY IF EXISTS "council_divergences_service_full" ON public.council_divergences;
CREATE POLICY "council_divergences_service_full"
ON public.council_divergences
USING (true)
WITH CHECK (true);

-- 2) Adaptation State: council_adaptation_state
--    Holds the current weights for each of the 7 roles.

CREATE TABLE IF NOT EXISTS public.council_adaptation_state (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

    profile_name TEXT NOT NULL UNIQUE DEFAULT 'default',

    judge_weight NUMERIC NOT NULL DEFAULT 1.0,
    weaver_weight NUMERIC NOT NULL DEFAULT 1.0,
    skeptic_weight NUMERIC NOT NULL DEFAULT 1.0,
    seer_weight NUMERIC NOT NULL DEFAULT 1.0,
    chronicler_weight NUMERIC NOT NULL DEFAULT 1.0,
    architect_weight NUMERIC NOT NULL DEFAULT 1.0,
    witness_weight NUMERIC NOT NULL DEFAULT 1.0,

    -- Aggregated stats snapshot used to compute current weights
    divergence_sample_window_days INTEGER NOT NULL DEFAULT 30,
    total_divergences INTEGER NOT NULL DEFAULT 0,
    witness_overrule_count INTEGER NOT NULL DEFAULT 0,
    council_overrule_count INTEGER NOT NULL DEFAULT 0,

    -- Per-role mismatch stats (for transparency and inertia)
    role_stats JSONB NOT NULL DEFAULT '{}'::jsonb,

    version INTEGER NOT NULL DEFAULT 1,
    last_recomputed_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

ALTER TABLE public.council_adaptation_state ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "council_adaptation_state_public_read" ON public.council_adaptation_state;
CREATE POLICY "council_adaptation_state_public_read"
ON public.council_adaptation_state
FOR SELECT
USING (true);

DROP POLICY IF EXISTS "council_adaptation_state_service_full" ON public.council_adaptation_state;
CREATE POLICY "council_adaptation_state_service_full"
ON public.council_adaptation_state
USING (true)
WITH CHECK (true);
