-- Phase 11: Align guardian_scarindex_history with locked ScarIndex schema
-- Adds created_at column (UTC) to preserve insertion chronology and match
-- core.contracts.scarindex expectations.

ALTER TABLE IF EXISTS public.guardian_scarindex_history
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();

COMMENT ON COLUMN public.guardian_scarindex_history.created_at IS
  'Insert time of the history record (Phase-11 determinism lock).';
