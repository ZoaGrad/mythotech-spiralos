-- ΔΩ.12: External quarantine table for rejected witness telemetry
CREATE TABLE IF NOT EXISTS public.external_quarantine (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    reason text NOT NULL,
    detail text,
    raw_event jsonb NOT NULL,
    quarantined_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX IF NOT EXISTS idx_external_quarantine_reason
    ON public.external_quarantine (reason);
