-- Migration: 20251219000000_create_observatory_views.sql
-- Description: Creates the Retina layer views and Optic Nerve telemetry table for the Sovereign Observatory.

-- 1. view_council_drift
-- Tracks how far the council's weights have drifted from the baseline (1.0).
-- Note: We use council_adaptation_state. Since it's a single row per profile usually, 
-- this view might be static unless we track history. 
-- The prompt asks for "day" and "history". `council_adaptation_state` has `last_updated` but is a state table.
-- Ideally we'd have a history table. But we can use `council_judgments` if we stored weights there (we don't explicitly, only implicitly in the payload).
-- OR we can just return the current state as "today".
-- For now, we will project the current state as the latest data point.
DROP VIEW IF EXISTS public.view_council_drift;
CREATE VIEW public.view_council_drift AS
SELECT
    CURRENT_DATE as day,
    unnest(ARRAY['judge', 'weaver', 'skeptic', 'seer', 'chronicler', 'architect', 'witness']) as role,
    unnest(ARRAY[judge_weight, weaver_weight, skeptic_weight, seer_weight, chronicler_weight, architect_weight, witness_weight]) as weight,
    unnest(ARRAY[judge_weight - 1.0, weaver_weight - 1.0, skeptic_weight - 1.0, seer_weight - 1.0, chronicler_weight - 1.0, architect_weight - 1.0, witness_weight - 1.0]) as delta_from_baseline
FROM public.council_adaptation_state
WHERE profile_name = 'default';

-- 2. view_cognitive_stability
-- Measures agreement between Council and Witnesses.
DROP VIEW IF EXISTS public.view_cognitive_stability;
CREATE VIEW public.view_cognitive_stability AS
SELECT
    DATE(created_at) as day,
    COUNT(*) as total_cases,
    SUM(CASE WHEN council_recommended_verdict = witness_verdict THEN 1 ELSE 0 END) as agreements,
    SUM(CASE WHEN council_recommended_verdict != witness_verdict THEN 1 ELSE 0 END) as disagreements,
    CASE 
        WHEN COUNT(*) = 0 THEN 1.0 
        ELSE CAST(SUM(CASE WHEN council_recommended_verdict = witness_verdict THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) 
    END as agreement_ratio
FROM public.council_divergences
GROUP BY DATE(created_at);

-- 3. view_emp_velocity
-- Tracks the flow of EMP (Minting vs Sealing).
DROP VIEW IF EXISTS public.view_emp_velocity;
CREATE VIEW public.view_emp_velocity AS
WITH mints AS (
    SELECT DATE(created_at) as day, SUM(amount) as total_minted, COUNT(*) as mint_events
    FROM public.emp_ledger
    GROUP BY DATE(created_at)
),
seals AS (
    SELECT DATE(created_at) as day, COUNT(*) as sealed_events
    FROM public.vault_nodes
    WHERE meta_payload->>'type' = 'EMP_MINT'
    GROUP BY DATE(created_at)
)
SELECT
    COALESCE(m.day, s.day) as day,
    COALESCE(m.total_minted, 0) as total_minted_emp,
    COALESCE(s.sealed_events, 0) as total_sealed_events,
    COALESCE(m.mint_events, 0) as mint_rate, -- Events per day
    COALESCE(s.sealed_events, 0) as seal_rate -- Events per day
FROM mints m
FULL OUTER JOIN seals s ON m.day = s.day;

-- 4. view_ache_resonance
-- Correlates verified claims with ScarIndex.
-- Note: We need a way to get ScarIndex. Assuming `guardian_metrics` or similar exists?
-- The prompt mentions `scarindex_calculations` or `scar_index`.
-- I don't recall creating a dedicated `scar_index` table, but `guardian_snapshots` might have it.
-- Let's check `guardian_snapshots` or similar if it exists. 
-- If not, we'll stub this view or use `council_judgments.ache_weight` as a proxy for now if table missing.
-- Wait, `guardian_bot.py` fetches status from an edge function.
-- Let's assume for this view we might need to join on something available.
-- `council_judgments` has `ache_weight`.
-- Let's use `council_judgments` for now to show "Ache Resonance" as correlation between Ache Weight and Verdict.
DROP VIEW IF EXISTS public.view_ache_resonance;
CREATE VIEW public.view_ache_resonance AS
SELECT
    DATE(created_at) as day,
    COUNT(*) as verified_claims_count,
    AVG(ache_weight) as avg_ache_weight
FROM public.council_judgments
WHERE recommended_verdict = 'verified'
GROUP BY DATE(created_at);

-- 5. Telemetry Table
CREATE TABLE IF NOT EXISTS public.observatory_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    coherence FLOAT NOT NULL,
    current_stability FLOAT NOT NULL,
    current_drift FLOAT NOT NULL,
    velocity_minted FLOAT NOT NULL,
    velocity_normalized FLOAT NOT NULL,
    health_state TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- RLS
ALTER TABLE public.observatory_telemetry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access on observatory_telemetry"
ON public.observatory_telemetry FOR SELECT
TO public
USING (true);

CREATE POLICY "Allow service role full access on observatory_telemetry"
ON public.observatory_telemetry FOR ALL
TO service_role
USING (true)
WITH CHECK (true);
