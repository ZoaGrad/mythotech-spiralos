-- ΔΩ.12: External witness telemetry landing table
CREATE TABLE IF NOT EXISTS public.external_witness_events (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    witness_id text NOT NULL,
    source text NOT NULL,
    event_type text NOT NULL,
    payload jsonb NOT NULL,
    signature text,
    metadata jsonb DEFAULT '{}'::jsonb,
    trust_score numeric(4,3) NOT NULL DEFAULT 0.0,
    timestamp timestamptz NOT NULL DEFAULT timezone('utc', now()),
    ingested_at timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX IF NOT EXISTS idx_external_witness_events_timestamp
    ON public.external_witness_events (timestamp);
CREATE INDEX IF NOT EXISTS idx_external_witness_events_source
    ON public.external_witness_events (source);
