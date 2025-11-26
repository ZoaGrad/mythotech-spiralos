-- Migration: Restore Missing Tables & Schema Alignment
-- Sequence F Repair - Migration A

-- 1. Restore witness_claims
CREATE TABLE IF NOT EXISTS public.witness_claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    initiator_id UUID,
    target_id UUID,
    mode witness_mode NOT NULL DEFAULT 'STREAM',
    payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    resonance NUMERIC NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
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

-- 2. Restore witness_events
CREATE TABLE IF NOT EXISTS public.witness_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    initiator UUID,
    target UUID,
    mode witness_mode NOT NULL,
    payload JSONB NOT NULL,
    emp_stake NUMERIC NOT NULL DEFAULT 0,
    reputation_cost NUMERIC NOT NULL DEFAULT 0,
    resonance NUMERIC NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    required_witnesses INT NOT NULL DEFAULT 3,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Restore scarcoin_bridge
CREATE TABLE IF NOT EXISTS public.scarcoin_bridge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_address TEXT UNIQUE NOT NULL,
    user_id UUID,
    balance NUMERIC NOT NULL DEFAULT 0,
    total_minted NUMERIC NOT NULL DEFAULT 0,
    total_burned NUMERIC NOT NULL DEFAULT 0,
    transaction_count INT NOT NULL DEFAULT 0,
    last_transaction_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

-- 4. Restore vault_events
CREATE TABLE IF NOT EXISTS public.vault_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    neural_signature TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Rename witness_assessments to assessments
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'witness_assessments') THEN
        ALTER TABLE public.witness_assessments RENAME TO assessments;
    END IF;
END$$;

-- Ensure assessments table exists if rename didn't happen (e.g. fresh start)
CREATE TABLE IF NOT EXISTS public.assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID, -- For witness_events linkage
    claim_id UUID, -- For witness_claims linkage
    witness_id UUID NOT NULL,
    semantic NUMERIC,
    emotional NUMERIC,
    contextual NUMERIC,
    rho_sigma NUMERIC,
    verdict TEXT,
    notes TEXT,
    score NUMERIC DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (claim_id, witness_id),
    UNIQUE (event_id, witness_id)
);
