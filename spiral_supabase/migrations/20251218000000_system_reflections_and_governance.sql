-- Migration: 20251218000000_system_reflections_and_governance.sql
-- Description: Adds tables for the Night (Reflection) and Dawn (Governance) cycles.

-- 1. System Reflections Table
CREATE TABLE IF NOT EXISTS public.system_reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_date DATE NOT NULL DEFAULT CURRENT_DATE,
    divergence_count INTEGER NOT NULL DEFAULT 0,
    patterns JSONB NOT NULL DEFAULT '{}'::jsonb,
    proposed_adjustments JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);

-- RLS for system_reflections
ALTER TABLE public.system_reflections ENABLE ROW LEVEL SECURITY;

-- Allow public read access (transparency)
CREATE POLICY "Allow public read access on system_reflections"
ON public.system_reflections FOR SELECT
TO public
USING (true);

-- Allow service role full access
CREATE POLICY "Allow service role full access on system_reflections"
ON public.system_reflections FOR ALL
TO service_role
USING (true)
WITH CHECK (true);


-- 2. Governance Proposals Table
CREATE TABLE IF NOT EXISTS public.governance_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reflection_id UUID REFERENCES public.system_reflections(id) ON DELETE CASCADE,
    proposed_weights JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    resolved_at TIMESTAMPTZ
);

-- RLS for governance_proposals
ALTER TABLE public.governance_proposals ENABLE ROW LEVEL SECURITY;

-- Allow public read access (transparency)
CREATE POLICY "Allow public read access on governance_proposals"
ON public.governance_proposals FOR SELECT
TO public
USING (true);

-- Allow service role full access
CREATE POLICY "Allow service role full access on governance_proposals"
ON public.governance_proposals FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_system_reflections_cycle_date ON public.system_reflections(cycle_date);
CREATE INDEX IF NOT EXISTS idx_governance_proposals_status ON public.governance_proposals(status);
